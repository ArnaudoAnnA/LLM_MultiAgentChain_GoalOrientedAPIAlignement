from nltk.corpus import stopwords
from transformers import AutoTokenizer, AutoModel
import torch
import matplotlib.pyplot as plt
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
from sklearn.metrics import auc
import numpy as np
from scipy.optimize import linear_sum_assignment
from difflib import SequenceMatcher

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')


# Sentence encoders selectable with GoalEvaluator(encoder=...), each pinned to a model revision.
# "prompt" is prepended to every text.
ENCODERS = {
    "minilm": {"model_id": "sentence-transformers/all-MiniLM-L6-v2",
               "revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"},
    "mpnet": {"model_id": "sentence-transformers/all-mpnet-base-v2",
              "revision": "e8c3b32edf5434bc2275fc9bab85f82640a19130"},
    "sbert_nli": {"model_id": "sentence-transformers/bert-base-nli-mean-tokens",
                  "revision": "160a52b38a51ae87295ec3eabcf11755e5d27a8d"},
    "sbert_stsb": {"model_id": "sentence-transformers/bert-base-nli-stsb-mean-tokens",
                   "revision": "c1e99553cc170c78b16717e93e8042552f5bef20"},
}

# Ramp points per encoder and node, as (low, high) cosines: a matched pair earns no credit
# below low, full credit from high upwards and a linear share in between.
RAMPS = {
    "minilm": {"actors": (0.6969, 0.7626), "highLevelGoals": (0.3941, 0.6241), "lowLevelGoals": (0.4334, 0.6241)},
}

# How many generated items one reference may give credit to, per node, when the ramp is used.
MAX_PER_REF = {"actors": 1, "highLevelGoals": 2, "lowLevelGoals": 2}

# Relative discount on every further copy of a reference offered to the matching. It only has
# to order assignments of equal total credit, so it stays far below any real credit difference.
SLOT_DISCOUNT = 1e-9


