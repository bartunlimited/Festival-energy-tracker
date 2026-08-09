# tools/ — generatoren en testscripts

Deze scripts bouwden de apps. Ze zijn op 1 augustus 2026 **teruggehaald uit het
sessie-transcript** nadat de tijdelijke werkmap was leeggelopen.

## ⚠️ Let op: dit zijn de as-written versies

Elk script is de versie zoals hij oorspronkelijk werd weggeschreven. Verschillende
scripts zijn daarná nog ter plekke aangepast (via losse commando's, die niet in deze
bestanden terechtkwamen). Bekende gevallen:

- `gen_awak.py` — de STAGES daarin zijn nog de **ongeverifieerde gok**; Bart heeft
  later bevestigd: Area Y is tent, B en C hebben een dak, de rest is buiten.
- `gen_milkshake.py` — de teruggehaalde versie bevat alleen de zondag; zaterdag is
  later toegevoegd.
- `update_tml.py` / `new_tt.py` — misten nog de alias voor `Dimitri Vegas & Like ...`
  en de slug-correctie `the-rave-cave` → `rave-cave`.

**Draai ze dus niet blind opnieuw** — dat draait bovenstaande correcties terug. De
gecommitte HTML-bestanden zijn de bron van waarheid; deze scripts zijn naslag voor
hoe de data is opgebouwd.

## Wat is wat

| Script | Rol |
|---|---|
| `parse.py`, `gen_data.py` | oorspronkelijke extractie van W1 uit `source/tomorrowland-final2.html` |
| `update_tml.py` + `new_tt.py` | de bijgewerkte officiële W1-timetable (388 sets, incl. donderdag) |
| `gen_awak.py` | Awakenings zondag |
| `gen_jesse.py` | TML W2 vrijdag (Jesse) |
| `gen_milkshake.py` | Milkshake |
| `gen_tillatec.py` | Tillatec — bevat de engine-aanpassingen voor het nachtmodel |
| `check.mjs` | headless Playwright-check |

Testen doe je headless met Playwright op `/opt/pw-browsers/chromium`, met
`?test=1&now=…` in de URL; zie `CLAUDE.md`.
