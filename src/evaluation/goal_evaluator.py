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


class GoalEvaluator:
    def __init__(self, model_name="bert-base-uncased", preprocess=True):
        self.summary = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
            return 0.0

        sim_matrix = self.compute_similarity(preds, refs)

        row_ind, col_ind = linear_sum_assignment(-sim_matrix)
        total_similarity = sim_matrix[row_ind, col_ind].sum()

        precision = total_similarity / len(preds)
        recall = total_similarity / len(refs)

        f1 = 0 if precision + recall == 0 else 2 * (precision * recall) / (precision + recall)

        rate_table = []
        optimized_similarities = sim_matrix[row_ind, col_ind]
        for tau in np.linspace(0, 1, 101):
            tp = np.sum(optimized_similarities >= tau)
            p = tp / len(preds) if len(preds) > 0 else 0
            r = tp / len(refs) if len(refs) > 0 else 0
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

        with open(output_file, "a") as f:
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

        return auc_prec_rec, summary_str, weighted_p, weighted_r, weighted_f1

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