class SentenceEncoder:
    """Unit-norm sentence embeddings with a per-text cache. The model is loaded on first use."""

    def __init__(self, name, device=None, batch_size=32):
        if name not in ENCODERS:
            raise KeyError(f"Unknown encoder '{name}'. Available: {sorted(ENCODERS)}")
        self.name = name
        self.spec = ENCODERS[name]
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = batch_size
        self.model = None
        self.cache = {}

    def _load(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(self.spec["model_id"], revision=self.spec["revision"], device=self.device)

    def encode_uncached(self, texts):
        if self.model is None:
            self._load()
        emb = self.model.encode(list(texts), prompt=self.spec.get("prompt"), batch_size=self.batch_size,
                                normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
        return emb.astype(np.float32)

    def encode(self, texts):
        missing = [t for t in dict.fromkeys(texts) if t not in self.cache]
        if missing:
            for text, vec in zip(missing, self.encode_uncached(missing)):
                self.cache[text] = vec
        return np.stack([self.cache[t] for t in texts])

    def release(self):
        """Drop the model and keep the cache, to free memory for the next encoder."""
        self.model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class GoalEvaluator:
    def __init__(self, model_name="bert-base-uncased", preprocess=True, encoder=None, ramp=None, max_per_ref=1):
        """With encoder=None the texts are embedded by mean-pooling model_name, optionally after
        preprocessing. With an ENCODERS name they go to that sentence encoder, never preprocessed.

        ramp is an optional (low, high) pair of cosines: when given, the credit of a pair is 0
        below low, 1 from high upwards and linear in between, and the pairs are matched on that
        credit. With ramp=None the credit is the cosine itself.

        max_per_ref is how many generated items one reference may give credit to. A generated
        item is always matched to one reference at most. Precision sums the credit of every
        matched item; recall counts each reference once, with the best credit among its items.
        Among matchings with the same total credit, the one with the highest recall is taken."""
        if ramp is not None and not ramp[0] < ramp[1]:
            raise ValueError(f"ramp needs low < high, got {ramp}")
        if max_per_ref < 1:
            raise ValueError(f"max_per_ref needs to be at least 1, got {max_per_ref}")
        self.ramp = ramp
        self.max_per_ref = max_per_ref
        self.summary = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sentence_encoder = SentenceEncoder(encoder) if encoder else None
        if self.sentence_encoder:
            self.preprocess = False
            return
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.preprocess = preprocess
        if preprocess:
            self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text):
        tokens = word_tokenize(text)
        filtered_tokens = [t for t in tokens if t not in self.stop_words and t.isalnum()]
        stemmed_tokens = [self.stemmer.stem(token) for token in filtered_tokens]
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in stemmed_tokens]
        return " ".join(lemmatized_tokens)

    def encode_texts(self, texts):
        if self.sentence_encoder:
            return torch.from_numpy(self.sentence_encoder.encode(texts)).to(self.device)

        if self.preprocess:
            texts = [self.preprocess_text(text) for text in texts]

        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(self.device)

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Mean Pooling
        token_embeddings = model_output.last_hidden_state
        attention_mask = encoded_input['attention_mask']
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def compute_similarity(self, generated_goals, reference_goals):
        gen_embeddings = self.encode_texts(generated_goals)
        ref_embeddings = self.encode_texts(reference_goals)

        # Cosine similarity matrix
        gen_norm = torch.nn.functional.normalize(gen_embeddings, p=2, dim=1)
        ref_norm = torch.nn.functional.normalize(ref_embeddings, p=2, dim=1)
        sim_matrix = torch.mm(gen_norm, ref_norm.transpose(0, 1))

        return sim_matrix.cpu().numpy()

    @staticmethod
    def string_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def calculate_soft_f1(self, preds, refs):
        if not preds or not refs:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "similarities": np.zeros((len(preds), len(refs))),
                "rate_table": [{"threshold": tau, "precision": 0.0, "recall": 0.0} for tau in np.linspace(0, 1, 101)]
            }

        sim_matrix = self.compute_similarity(preds, refs)

        credit = sim_matrix
        if self.ramp is not None:
            low, high = self.ramp
            credit = np.clip((sim_matrix - low) / (high - low), 0.0, 1.0)

        # Matching on the credit, not on the cosine: a pair worth nothing must not hold a slot.
        # A reference that may pay several items is the same column offered several times.
        # Each further copy is worth a hair less: among assignments with the same total credit
        # the solver then spreads the items over more references, so the scores do not depend
        # on the order of the lists. Double precision keeps the discount from rounding away.
        offered = np.hstack([credit.astype(np.float64) * (1 - k * SLOT_DISCOUNT)
                             for k in range(self.max_per_ref)])
        row_ind, col_ind = linear_sum_assignment(-offered)
        col_ind = col_ind % len(refs)
        matched_credit = credit[row_ind, col_ind]

        # A cosine can be negative: a reference keeps the credit of its best item as it is.
        covered = np.full(len(refs), -np.inf)
        np.maximum.at(covered, col_ind, matched_credit)
        covered[np.isinf(covered)] = 0.0

        precision = matched_credit.sum() / len(preds)
        recall = covered.sum() / len(refs)

        f1 = 0 if precision + recall == 0 else 2 * (precision * recall) / (precision + recall)

        rate_table = []
        optimized_similarities = sim_matrix[row_ind, col_ind]
        best_similarities = np.full(len(refs), -np.inf)
        np.maximum.at(best_similarities, col_ind, optimized_similarities)
        for tau in np.linspace(0, 1, 101):
            p = np.sum(optimized_similarities >= tau) / len(preds)
            r = np.sum(best_similarities >= tau) / len(refs)
            rate_table.append({"threshold": tau, "precision": p, "recall": r})

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "similarities": sim_matrix,
            "rate_table": rate_table
        }

    def print_prec_rec_curve(self, generated_goals_dict: dict[str, list[str]],
                             reference_goals_dict: dict[str, list[str]], hide_prec_rec=False,
                             save_to_file=False, output_file="output.txt", threshold=0.9, rate_table=False):

        with open(output_file, "w") as f:
            f.write("dataset name; recall; precision; f1_score;\n")

        weighted_recalls = np.array([0.0] * 101)
        weighted_precisions = np.array([0.0] * 101)

        weighted_r = 0
        weighted_p = 0

        for dataset_name, generated_goals in generated_goals_dict.items():
            weight = len(reference_goals_dict[dataset_name])
            reference_goals = reference_goals_dict[dataset_name]
            results = self.calculate_soft_f1(generated_goals, reference_goals)

            weighted_p += (results["precision"] * weight)
            weighted_r += (results["recall"] * weight)

            summary_str = f"{dataset_name}; {results['recall']}; {results['precision']}; {results['f1_score']};"
            self.summary.append(summary_str)

            if save_to_file:
                with open(output_file, "a") as f:
                    f.write(summary_str + "\n")

            if rate_table:
                recalls = np.array([point['recall'] for point in results["rate_table"]])
                precisions = np.array([point['precision'] for point in results["rate_table"]])
                weighted_recalls += (recalls * weight)
                weighted_precisions += (precisions * weight)

        normalization_term = 1 / (sum([len(l) for l in reference_goals_dict.values()]))

        if rate_table:
            weighted_recalls *= normalization_term
            weighted_precisions *= normalization_term

        weighted_r *= normalization_term
        weighted_p *= normalization_term
        weighted_f1 = 2 * weighted_p * weighted_r / (weighted_p + weighted_r) if weighted_r + weighted_p else 0
        summary_str = f"Precision: {weighted_p}; Recall: {weighted_r}; F1-score: {weighted_f1};"

        if save_to_file:
            with open(output_file, "a") as f:
                f.write("Weighted averages; "+ summary_str + "\n")

        auc_prec_rec = auc(weighted_recalls[::-1], weighted_precisions[::-1])

        if not hide_prec_rec:
            plt.figure(figsize=(8, 6))
            plt.plot(weighted_recalls, weighted_precisions, marker='o', linestyle='-', color='b',
                     label="Precision-Recall Curve")
            plt.xlabel("Recall")
            plt.ylabel("Precision")
            plt.title("Precision-Recall Curve")
            plt.legend()
            plt.grid()
            plt.show()

        return auc_prec_rec, summary_str

    def print_best_f1(self, generated_goals_dict: dict[str, list[str]], reference_goals_dict: dict[str, list[str]],
                      save_to_file=False, output_file="output.txt", ):

        best_f1 = 0
        best_summary = ""

        for th in range(1, 101):
            _, summary_str, p, r, f1 = self.print_prec_rec_curve(generated_goals_dict, reference_goals_dict,
                                                                 threshold=th, hide_prec_rec=True)

            if f1 > best_f1:
                best_f1 = f1
                best_summary = summary_str

        print(best_summary)
        return best_summary