**Data:** 2026-10-14

**Breve descrizione:** guida rapida al codice aggiornato rispetto alla versione originale del repository: cosa è cambiato, a cosa serve ogni file e come eseguire il notebook.

# Indice del codice aggiornato

## 1. Cosa è cambiato rispetto alla versione originale

| Prima | Ora |
|---|---|
| Generatore OpenAI (`gpt-4o-mini`) | Generatore Gemini (`gemini-2.5-flash`), `temperature=0`, thinking spento |
| Critico Llama su Groq | Critico `qwen/qwen3.8-27b` su Groq (il modello originale non è più nel catalogo) |
| Chiavi in chiaro in `src/data_key/key.py` | Chiavi in `.env`, lette da `src/data_key/api_keys.py` (round-robin tra più chiavi) |
| Ground truth a pochi sistemi | Ground truth finale a **12 sistemi**, con la `description` inclusa: nessun README da scaricare |
| Tutti i sistemi sempre | Insiemi di sistemi selezionabili: `all` (12), `dev` (4), `holdout` (8) |
| Un solo output per run | Una cartella per run in `artifacts/results/<RUN_LABEL>/`, con log, CSV e registro cumulativo |

Invariati: `src/data_model.py`, `src/mapping/APIs_mapping.py`, `src/examples/shot_learning.py`.

`src/evaluation/goal_evaluator.py` calcola per default la metrica originale, quindi il notebook produce gli stessi punteggi di prima. La metrica nuova della fase 3 si attiva con i parametri `encoder`, `ramp` e `max_per_ref`.

## 2. A cosa serve ogni file

| File | Ruolo |
|---|---|
| `notebook/experiments.ipynb` | Lancia la matrice sperimentale (sistemi × shot mode × critico acceso/spento), valuta e riepiloga |
| `notebook/groundtruth.py` | Ground truth dei 12 sistemi: attori, High-Level Goals, Low-Level Goals e description. Generato dal workbook di validazione: non si modifica a mano |
| `notebook/system_sets.py` | Definisce `all`, `dev`, `holdout` e `resolve_systems()`; un nome sbagliato solleva errore invece di essere ignorato |
| `src/llm_clients.py` | Chiamate ai modelli: generatore Gemini e critico Groq, con rotazione delle chiavi sui limiti di richieste. La funzione del critico si chiama ancora `generate_response_llama` per ragioni storiche |
| `src/data_key/api_keys.py` | Legge le chiavi da `.env` (`<PREFISSO>_1`, `_2`, ...) |
| `src/extraction/extractor.py` | Genera description, attori, HLG e LLG; può leggere il README da uno snapshot locale |
| `src/self_critique/refine_response.py` | Ciclo generatore–critico: soglia 8,5/10, massimo 3 tentativi. Restituisce `(risultato, score, critica, tentativi, storico_score)` |
| `src/utils.py` | Lettura del README (rete o snapshot HTML locale) |
| `src/evaluation/goal_evaluator.py` | Precision, recall e F1 per attori, HLG e LLG. Di default con embedding BERT (metrica originale); con `encoder`, `ramp` e `max_per_ref` la metrica nuova |
| `.env.example` | Modello delle variabili da impostare. Il file `.env` vero non va mai committato |
| `requirements.txt` | Dipendenze, con le versioni nuove fissate |

## 3. Come eseguire il notebook

**Preparazione (una volta)**

1. `pip install -r requirements.txt` (Python 3.12 testato).
2. `cp .env.example .env` e inserire almeno una chiave Gemini (`GOOGLE_API_KEY_1`) e una Groq (`GROQ_API_KEY_1`). Per usare più chiavi in rotazione, aggiungere `_2`, `_3`, ... senza saltare numeri.
3. Aprire `notebook/experiments.ipynb` con la cartella `notebook/` come directory di lavoro: i percorsi sono relativi (`../src`, `../artifacts`).

