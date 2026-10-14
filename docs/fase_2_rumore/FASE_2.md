**Data:** 2026-10-14

**Breve descrizione:** indice dei file della fase 2 (misura del rumore): cosa contiene ogni file, a cosa serve ogni script, quali esperimenti sono stati eseguiti e come rifare i numeri.

# Fase 2 — Il rumore

## La domanda

Se si rilancia lo stesso esperimento senza cambiare nulla, di quanto si spostano i punteggi? Senza questa misura nessun confronto fra configurazioni (critico acceso o spento, più esempi nel prompt) si può leggere.

La fase ha prodotto due cose: la misura del rumore sulla baseline e la regola scritta con cui si confronteranno gli esperimenti successivi.

## Cosa contiene questa cartella

```
docs/fase_2_rumore/
├── FASE_2.md                                      questo indice
├── REPORT_FASE_2.md                               report degli esperimenti: perché, domanda, risposta
├── rumore-riepilogo-fase.html                     riepilogo illustrato della fase
├── spiegazione-intervallo-test-dei-ranghi.html    guida a intervallo bootstrap e test dei ranghi
└── experiments/exp_01_baseline/
    ├── exp_01_baseline_r1, _r2, _r3               le tre esecuzioni identiche della baseline
    ├── exp_01_baseline_noise/                     tabelle del rumore
    └── exp_01_baseline_rule_tests/                tabelle delle prove sulle regole di confronto
```

**Da dove partire:** `REPORT_FASE_2.md` per le risposte; `rumore-riepilogo-fase.html` per una lettura illustrata.

## Cosa è stato fatto

| Passo | Cosa | Risultato |
|---|---|---|
| Repliche | La stessa matrice (12 sistemi × 3 shot mode × critico acceso/spento = 72 celle) eseguita tre volte | `exp_01_baseline_r1`, `_r2`, `_r3` |
| Rumore | Confronto delle tre repliche: liste uguali o diverse, oscillazione dei punteggi, spostamento a vuoto | `exp_01_baseline_noise/` |
| Regola di confronto | Sei regole candidate provate su esperimenti simulati dai punteggi veri (falsi allarmi, effetti persi) | `exp_01_baseline_rule_tests/` |
| Script di confronto | La regola scelta, pronta per gli esperimenti successivi | `src/evaluation/compare.py` |

## Il codice

Tutti gli script stanno in `src/evaluation/`, si lanciano dalla radice del repository e usano solo `numpy` e `scipy`. Non chiamano modelli.

| Script | Perché esiste | Legge | Scrive |
|---|---|---|---|
| `replica_noise.py` | Mette a confronto più repliche identiche: quante liste sono uguali, di quanto oscillano i punteggi, quanto si spostano a vuoto. Si rilancia a ogni esperimento | Le cartelle delle repliche e `notebook/system_sets.py` | `cells.csv`, `oscillation.csv`, `null_shift.csv`, `comparisons.csv` |
| `compare.py` | Applica la regola scelta a due configurazioni: differenza media, intervallo bootstrap al 95%, sistemi che migliorano e peggiorano, test dei ranghi (Wilcoxon). Si rilancia a ogni esperimento | Uno o due `cells.csv` | Un CSV con una riga per gruppo di sistemi, tipo di lista e misura |
| `rule_tests.py` | Studio con cui è stata scelta la regola: tasso di falsi allarmi e di effetti persi di sei regole candidate. Resta nel repository per rifare i numeri | `cells.csv` | `rule_tests.csv`, `rule_tests_summary.csv`, `resample_check.csv`, `pairing_check.csv` |

## Gli esperimenti (dati)

Cartelle in `docs/fase_2_rumore/experiments/exp_01_baseline/`:

| Cartella | Contenuto |
|---|---|
| `exp_01_baseline_r1`, `_r2`, `_r3` | Un JSON per sistema e configurazione, i CSV con precision, recall e F1 per tipo di lista, il registro e il log della run. In `_r3` manca `verbose_log.txt` (5 MB di output interno della pipeline, non necessario) |
| `exp_01_baseline_noise/` | Le quattro tabelle di `replica_noise.py`. Una riga di `cells.csv` è un caso: sistema × shot mode × critico × tipo di lista (216 righe) |
| `exp_01_baseline_rule_tests/` | Le quattro tabelle di `rule_tests.py` |

Configurazione delle repliche: generatore `gemini-2.5-flash`, critico `qwen/qwen3.8-27b`, soglia 8,5/10, massimo 3 iterazioni, `temperature=0`. Il modello usato è dichiarato nei JSON e nel registro di ogni replica.

## Come rifare i numeri

Dalla radice del repository.

**Rumore sulle tre repliche** (le quattro tabelle sono state rigenerate in questo repository e coincidono byte per byte con quelle presenti):

```bash
E=docs/fase_2_rumore/experiments/exp_01_baseline
python src/evaluation/replica_noise.py \
  --runs $E/exp_01_baseline_r1 $E/exp_01_baseline_r2 $E/exp_01_baseline_r3 \
  --out $E/exp_01_baseline_noise
```

**Prove sulle regole candidate** (predefiniti: 1000 simulazioni, 1000 ricalcoli del bootstrap, 200 rimescolamenti, seme `20261011`; `--device cuda` sposta il bootstrap su GPU):

```bash
python src/evaluation/rule_tests.py \
  --cells $E/exp_01_baseline_noise/cells.csv \
  --out $E/exp_01_baseline_rule_tests
```

**Confronto fra due configurazioni** (esempio: critico acceso contro spento, FEW_SHOT; la differenza riportata è B − A):

```bash
python src/evaluation/compare.py \
  --cells-a $E/exp_01_baseline_noise/cells.csv --shot-a FEW_SHOT --critic-a OFF \
  --shot-b FEW_SHOT --critic-b ON \
  --out docs/<cartella_fase>/experiments/<esperimento>/<nome>.csv
```

Se le due configurazioni vengono da esperimenti diversi si aggiunge `--cells-b`. Nessun risultato di `compare.py` è ancora stato salvato fra i risultati. I comandi di `rule_tests.py` e `compare.py` sono ricostruiti dagli argomenti degli script: `rule_tests.py` è stato provato su una versione ridotta (20 simulazioni), `compare.py` solo con `--help`.

## Nota sul notebook

Il notebook `notebook/experiments.ipynb` scrive i risultati di una nuova run in `artifacts/results/<RUN_LABEL>/` (vedi `INDEX.md`). Per tenere la struttura di questo repository, la cartella della run va spostata in `docs/<cartella_fase>/experiments/<esperimento>/` dopo l'esecuzione.
