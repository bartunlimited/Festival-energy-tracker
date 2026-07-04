# Source data

Plaats hier Barts bestaande, geverifieerde tool:

    source/tomorrowland-final2.html

Dit bestand bevat de volledige W1-timetable (3 dagen × 16 stages × 330+ acts,
gebouwd op basis van officiële screenshots — NIET her-scrapen van fan-sites)
plus zijn persoonlijke picks (must/tip-markeringen).

Zodra het bestand hier staat:

1. Parse het naar `TIMETABLE`-records: `{day, stage, artist, start, end, pick, genre}`
   — picks 1:1 overnemen.
2. Verifieer de aantallen: 3 dagen, 16 stages, 330+ acts, alle picks aanwezig.
3. Vervang de DEMODATA in `index.html` en zet `DEMO_DATA = false`.
4. Genereer `ARTISTS`-energieprofielen voor alle acts (heuristiek in het
   design-document) + een review-tabel voor Bart.
5. Vul `STAGES` aan voor alle 16 stages; onbekend → `cover:"open", verified:false`.