Al primo avvio la valutazione scarica i dati NLTK e il modello BERT: serve la rete, la GPU è facoltativa.

**Configurazione (prima cella)**

| Variabile | Cosa decide |
|---|---|
| `RUN_LABEL` e `REPLICA` | Nome della run e numero di replica, da tenere allineati (es. `exp_01_baseline_r1` e `1`). Determinano la cartella di output |
| `SELECTED_SYSTEMS` | `"all"`, `"dev"`, `"holdout"` oppure una lista di nomi di sistema |
| `EXPERIMENT_PROMPT_MODES` | Shot mode: `ZERO_SHOT`, `ONE_SHOT`, `FEW_SHOT` |
| `EXPERIMENT_ABLATION_MODES` | `True` = critico spento, `False` = critico acceso. `[True, False]` esegue entrambi |
| `MAX_PARALLEL_RUNS` | Quanti sistemi girano in parallelo (default 4) |

La matrice intera (12 sistemi × 3 shot mode × 2 bracci) sono 72 celle, ognuna con chiamate reali ai modelli.

**Ordine delle celle**

| Cella | Cosa fa |
|---|---|
| 1 | Configurazione |
| 2 | Logging (`experiment_log.txt` e `verbose_log.txt` nella cartella di output) |
| 4 | Esecuzione: genera attori, HLG e LLG per ogni cella e salva un JSON per sistema |
| 6 | Valutazione: precision, recall e F1 pesati, un CSV per tipo di lista e configurazione |
| 8 | Tabella riepilogativa |
| 10 | Registro cumulativo `<RUN_LABEL>_registry.csv`, con modello generatore e critico |
| 11 | Chiude i log e ripristina lo stdout (a fine sessione) |

**Cosa si ottiene** in `artifacts/results/<RUN_LABEL>/`:

```
<Sistema>/<Sistema>_<SHOT>[_noLlama].json   # output per sistema; _noLlama = critico spento
actor_<SHOT>[_noLlama].csv   hl_...csv   ll_...csv   # punteggi per tipo di lista
<RUN_LABEL>_registry.csv                    # riepilogo con modelli usati
experiment_log.txt   verbose_log.txt
```

**Da sapere**

- Se un JSON esiste già, la cella 4 lo salta. Per rifare una cella si cancella il file corrispondente.
- A `temperature=0` il generatore non è deterministico su tutti i sistemi: per questo si fanno più repliche.
- `GENERATOR_SEED` è un'indicazione al provider, non una garanzia di riproducibilità.
- Alcuni commenti nel codice citano file e cartelle del progetto di origine (log, piani, snapshot) che non sono in questo repository: non servono per l'esecuzione.

## 4. Struttura del repository per i risultati

Il codice sta in `src/` e `notebook/`. Ogni fase di lavoro ha una cartella in `docs/`, con lo stesso schema:

```
docs/fase_<N>_<nome>/
├── FASE_<N>.md          indice: cosa contiene, a cosa serve ogni script, come rifare i numeri
├── REPORT_FASE_<N>.md   report: perché, a quale domanda rispondeva ogni esperimento, risposta
├── *.html               riepiloghi e spiegazioni illustrate
└── experiments/<esperimento>/<run>/   dati e tabelle prodotti
```

| Fase | Cartella | Contenuto |
|---|---|---|
| 2 — Il rumore | [`docs/fase_2_rumore/`](docs/fase_2_rumore/FASE_2.md) | Tre repliche della baseline, misura del rumore, scelta della regola di confronto. Report: [`REPORT_FASE_2.md`](docs/fase_2_rumore/REPORT_FASE_2.md) |
| 3 — La metrica | [`docs/fase_3_metrica/`](docs/fase_3_metrica/FASE_3.md) | Difetti misurati della metrica originale, metrica nuova (modello di frasi, credito a rampa, al massimo due goal per riferimento), accordo con un giudice umano e costi. Script di studio in `src/evaluation/phase-3-metric/` |
