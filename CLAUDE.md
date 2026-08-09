# Festival Energy Tracker — werkinstructies

Vijf standalone web-apps die per stage voorspellen **waar de crowd danst** (niet
staat te praten), live reagerend op het weer. Gebouwd voor en met Bart.

## ⚠️ Lees eerst

**`docs/muziek-dna.md`** — Barts muzieksmaak, de drie dislikes en de regels voor
aanbevelingen. Zonder dat document geef je verkeerde picks. Lees het voordat je
ook maar één set markeert. **Kern: Bart heeft twee profielen — thuis (melodisch,
122–128 BPM) en festival (hard, 130–140+). Deze apps gebruiken altijd het
festivalprofiel.**

Achtergrond, alleen nodig bij grotere wijzigingen:
- `docs/DESIGN-tml-energy-tool.md` — het oorspronkelijke ontwerp: scoringsmodel,
  gewichten, weer-integratie, stage-metadata.
- `docs/muziek-dna-2025-origineel.md` — Barts eigen profiel van okt 2025 (na
  Draaimolen); structuur geldt nog, delen zijn achterhaald.
- `docs/handover-festival-tool.md` — het recept van Barts eerdere tools.
- `tools/` — de generatoren, met een waarschuwing in `tools/README.md`: draai ze niet
  blind opnieuw.

## Apps

| Pad | Festival | Datum |
|---|---|---|
| `/index.html` | Tomorrowland W1 (Bart) | 16–19 juli 2026, Boom |
| `/awakenings/` | Awakenings zondag | 12 juli 2026, Hilvarenbeek |
| `/jesse/` | TML W2 vrijdag (voor Jesse, Barts smaak) | 24 juli 2026, Boom |
| `/milkshake/` | Milkshake za + zo | 25–26 juli 2026, Westerpark |
| `/tillatec/` | Tillatec × WorldPride (34-uurs marathon) | 1–3 aug 2026, Amsterdam |

Elke app is **één self-contained HTML-bestand**: engine, data en UI in één. Ze delen
de engine door kopiëren, niet door importeren — een engine-fix moet je dus bewust in
elke app doorvoeren.

## Data zit in de HTML zelf

De drie datablokken bovenin elk bestand zijn de bron van waarheid en direct te
bewerken. De generatoren in `tools/` zijn naslag, geen build-stap:

```js
const TIMETABLE = [ {day, stage, artist, start, end, pick:"must"|"rec"|"", genre}, … ];
const STAGES    = { slug: {name, cover:"indoor"|"covered"|"open", size, dark, verified, fit?, lightshow?} };
const ARTISTS   = { "Naam": { energy: 0-100, note? } };
```

- `pick:"must"` = 🔴 van Bart zelf · `pick:"rec"` = 🟠 tip · leeg = niet gemarkeerd.
- `verified:false` toont een `?`-badge; zet pas op `true` als **Bart** de dekking
  bevestigt. Nooit zelf zomaar op `true` zetten.
- Tijden `"HH:MM"`; uren vóór de dagstart horen bij de volgende ochtend.

## Tillatec wijkt af

Die app draait een **nacht-model** voor de 34-uurs marathon: `DAY_START`/`DAY_END`
per dag, `toMin(hhmm, day)` in plaats van een vaste 06:00-grens, `festHour` mapt naar
dezelfde 11..37-ruimte, en de `slotCurve` piekt om **02:00–06:00** in plaats van in
de avond. Kopieer die engine niet terug naar de dag-festivals.

## Werkwijze

1. **Ontwikkelen** op branch `claude/tomorrowland-stage-predictor-moik2y`.
2. **Testen vóór elke push** — headless met Playwright (`/opt/pw-browsers/chromium`),
   open de app met `?test=1&now=YYYY-MM-DDTHH:MM` en controleer dat alle
   `runTests()`-checks groen zijn én dat er geen `pageerror` is. Elke app heeft een
   eigen testset; werk de verwachte aantallen bij als je data toevoegt.
3. **Deployen** = mergen naar `main` (`git merge --no-ff`) en pushen; GitHub Pages
   pakt het automatisch op. Bart herlaadt de PWA soms twee keer wegens de
   service worker.
4. **Simuleren** kan altijd met `?now=…`, plus `&rain=demo` voor het regenscenario.

## Omgang met Bart

- Timetables komen als **screenshot**; transcribeer die met de tijden en namen exact
  zoals ze er staan, inclusief afgekapte namen (`Mark Wit...`) — en meld welke je
  niet zeker kon lezen. Nooit een fan-site scrapen.
- Zijn **picks zijn heilig**: bij een nieuwe timetable neem je ze 1-op-1 mee via
  artiestnaam. Eigen suggesties benoem je expliciet als suggestie.
- Hij corrigeert graag en snel (stage-dekking, energie, namen). Vraag liever door dan
  te gokken, en zeg eerlijk wat je niet kon lezen.
- Antwoord in het Nederlands.
