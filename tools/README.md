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
| `ade_watch.py` | scrapet het ADE-programma en meldt wat er veranderd is |
| `ade_render.mjs` | render-helper voor `ade_watch.py --render` |

## ade_watch.py — ADE-programma bewaken

De enige tool hier die je **wél** gewoon opnieuw mag draaien; hij genereert geen
app-data maar bewaakt de officiële programmapagina.

```bash
python3 tools/ade_watch.py            # scrapen + diffen tegen de snapshot
python3 tools/ade_watch.py --save     # idem, en de snapshot bijwerken
python3 tools/ade_watch.py --render   # via een echte browser (JS-pagina's)
python3 tools/ade_watch.py --dump /tmp/ade.html   # ruwe HTML om selectors te fixen
```

Exit codes: `0` niets veranderd · `1` wijzigingen gevonden · `2` fout of 0 events.

- Sleutel per event is het **id uit de detail-URL** (`/en/program/2026/<slug>/<id>/`),
  niet de titel — hernoemen telt dan als wijziging, niet als nieuw event.
- Twee extractieroutes: eerst JSON-LD `Event`-objecten (schone velden: titel, zaal,
  begin- en eindtijd), anders de links zelf plus een stukje omliggende tekst als
  vingerafdruk. Bij die tweede route diffen we óók op die tekst, want datum en zaal
  zitten er dan alleen ongelabeld in.
- Snapshot en historie staan in `data/ade-2026/` (`snapshot.json`, `changelog.md`).
- `.github/workflows/ade-watch.yml` draait dit elke dag en opent een issue zodra er
  iets verandert.

> ⚠️ **De parser is nooit tegen de echte pagina gedraaid.** De omgeving waarin hij
> geschreven is kon `amsterdam-dance-event.nl` niet bereiken (egress-proxy gaf 403),
> dus hij is getest tegen nagebouwde fixtures. Levert de eerste echte run 0 events op,
> draai dan `--dump` en kijk of de HTML de verwachte `/program/<jaar>/<slug>/<id>/`-links
> bevat; zo niet, dan rendert de pagina via JavaScript en is `--render` nodig.

Testen doe je headless met Playwright op `/opt/pw-browsers/chromium`, met
`?test=1&now=…` in de URL; zie `CLAUDE.md`.
