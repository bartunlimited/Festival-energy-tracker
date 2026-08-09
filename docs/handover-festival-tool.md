# Handover: Festival Schedule Tool (offline iPhone HTML)

Recept voor het bouwen van een offline festivalschema voor Bart's iPhone, zoals gemaakt voor Tomorrowland 2026 W1 (en eerder in React-vorm voor UPCLOSE en 909 Festival).

## Doel

Eén standalone HTML-bestand dat Bart op zijn iPhone opent via de Files-app (Quick Look), volledig offline, zonder apps of internet. Met dag-tabs, stage-filter, uur-filter, en zijn persoonlijke picks gemarkeerd.

## De harde iOS-beperkingen (waarom dit recept zo is)

Dit is de kern van het hele recept. iOS Quick Look (wat opent als je in Files op een HTML-bestand tikt):

1. **Voert GEEN JavaScript uit.** Alles wat met JS is gebouwd toont een lege pagina of alleen de statische delen.
2. **Blokkeert anchor-links** (`<a href="#id">`). Springen binnen de pagina werkt niet.
3. Safari/Firefox op iOS kunnen **geen lokale bestanden openen** — er is geen "open in browser" route. Quick Look is de enige viewer.
4. De Claude-app download-knop levert soms een onvolledig bestand bij .html (de viewer rendert en slaat de DOM op). **Oplossing: lever het bestand als .txt** — dan wordt het als platte tekst opgeslagen (volledig), en Bart hernoemt het in Files naar .html (ingedrukt houden → Wijzig naam → extensie-waarschuwing bevestigen).

## Het enige interactiemechanisme dat werkt: CSS `:checked`

Alle interactie bouwen met verborgen radio/checkbox inputs + labels + CSS sibling-selectors:

```html
<input type="radio" name="day" id="d1" checked>  <!-- verborgen -->
<label for="d1">Vr 17</label>                     <!-- de "knop" -->
```
```css
input { display:none; }
#d1:checked ~ #day1 { display:block; }           /* toon dag 1 */
#d1:checked ~ .tabs label[for=d1] { background:#e63946; }  /* actieve tab */
```

**Kritisch:** alle inputs moeten *siblings* zijn van (en vóór) de content-divs in de DOM, anders werkt de `~` selector niet. Structuur:

```
<body>
  header
  [alle inputs: dag-radio's, picks-checkbox, uur-radio's, stage-radio's]
  .tabs (dag-labels)
  .opts (picks-label)
  #day1 [stage-nav][uur-nav][content]
  #day2 [...]
  #day3 [...]
```

## De vier filters

1. **Dag-tabs**: radiogroep `name="day"`, toont/verbergt hele dag-divs.
2. **Picks-filter**: checkbox `#po`. `#po:checked ~ .day .card.none { display:none }` + verberg ook `.th` (tijd-headers) want die slaan nergens meer op.
3. **Uur-filter ("toon vanaf")**: radiogroep met optie per uur (12 t/m 25; uren na middernacht = 24/25, label "00"/"01"). Elke kaart en tijd-header krijgt klasse `hXX` (startuur). Gegenereerde CSS per filteroptie F: verberg alle `.hX` met X < F. Dit is het alternatief voor "scroll naar nu": Bart tikt het huidige uur aan en dat staat bovenaan.
4. **Stage-filter**: radiogroep, elke kaart krijgt stage-klasse `s0..s14`. Bij selectie: `#s3r:checked ~ .day .card:not(.s3) { display:none !important }`.

Alle filters combineren vrij (bijv. Atmosphere + vanaf 20 + alleen picks).

## Data-model

Per set één record: `{d: dag(1-3), st: stage, s: "HH:MM" start, e: "HH:MM" eind, a: artiest, g: genre/stijl, r: "must"|"rec"|"none"}`

- Tijden na middernacht: bij sorteren/uurklassen uur+24 als uur < 6.
- Sorteer chronologisch op starttijd, groepeer onder tijd-headers (`.th`) per unieke starttijd.
- Lange stagenamen inkorten voor leesbaarheid ("House of Fortune by JBL" → "House of Fortune").

## Data verzamelen

- Officiële festivalsites zijn vaak geblokkeerd voor web_fetch én staan niet op de container-allowlist. Timetable-data zit bovendien meestal in een JS-component, niet in de HTML.
- Fan-bronnen (Clashfinder e.d.) bleken onbetrouwbaar (verkeerde tijden/acts).
- **Beste route: Bart stuurt screenshots van de officiële timetable.** Die uitlezen is accuraat gebleken. Afgekapte namen ("Symphony Of...") overnemen zoals getoond en aan Bart vragen.

## Aanbevelingen (r-veld)

Gebruik Bart's Music DNA uit het geheugen. Kernpunten: heel breed spectrum (hard techno t/m mainstage EDM/trance/pop-crossover), dislikes alleen experimental/ambient, dubstep, en Dimitri Vegas & Like Mike. Markeer ruim: alle goede DJs op alle stages — Bart kiest zelf op basis van mood/weer/crowd/binnen-buiten. Verwacht iteratie: Bart corrigeert ratings per artiest; verwerk die en update zo nodig het DNA-geheugen.

## Opmaak (leesbaarheid zonder leesbril)

- Puur zwart (`#000`) achtergrond, alle tekst wit en bold.
- **Alle content-tekst 22px**: artiestennaam (800), tijd, stage, genre (cursief ter onderscheiding).
- Tijd-headers 20px, sticky (`position:sticky; top:0`).
- Must-cards: donkerrode achtergrond `#38070c`, felrode linkerrand `#ff4d5a`, MUST-badge. Tip-cards: donkeroranje `#2e1e08`, rand `#ffa940`, TIP-badge. Prefix 🔴/🟠 vóór de artiestennaam.
- Grote tap-targets (chips ~11px 16px padding), horizontaal scrollende chip-balken zonder zichtbare scrollbar.
- `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` en safe-area padding.

## Genereren

Bouw het bestand met een Python-script (string-templating): parse de set-data, genereer per dag de HTML-kaarten, genereer de uur- en stage-filter-CSS programmatisch (dat zijn tientallen regels), en schrijf één bestand. Sanity checks: geen `<a href=` aanwezig, inputs staan vóór de day-divs, aantal musts/picks klopt.

## Levering aan Bart

1. Kopieer het .html-bestand naar een .txt met duidelijke naam: `naam-RENAME-NAAR-HTML.txt`.
2. Present via present_files.
3. Instructies: bewaar in Files → hernoem naar .html → tik om te openen.
4. Laat Bart testen; itereer op ratings en leesbaarheid.

## Wat NIET te doen

- Geen JavaScript voor kernfunctionaliteit (zoekbalk is daarom gesneuveld — acceptabel verlies).
- Geen anchor-navigatie.
- Geen React-artifact als einddoel (werkt alleen in de Claude-app; Bart wil erbuiten).
- Geen publieke artifact-link (Bart wees dit af).
- Niet vertrouwen op fan-timetables zonder verificatie.
