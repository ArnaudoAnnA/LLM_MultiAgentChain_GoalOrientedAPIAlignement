**Data:** 2026-10-14

**Breve descrizione:** report degli esperimenti sul rumore del sistema di estrazione dei goal: cosa è stato eseguito, perché, a quale domanda rispondeva ciascun esperimento e quale risposta è emersa. Pensato per essere letto senza conoscere i dettagli del lavoro.

# Quanto rumore c'è nel sistema di estrazione dei goal, e come si decide se una modifica lo migliora davvero

## Sintesi

Il sistema estrae da un testo che descrive un software gli attori e gli obiettivi (goal) del sistema stesso. Prima di provare qualunque modifica al sistema (un critico che rivede l'output, esempi nel prompt) serviva sapere una cosa: **se rilancio lo stesso esperimento, senza cambiare nulla, di quanto si spostano i risultati?** Se i risultati si muovono da soli quanto l'effetto di una modifica, ogni confronto è inconcludente.

Gli esperimenti hanno risposto così:

1. **Il sistema non è ripetibile.** Con le stesse impostazioni e gli stessi input produce quasi sempre liste di goal diverse (le tre esecuzioni coincidono in 1–2 casi su 72). Gli attori sono più stabili (46 casi su 72).
2. **Il punteggio oscilla di circa 0.02–0.03** (su una scala da 0 a 1) fra due esecuzioni identiche; in un caso su dieci arriva a 0.08–0.12 o più. A oscillare è la precision, non la recall.
3. **Con le tre esecuzioni disponibili, critico ed esempi nel prompt non producono differenze chiaramente più grandi del rumore.** Su 27 confronti, 4 superano il rumore in tutte e tre le esecuzioni, ma nessuno di questi 4 regge a un esame più attento: due dipendono da un solo sistema, uno cambia segno fra gruppi di sistemi, uno supera il rumore per un soffio.
4. **È stata scelta una regola per decidere se una differenza è reale:** l'intervallo di confidenza bootstrap al 95% sulla differenza media, affiancato dal conteggio dei sistemi che migliorano e peggiorano e dal test dei ranghi di Wilcoxon. La regola riconosce in modo affidabile un miglioramento di circa 0.05 su 12 sistemi e di circa 0.10 su 8 o su 4.

## 2. Materiali e metodo comune

### 2.1 Sistemi e riferimento

- **12 sistemi software** con lista di riferimento (ground truth) annotata a mano: attori, HLG e LLG per ciascuno. I testi di input sono congelati: sono identici in tutte le esecuzioni, così l'unica fonte di variazione è la generazione. Tre testi originariamente in italiano sono stati tradotti in inglese prima delle ultime due repliche; le celle già prodotte su quei sistemi sono state rigenerate sui testi tradotti.

### 2.2 Cosa è stato eseguito

La stessa matrice, tre volte (`exp_01_baseline_r1`, `_r2`, `_r3`), senza cambiare nulla fra una esecuzione e l'altra (una *replica*):

| Dimensione | Valori |
|---|---|
| Sistemi | 12 |
| Esempi nel prompt | zero, uno, più di uno |
| Critico | acceso, spento |
| Tipo di lista | attori, HLG, LLG |

Un **caso** è una combinazione di sistema, numero di esempi, critico e tipo di lista: 216 casi, ognuno con tre punteggi.

### 2.3 Come si misura un punteggio

Per ogni caso si confronta la lista generata con quella di riferimento. Ogni voce è trasformata in un vettore con il modello `bert-base-uncased`; si calcola la similarità coseno fra ogni coppia (voce generata, voce di riferimento) e si abbina ogni voce generata ad al più una voce di riferimento, massimizzando la somiglianza totale.

- **Precision** = somiglianza totale ÷ numero di voci generate (quante delle voci prodotte sono "giuste").
- **Recall** = somiglianza totale ÷ numero di voci di riferimento (quante delle attese sono state trovate).
- **F1** = media armonica di precision e recall, da 0 a 1.

La metrica è quella del lavoro da cui parte il sistema e non è stata ancora validata: i numeri di questo report vanno letti come misure di *variazione*, non come giudizi assoluti sulla qualità.

### 2.4 Termini usati

| Termine | Significato |
|---|---|
| **Rumore** (o tremolio) | Differenza fra due esecuzioni identiche della stessa configurazione |
| **Mediana** | Il valore al centro: metà dei casi sta sotto, metà sopra |
| **Una volta su dieci** | 90° percentile: il valore che solo un caso su dieci supera |
| **Falso allarme** | Una regola dice "c'è un effetto" quando fra le due configurazioni non c'è alcuna differenza reale |
| **Effetto perso** | Una regola dice "nessun effetto" quando la differenza reale esiste |
| **Intervallo bootstrap** | Si ripesca a caso, molte volte, sistemi e repliche dai dati e si ricalcola la differenza media; l'intervallo che contiene il 95% dei valori ottenuti dice quanto è incerta la differenza. Se lo zero resta fuori, la differenza è riconosciuta [1], [2] |
| **Test dei ranghi di Wilcoxon** | Test che guarda, per ogni sistema, se la differenza è positiva o negativa, pesando di più le differenze più grandi; dice quanti sistemi sono d'accordo, non di quanto [1], [3] |

## 3. Esperimenti

### Esperimento 1 — Il sistema ripete lo stesso risultato?

**Perché.** Se due esecuzioni identiche danno liste diverse, il confronto fra configurazioni va fatto su più esecuzioni.

**Domanda.** Rilanciando senza cambiare nulla, la lista prodotta per uno stesso caso è la stessa?

**Come.** Per ognuno dei 72 casi per tipo di lista si confrontano le tre liste prodotte, ignorando l'ordine delle voci.

**Risultato.**

| Tipo di lista | Casi con le tre liste uguali | Critico spento | Critico acceso |
|---|---|---|---|
| Attori | 46 su 72 | 28 su 36 | 18 su 36 |
| HLG | 2 su 72 | 1 su 36 | 1 su 36 |
| LLG | 1 su 72 | 1 su 36 | 0 su 36 |

**Risposta.** No. Gli attori sono stabili in circa due casi su tre; i goal cambiano praticamente sempre. La variazione c'è già a critico spento, quindi nasce nel generatore; sugli attori il critico ne aggiunge altra (le liste uguali scendono da 28 a 18 su 36).

### Esperimento 2 — Di quanto si sposta il punteggio da solo?

**Perché.** Conoscere l'ampiezza del rumore è la condizione per leggere qualunque differenza.

**Domanda.** Fra due esecuzioni identiche, di quanto differisce l'F1 dello stesso caso? E di quanto si sposta la media su tutti i sistemi?

**Come.** Per ogni caso e per ogni coppia di repliche (3 coppie × 216 casi = 648 confronti) si calcola il valore assoluto della differenza di F1. Per la media sui sistemi si confrontano le medie di due repliche della stessa configurazione.

**Risultato.**

| Tipo di lista | Spostamento tipico (mediana) | Una volta su dieci |
|---|---|---|
| Attori | 0.00 | 0.08 o più |
| HLG | 0.02 | 0.10 o più |
| LLG | 0.03 | 0.12 o più |

La media sui 12 sistemi si sposta da sola fino a 0.04 (fino a 0.06 sui 4 sistemi di sviluppo).

Un esempio concreto: sugli LLG di *Assegno Unico Universale*, con critico acceso e senza esempi, la prima esecuzione produce 115 goal e la terza 53. La recall è la stessa (0.82 e 0.80), la precision passa da 0.19 a 0.42 e F1 da 0.31 a 0.55: il sistema trova le stesse cose giuste, ma ogni volta aggiunge un numero diverso di voci in più.

Il rumore non è uniforme: sugli LLG il sistema più instabile (*Assegno Unico Universale*, oscillazione tipica 0.13) oscilla sei volte più del più stabile (*London Ambulance Service*, 0.02).

**Risposta.** Il punteggio oscilla da solo di 0.02–0.03 e, nei casi sfortunati, di 0.10 o più; la media sui sistemi di circa 0.04. A oscillare è la precision, perché cambia il numero di voci superflue, non la recall.

### Esperimento 3 — Critico ed esempi fanno meglio del rumore?

**Perché.** Sono le due modifiche già disponibili nel sistema: è il caso reale su cui provare il rumore appena misurato.

**Domanda.** La differenza fra due configurazioni è più grande di quella dovuta al solo caso?

**Come.** Per ogni tipo di lista si fanno 9 confronti: 3 sul critico (acceso − spento, con zero, uno o più esempi) e 6 sugli esempi (tre coppie di quantità di esempi, a critico acceso e a critico spento). Per ognuno, e per ogni replica, si calcola la differenza media di F1 sui 12 sistemi e la si confronta con quanto si sposta da sola la media rilanciando una delle due configurazioni. Un confronto è *costante* se la differenza supera il rumore in tutte e tre le repliche, *incerto* se lo supera in una o due.

**Risultato.**

| Tipo di lista | Confronti | Costanti | Incerti | Mai oltre il rumore |
|---|---|---|---|---|
| Attori | 9 | 3 | 3 | 3 |
| HLG | 9 | 0 | 4 | 5 |
| LLG | 9 | 1 | 6 | 2 |

I 4 confronti costanti:

| Confronto | Differenza di F1 nelle tre repliche | Rumore massimo |
|---|---|---|
| Attori: critico acceso − spento, con un esempio | +0.038, +0.056, +0.045 | 0.012 |
| Attori: più esempi − zero esempi, critico spento | +0.053, +0.048, +0.068 | 0.013 |
| Attori: più esempi − un esempio, critico spento | +0.052, +0.058, +0.063 | 0.006 |
| LLG: critico acceso − spento, con più esempi | −0.026, −0.032, −0.040 | 0.025 |

Guardando dentro i quattro:

- **Esempi sugli attori:** i due confronti dipendono da un solo sistema, *Fitness Tracker*, che con più esempi passa da 0.29 a 1.00. Senza di lui la differenza media scende sotto 0.01.
- **Critico sugli attori:** in media il critico abbassa F1 nei 4 sistemi di sviluppo e lo alza negli altri 8: l'effetto dipende dal sistema.
- **Critico sugli LLG con più esempi:** il critico *toglie* circa 0.03; nella prima replica supera il rumore per un soffio (0.026 contro 0.025).

**Risposta.** Con queste tre esecuzioni non si può affermare che critico o esempi migliorino i risultati in generale. Sugli HLG nessuna configurazione è riconoscibilmente migliore di un'altra. Questa lettura è preliminare: la regola con cui giudicare i confronti è stata scelta dopo averne visto i numeri, e per questo è stata poi sostituita da una scelta fatta con prove esplicite (Esperimento 4).

### Esperimento 4 — Quale regola di confronto sbaglia meno?

**Perché.** La lettura dell'Esperimento 3 non è una regola: serve un criterio fissato *prima* di guardare i dati, di cui si conoscano i tassi di errore.

**Domanda.** Fra sei regole candidate per decidere "questa differenza è un effetto reale", quale commette meno errori, sia dicendo "effetto" quando non c'è (falso allarme) sia non vedendolo quando c'è (effetto perso)?

**Le sei regole.**

| Regola | In breve |
|---|---|
| Permissiva | Rumore stimato dalle due configurazioni; basta superarlo in 2 repliche su 3 |
| Intermedia | Come sopra, ma va superato in tutte e 3 |
| Severa | Rumore stimato da tutto il tipo di lista; va superato in tutte e 3 |
| Severa con verso | Come la severa, più il saldo dei sistemi a favore |
| Test dei ranghi | Wilcoxon sulle differenze per sistema, a repliche mediate; si dice "effetto" se la probabilità di osservarlo per caso è sotto 5 su 100 |
| Intervallo | Bootstrap su sistemi e repliche; "effetto" se l'intervallo al 95% non contiene lo zero |

**Come.** Per provare una regola servono molti esperimenti di cui si conosca già la risposta giusta. Se ne ha uno solo (le tre repliche), quindi si costruiscono **esperimenti simulati con i numeri veri**: per ogni caso, un punteggio medio e un'oscillazione pari a quelli osservati; due copie della stessa configurazione (la risposta giusta è "nessun effetto") oppure una copia con un miglioramento noto aggiunto (+0.03, +0.05, +0.10; la risposta giusta è "effetto"). Ogni numero riportato sotto è una frequenza su 1000 esperimenti simulati per ognuna delle 6 configurazioni (3 quantità di esempi × critico acceso/spento).

Il criterio di scelta è stato scritto prima di guardare i risultati: scartare le regole con più di 5 falsi allarmi su 100; fra le rimaste, preferire quella che riconosce l'effetto più piccolo almeno 80 volte su 100; a parità, la più semplice.

**Risultato 1 — falsi allarmi** (su 100 confronti fra copie identiche, 12 sistemi, media sulle 6 configurazioni):

| Regola | Attori | HLG | LLG |
|---|---|---|---|
| Permissiva | 5.9 | 5.9 | 6.4 |
| Intermedia | 1.5 | 1.2 | 1.3 |
| Severa | 0.0 | 0.0 | 0.0 |
| Severa con verso | 0.0 | 0.0 | 0.0 |
| Test dei ranghi | 1.4 | 4.8 | 4.1 |
| Intervallo | 1.1 | 2.1 | 1.9 |

La permissiva supera il limite di 5 e viene scartata. Il test dei ranghi resta sotto, ma di poco; nella configurazione peggiore lo supera (sui 12 sistemi: 6.1). Le due severe non sbagliano mai in questo senso: è un pregio solo se vedono anche gli effetti veri.

**Risultato 2 — effetti riconosciuti** (miglioramento uguale per tutti i sistemi, 12 sistemi, volte su 100; l'intervallo di valori va dal tipo di lista in cui la regola va peggio a quello in cui va meglio; la permissiva, già scartata, non è riportata):

| Regola | +0.03 | +0.05 | +0.10 |
|---|---|---|---|
| Intermedia | 20–53 | 52–75 | 96–98 |
| Severa | 2–3 | 33–63 | 99 |
| Severa con verso | 0–3 | 3–63 | 26–99 |
| Test dei ranghi | 74–92 | 95–98 | 100 |
| Intervallo | 57–77 | 88–94 | 100 |

Solo test dei ranghi e intervallo riconoscono +0.05 in modo affidabile (almeno 80 su 100 in tutti i tipi di lista). Nessuna regola vede in modo affidabile +0.03 su tutti i tipi di lista.

**Risultato 3 — due situazioni che le regole distinguono male.**

- **Migliora solo metà dei sistemi** (miglioramento raddoppiato nei 6 che migliorano, 0 negli altri): il test dei ranghi, con +0.10, scende a 71–93 su 100; l'intervallo resta a 98–99.
- **Migliora un solo sistema** (come nel caso di *Fitness Tracker*): sono da evitare le regole che guardano solo la media, perché scambiano un salto di un sistema per un miglioramento generale (permissiva da 47 a 100 volte su 100, intermedia da 20 a 98, severa da 2 a 100). Test dei ranghi (2–5) e intervallo (3–5) non ci cascano.

**Risultato 4 — dipendenza dall'abbinamento delle repliche.** Le quattro regole "replica per replica" confrontano la prima replica di una configurazione con la prima dell'altra, e così via; ma l'ordine delle repliche è arbitrario. Rimescolando quell'ordine, l'esito cambia in 18 confronti su 27 per la permissiva e in 17 su 27 per l'intermedia. Test dei ranghi e intervallo fanno prima la media delle repliche e non hanno il problema.

**Risultato 5 — con pochi sistemi.** Il miglioramento più piccolo riconosciuto in modo affidabile sale con il restringersi del gruppo:

| Regola | 12 sistemi | 8 di conferma | 4 di sviluppo |
|---|---|---|---|
| Test dei ranghi | 0.05 | 0.10 | nessuno |
| Intervallo | 0.05 | 0.10 | 0.10 |

Con 4 sistemi il test dei ranghi non può mai riconoscere una differenza (con così pochi dati la probabilità minima che può dare è già sopra la soglia). Anche l'intervallo, sui 4, perde più della metà degli effetti se migliorano solo due sistemi su quattro (33–43 volte su 100 a +0.10).

**Risposta.** Il criterio fissato prima indica l'**intervallo bootstrap**. Il test dei ranghi è un po' più sensibile quando tutti i sistemi migliorano di poco, ma perde effetti concentrati in metà dei sistemi e non funziona sui 4. Le quattro regole replica per replica sono state abbandonate.

### Esperimento 5 — Controllo del metodo con i valori veri

**Perché.** I falsi allarmi dell'Esperimento 4 dipendono da come sono state costruite le repliche simulate.

**Domanda.** La classifica delle regole cambia se invece di inventare repliche si ripescano i tre valori veri di ogni caso?

**Risultato** (falsi allarmi su 100, 12 sistemi, tipo di lista peggiore):

| Regola | Repliche simulate | Valori veri ripescati |
|---|---|---|
| Permissiva | 6.4 | 6.6 |
| Intermedia | 1.5 | 2.2 |
| Severa | 0.0 | 0.0 |
| Severa con verso | 0.0 | 0.0 |
| Test dei ranghi | 4.9 | 3.9 |
| Intervallo | 2.1 | 2.2 |

**Risposta.** No: l'ordine delle regole resta lo stesso. Il controllo riguarda solo i falsi allarmi, non gli effetti persi.

## 4. La regola adottata

Sulla base dei risultati, ogni confronto fra due configurazioni si legge così:

| Elemento | Scelta |
|---|---|
| Numero di repliche | Tre per ogni configurazione (non è stato misurato cosa si guadagnerebbe con più repliche) |
| Misura principale | F1; precision e recall si riportano accanto |
| Verdetto | Intervallo bootstrap al 95% sulla differenza media (si ripescano sistemi e repliche): la differenza è riconosciuta se lo zero resta fuori. Il livello 95% non si cambia dopo aver visto i confronti |
| Letture accanto (non cambiano il verdetto) | Conteggio dei sistemi che migliorano e peggiorano; test dei ranghi sulle differenze per sistema, a repliche mediate |
| 4 sistemi di sviluppo | Solo intervallo e conteggio: il test dei ranghi non può dare un verdetto |
| Quali sistemi usare per giudicare | Non fissato: si decide per ogni esperimento, sapendo che l'effetto più piccolo che si riesce a vedere è circa 0.05 su 12 sistemi e circa 0.10 su 8 o su 4 |
| Critico acceso/spento | Non c'è una regola fissa: si decide per ogni esperimento in base a cosa vuole misurare |

La regola è implementata in `src/evaluation/compare.py`.

## Riferimenti

[1] J. Demšar, «Statistical Comparisons of Classifiers over Multiple Data Sets», *J. Mach. Learn. Res.*, vol. 7, pp. 1–30, 2006.

[2] T. Berg-Kirkpatrick, D. Burkett, D. Klein, «An Empirical Investigation of Statistical Significance in NLP», in *Proc. EMNLP-CoNLL*, 2012, pp. 995–1005.

[3] F. Wilcoxon, «Individual comparisons by ranking methods», 1945 (citato in [1]).
