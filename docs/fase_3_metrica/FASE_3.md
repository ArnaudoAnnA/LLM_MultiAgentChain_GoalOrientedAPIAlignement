**Data:** 2026-10-14

**Breve descrizione:** indice dei file della fase 3 (la metrica di valutazione): cosa contiene ogni file, a cosa serve ogni script, quali esperimenti sono stati eseguiti, cosa non è incluso in questo repository e come rifare i numeri che si possono rifare.

# Fase 3 — La metrica

## La domanda

Il punteggio con cui si confrontano due liste di goal (F1 «soft» sulla similarità fra frasi) è d'accordo con un giudizio umano su «questi due goal sono lo stesso goal»? Dove non lo è, quale correzione lo avvicina?

La fase ha prodotto due cose: la misura dei difetti della metrica del lavoro di partenza e una metrica nuova (modello `all-MiniLM-L6-v2`, credito a rampa, al massimo due goal generati per riferimento sui goal), già implementata in `goal_evaluator.py` e applicabile alle liste salvate con `rescore.py`.

## Cosa contiene questa cartella

```
docs/fase_3_metrica/
├── FASE_3.md                      questo indice
├── REPORT_FASE_3.md               report degli esperimenti: perché, domanda, risposta
├── metrica-riepilogo-fase.html    riepilogo illustrato della fase
├── metrica-spiegazione.html       spiegazione illustrata di prove ed esiti
└── metrica-grafo-bipartito.md     come funziona l'abbinamento e quali problemi ha, con la diagnosi misurata
```

**Da dove partire:** `REPORT_FASE_3.md` per le risposte; `metrica-riepilogo-fase.html` per una lettura illustrata.

**Non incluso in questo repository:** il banco di coppie giudicate, il campione dei goal a credito zero e le tabelle intermedie degli esperimenti (confronto di modelli, forme del credito, abbinamenti, accordo col giudice). Gli script che le producono sono qui, ma non si possono rilanciare senza quei dati: vedi «Come rifare i numeri».

## Cosa è stato fatto

| Passo | Cosa | Script |
|---|---|---|
| Diagnosi | Proprietà della metrica di partenza sui 12 sistemi: voto a vuoto, effetto delle lunghezze, vincolo uno a uno, aggregazione | `src/diagnostics/metric_diagnostics.py` |
| Lunghezze | Ripunteggio delle 648 liste con goal generati, goal di riferimento e tetto accanto a ogni voto | `rescore.py` |
| Modello | Sei modelli candidati più due Sentence-BERT originali; regola di scelta scritta prima | `metric_diagnostics.py` |
| Banco di coppie | 210 coppie (goal generato, goal di riferimento) con etichetta `equivalente`, `parziale`, `diverso` | `pair_bench.py` |
| Soglia o rampa | Tre forme del credito a confronto con quattro prove | `credit_forms.py` |
| Abbinamento | Censimento dei goal a credito zero, campione giudicato, tabella di 12 combinazioni modello × credito × abbinamento, spareggio | `matching_forms.py` |
| Conferma | Accordo col giudice sul banco; rumore e regola di confronto ricalcolati con la metrica nuova | `bench_agreement.py`, `rescore.py`, `replica_noise.py` |

## Il codice

Si lanciano dalla radice del repository. Nessuno chiama modelli via API. Gli script di studio stanno in `src/evaluation/phase-3-metric/`; la metrica e gli strumenti riutilizzabili in `src/evaluation/`.

