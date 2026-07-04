# Festival Energy Tracker — Tomorrowland W1 2026

Realtime tool die per stage en per uur voorspelt waar de crowd het meest
**danst** (niet staat te praten) op Tomorrowland Weekend 1 (17–19 juli 2026,
Boom). Reageert live op regen: aanbeveling voor overdekte/indoor stages
*vóórdat* de massa verschuift.

## Gebruik

- Open `index.html` via GitHub Pages op iPhone Safari → deel-menu → "Zet op beginscherm".
- **NU**: huidige + volgende set per stage, gesorteerd op live energie-score.
- **SCHEMA**: volledige dag-timetable met filters (stage, "toon vanaf", picks, energie ≥70).
- **WEER**: kwartier-neerslag komende 2 uur + uuroverzicht.

## Test-simulators

- `?now=2026-07-17T22:00` — klok overschrijven (pre-festival dry-run)
- `?rain=demo` — synthetische regenbui over 30 min (test de regenbanner)
- `?test=1` — engine sanity checks in de console

## Status

⚠️ **De timetable is nu DEMODATA.** De echte, geverifieerde W1-timetable moet
worden geëxtraheerd uit Barts bestaande tool: plaats `tomorrowland-final2.html`
in `source/` — zie `source/README.md`.

## Architectuur

Eén statisch `index.html` (inline CSS+JS, geen build, geen backend):

- **DATA**: `TIMETABLE`, `STAGES`, `ARTISTS` (energieprofielen 0–100), `CONFIG` (modelgewichten)
- **APP**: pure scoring-engine · weer-module (Open-Meteo, localStorage-cache, offline-degradatie) · klok-module · render

Score per set: `clamp(0.40·artiest + 0.25·tijdslot + 0.20·stage-fit + 0.15·concurrentie, 0, 100) × weer-multiplier`.
Alle gewichten staan bovenin in `CONFIG` en zijn tuneerbaar zonder de logica aan te raken.