| Script | Perché esiste | Legge | Scrive |
|---|---|---|---|
| `src/evaluation/goal_evaluator.py` | Calcola precision, recall e F1 di una lista generata contro quella di riferimento. Senza parametri è la metrica del lavoro di partenza, chiamata dal notebook. Con `encoder=` usa un modello di frasi di `ENCODERS` (revisione fissata, nessun preprocessing). Con `ramp=(basso, alto)` il credito è 0 sotto il punto basso, 1 sopra il punto alto, lineare in mezzo; con `max_per_ref=2` ogni riferimento può dare credito a due goal generati. A parità di credito totale si prende l'abbinamento con la recall più alta, così il voto non dipende dall'ordine dei goal. Una lista vuota vale 0 | Liste generate e `notebook/groundtruth.py` | Punteggi restituiti al chiamante |
| `src/evaluation/phase-3-metric/rescore.py` | Ripunteggia le liste già su disco e scrive accanto a ogni voto goal generati, goal di riferimento, loro rapporto, F1 massimo permesso dalle lunghezze e somiglianza media delle coppie abbinate. Con `--metric new_metric` usa la metrica nuova (punti di `RAMPS`, abbinamento di `MAX_PER_REF`). Con la metrica originale controlla che l'F1 ricalcolato coincida con quello salvato | Le cartelle delle repliche, `notebook/groundtruth.py`, `notebook/system_sets.py` | `lists.csv`, `aggregates.csv`, `scores/<replica>/` nel formato dei CSV delle repliche |
| `src/evaluation/replica_noise.py` | Come nella fase 2. Con `--scores` legge i punteggi da un'altra cartella per replica, per esempio quelle scritte da `rescore.py` | Le cartelle delle repliche e `notebook/system_sets.py` | `cells.csv`, `oscillation.csv`, `null_shift.csv`, `comparisons.csv` |
| `src/diagnostics/metric_diagnostics.py` | Misura le proprietà della metrica: voto a vuoto, effetto delle lunghezze, vincolo uno a uno, separazione fra coppie abbinate nel sistema giusto e fra sistemi diversi, per ogni modello | Le cartelle delle repliche e `notebook/groundtruth.py` | Un file JSON |
| `src/evaluation/phase-3-metric/pair_bench.py` | Costruisce il banco di coppie giudicate a mano. `extract` estrae da una replica le coppie e le congela su disco; `label` le mostra una per volta, senza punteggi, e salva un'etichetta per coppia | Una cartella di replica, `notebook/groundtruth.py` | `pairs.csv`, `selection.csv`, `manifest.json`, `labels.csv` |
| `src/evaluation/phase-3-metric/credit_forms.py` | Confronta tre modi di trasformare la somiglianza in credito (somma, soglia, rampa): ricava i punti dalle coppie del banco e misura voto a vuoto, effetto di un goal estraneo, rumore e stabilità dell'ordine delle configurazioni | Le repliche, il banco di coppie | `tests.csv`, `bench_credit.csv`, `lists.csv`, `points.json` |
| `src/evaluation/phase-3-metric/matching_forms.py` | `census` censisce i goal a credito zero; `sample` estrae un campione da giudicare; `winners` accoppia ogni riferimento col goal che lo ha preso; `grid` ripunteggia ogni lista in tutte le combinazioni modello × credito × abbinamento | Le repliche, il banco e il campione giudicato | `census`: `goals.csv`, `lists.csv`, `summary.csv`; `sample`: `pairs.csv`, `selection.csv`; `grid`: `grid.csv`, `lists.csv`, `copies.csv`, `points.json` |
| `src/evaluation/phase-3-metric/bench_agreement.py` | Misura quanto il credito di una metrica segue l'etichetta del giudice, con intervallo bootstrap sulla differenza fra le due metriche | Il banco e il campione giudicato | `pairs.csv`, `agreement.csv`, `points_check.csv`, `partial.csv` |

Le etichette dei file del banco restano in italiano (`equivalente` = equivalent, `parziale` = partial, `diverso` = different): sono valori dei dati, non messaggi.

## Come rifare i numeri

Dalla radice del repository. Le tre repliche della baseline sono quelle della fase 2.

```bash
E=docs/fase_2_rumore/experiments/exp_01_baseline
P=src/evaluation/phase-3-metric
O=docs/fase_3_metrica/experiments/exp_01_baseline
```

**Ripunteggio con la metrica originale** (verifica che l'F1 ricalcolato coincida con quello salvato):

```bash
python $P/rescore.py --runs $E/exp_01_baseline_r1 $E/exp_01_baseline_r2 $E/exp_01_baseline_r3 \
  --out $O/exp_01_baseline_rescore
```

Rilanciato in questo repository: 648 liste ripunteggiate, differenza massima rispetto ai CSV delle repliche 1.8·10⁻⁷.

**Ripunteggio con la metrica nuova e rumore sulle liste ripunteggiate:**

```bash
python $P/rescore.py --metric new_metric \
  --runs $E/exp_01_baseline_r1 $E/exp_01_baseline_r2 $E/exp_01_baseline_r3 \
  --out $O/exp_01_baseline_rescore_new_metric

python src/evaluation/replica_noise.py \
  --runs $E/exp_01_baseline_r1 $E/exp_01_baseline_r2 $E/exp_01_baseline_r3 \
  --scores $O/exp_01_baseline_rescore_new_metric/scores/r1 \
           $O/exp_01_baseline_rescore_new_metric/scores/r2 \
           $O/exp_01_baseline_rescore_new_metric/scores/r3 \
  --out $O/exp_01_baseline_noise_new_metric
```

Rilanciati in questo repository (con scritture in una cartella temporanea): i punteggi per lista e le quattro tabelle del rumore coincidono con quelli ottenuti in origine a meno dell'ultimo decimale arrotondato (differenza massima 10⁻⁶ sui punteggi, 10⁻⁴ sulle tabelle del rumore); i file originali non sono inclusi.

**Accordo col giudice sul banco:**

```bash
python $P/bench_agreement.py --bench <cartella del banco> --sample <cartella del campione> --out <cartella>
```

Rilanciato con il banco e il campione originali (non inclusi): le quattro tabelle coincidono con quelle originali a meno di due celle all'ultimo decimale arrotondato (10⁻⁴) e della ridenominazione delle colonne `credit_candidate*` in `credit_new_metric*`.

**Non rilanciati dopo la preparazione di questo repository** (richiedono il banco o il campione): `pair_bench.py`, `credit_forms.py`, `matching_forms.py`, `metric_diagnostics.py`. Compilano e rispondono a `--help`; gli argomenti sono descritti nei docstring in testa a ciascun file.

La metrica nuova è anche usabile direttamente: `GoalEvaluator(encoder="minilm", ramp=RAMPS["minilm"][nodo], max_per_ref=MAX_PER_REF[nodo])`.
