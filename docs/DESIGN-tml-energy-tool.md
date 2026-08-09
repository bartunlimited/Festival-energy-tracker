# Design Document — Tomorrowland W1 "Dance Energy" Predictor

**Project:** Realtime tool that predicts, per stage and per hour, where the crowd is most likely to be *dancing* (not standing around talking) at Tomorrowland Weekend 1 (July 17–19, 2026, Boom, Belgium), and that reacts live to local rain by recommending covered/indoor stages *before* the crowd shifts.

**For:** Claude Code implementation session.
**User:** Bart — experienced festival-goer, iPhone user, technical. UI language: Dutch. Code/comments: English.

---

## 1. Product goal

Bart's festival behavior: he walks around and locks in where the dancefloor energy is right. Energy depends on: (a) the DJ's style/intensity, (b) the crowd a slot+stage attracts, (c) competition from simultaneous sets, (d) weather, (e) indoor vs outdoor. The tool formalizes this intuition into a per-set **energy score (0–100)** and adds a realtime layer: clock-aware "now/next" view and rain-radar-driven advice.

Key differentiator over just checking Buienradar: **anticipation**. When rain is predicted in ~30–45 min, the tool should tell him where to go *and by when*, because everyone else moves when the rain starts — arriving 15 min early beats the queue.

## 2. Hard constraints

1. **Single static HTML file** (`index.html`), self-contained: inline CSS + JS, no build step, no framework, no backend. All intelligence runs client-side.
2. **Hosted on GitHub Pages** (Bart opens it in iOS Safari, added to homescreen). This replaces his previous Quick Look constraint (no-JS): JavaScript is now allowed and required.
3. **Weather APIs must be callable directly from the browser** (CORS). No API keys.
4. **Graceful degradation**: festival network is unreliable (400k phones on one field). If fetch fails → use last cached forecast from `localStorage` with a visible "stale since HH:MM" indicator; if nothing cached → fall back to the static prediction model. The tool must never break offline.
5. **Battery-friendly**: weather poll every 10 min max (and on `visibilitychange` when returning to the app), clock tick 1/min. No continuous animation.
6. **Readability recipe from Bart's previous tools**: mobile-first, high contrast black/white, large bold text (~22px), day tabs, stage filter, hour filter ("show from"), picks filter — all present simultaneously. Keep this visual language; JS may simplify the old CSS-:checked mechanics.

## 3. Architecture

```
index.html
├── <style>   inline CSS (b/w, 22px, filter chips)
├── <script>  DATA block
│   ├── TIMETABLE   — all sets: {day, stage, artist, start, end, pick, genre}
│   ├── STAGES      — metadata per stage (see §5)
│   ├── ARTISTS     — energy profiles (see §6)
│   └── CONFIG      — model weights + tunables (see §7)
└── <script>  APP block
    ├── scoring engine (pure functions, no I/O)
    ├── weather module (fetch + cache + degrade)
    ├── clock module (real time or ?now= override)
    └── render (views, filters, rain banner)
```

Optional (nice-to-have, phase 2): `manifest.json` + minimal service worker so the homescreen icon behaves like an app and the shell loads offline. Not required for v1.

## 4. Source data

- **Timetable**: Bart provides his existing working tool `tomorrowland-final2.html` (place in repo under `/source/`). It contains the verified W1 timetable (3 days × 16 stages × 330+ acts, built from official screenshots — do NOT re-scrape from fan sites like Clashfinder; those were proven wrong) plus his personal picks. **First implementation task: parse this file and extract TIMETABLE as structured JSON.** Preserve the pick markers exactly.
- **Stage metadata**: initial table in §5, but several indoor/covered classifications are **unverified for the 2026 layout** — flag these in the UI data as `verified: false` and ask Bart to confirm/correct before the festival.
- **Artist energy profiles**: generate initial scores with the heuristics in §6, output as a reviewable table (Markdown) for Bart to tune. His corrections are the calibration step.

## 5. Stage metadata (schema + starting point)

```js
STAGES = {
  "mainstage":      { cover: "open",    size: "XL", dark: false, verified: true  },
  "freedom":        { cover: "indoor",  size: "L",  dark: true,  verified: true  },  // indoor hall, famous LED ceiling
  "the-rave-cave":  { cover: "covered", size: "S",  dark: true,  verified: true  },
  "atmosphere":     { cover: "covered", size: "M",  dark: true,  verified: false },  // dome in earlier editions — verify 2026
  "core":           { cover: "open",    size: "M",  dark: false, verified: true  },  // forest stage
  "elixir":         { cover: "covered", size: "S",  dark: false, verified: false },
  "crystal-garden": { cover: "indoor",  size: "M",  dark: true,  verified: false },
  // ... complete from the extracted timetable's stage list; anything unknown => cover:"open", verified:false
}
```

Fields:
- `cover`: `indoor` | `covered` (roof, open sides) | `open`
- `size`: XS–XL (affects intimacy: on small stages you stand *in* the music; on Mainstage you can chat 50 m from the speakers)
- `dark`: enclosed/dark stages promote dancing even in daytime

## 6. Artist energy profile (0–100)

Heuristic base score per artist, from genre + set type:

| Component | Range | Logic |
|---|---|---|
| Genre intensity | 0–40 | hard/industrial/peak techno 35–40 · tech house / driving house 28–35 · trance/big-room 25–35 · melodic/progressive 18–28 · downtempo/ambient 0–10 |
| Set type | 0–15 | DJ set 12–15 · hybrid 8 · live act 4 (live acts attract watchers, not dancers) |
| Track familiarity | 0–20 | relentless underground (no singalongs) 15–20 · mixed 10 · hit-driven (phones come out, crowd sings/talks between drops) 5–12 |
| Reputation as crowd-mover | 0–25 | manual, from known sets; default 12 |

Emit `ARTISTS = { "Artist Name": { energy: 78, note: "..." }, ... }` for every act in TIMETABLE (default 50 + genre adjustment when unknown), plus a review table for Bart.

## 7. Scoring model (per set, per moment)

```
score(set, t) = clamp( W_a·A + W_s·S(t) + W_g·G + W_c·C , 0, 100 ) · M_weather(t)
```

- **A** — artist energy (§6), normalized 0–1.
- **S(t)** — timeslot curve, universal festival rhythm:
  `12–15h: 0.35 · 15–17h: 0.50 · 17–19h: 0.65 · 19–21h: 0.80 · 21–24h: 1.00 · 00–01h: 0.90`
  Dark/indoor stages (`dark: true`) get `max(S, 0.7)` — inside, daytime barely matters.
- **G** — stage fit: `indoor/covered+dark: 1.0 · covered: 0.85 · open small: 0.75 · open XL: 0.6`.
- **C** — competition, computed from TIMETABLE itself: for each set, find simultaneous sets with similar genre and equal/higher artist energy. No same-genre competition → 1.0; one strong competitor → 0.85; multiple → 0.7. (A mid-size techno DJ with no genre competition gets a concentrated, motivated crowd — often the best floor.)
- **M_weather(t)** — realtime multiplier: dry → 1.0 for all. Rain now or ≤45 min: `indoor 1.15 · covered 1.10 · open 0.55`. Heavy rain: open 0.35. Temperature <14 °C in evening: open −0.1.

Default weights `W_a=0.40, W_s=0.25, W_g=0.20, W_c=0.15` — all in a single `CONFIG` object at the top of the file so Bart can tune without touching logic. **Keep the scoring engine as pure functions of (set, stages, artists, weather, t)** so calibration and the `?now=` simulator are trivial.

Personal picks stay a **separate overlay** (his taste ≠ crowd energy): a pick marker next to the score, never merged into it.

## 8. Weather integration

**Location:** De Schorre, Boom — `lat 51.087, lon 4.379`, timezone `Europe/Brussels`.

**Primary — Open-Meteo** (free, no key, CORS-enabled):
```
https://api.open-meteo.com/v1/forecast?latitude=51.087&longitude=4.379
  &minutely_15=precipitation
  &hourly=temperature_2m,precipitation_probability,precipitation
  &forecast_days=2&timezone=Europe%2FBrussels
```
`minutely_15` gives 15-min-resolution precipitation for the next hours — sufficient for the "rain in ~30 min" trigger.

**Optional secondary — Buienradar** 5-min radar forecast (covers Belgium). **Verify CORS from Safari first**; if blocked, skip it — Open-Meteo alone is acceptable. Do not add a proxy/backend for this.

**Caching:** store last successful response + timestamp in `localStorage`. On fetch failure, use cache and show `Weer: HH:MM (offline)`. Poll: on load, on `visibilitychange`→visible, and every 10 min while visible.

**Rain advice logic:** if precipitation ≥ 0.3 mm within the next 60 min:
1. Show a persistent banner: expected start time, expected duration (first dry 15-min slot after).
2. Recommend the top 2–3 covered/indoor sets *at rain time* by score.
3. Compute "move by": `rain_start − 15 min` (walk + beat-the-crowd buffer).
   Copy (Dutch, direct): `Regen ~21:55 (±20 min). Ga vóór 21:40 naar Freedom — Anetha (energie 86).`

## 9. UI / views

Keep Bart's established recipe (§2.6). Views as top-level tabs:

1. **NU** (default during festival): current + next set per stage, sorted by score descending. Score shown as filled blocks `▮▮▮▮▯` + number. Pick marker where applicable. Rain banner above when active.
2. **Dag-schema** (Fri/Sat/Sun tabs): the familiar full timetable with all existing filters (stage chips, "toon vanaf" hour chips, picks-only), plus a new **energie-filter** chip (e.g. ≥70). Each set row shows its *static* score (dry assumption); during the festival the NU view carries the live scores.
3. **Weer**: next-2h precipitation timeline (simple text/blocks, no chart library) + hourly overview for the day.

Design notes: stay disciplined — the black/white 22px recipe *is* the visual identity; the one signature element is the score-blocks glyph. UI copy in Dutch, plain and imperative ("Ga vóór 21:40 naar…"). No decorative animation.

## 10. Testing

- `?now=2026-07-17T22:00` URL param overrides the clock (and selects matching weather slots from the forecast arrays) → full pre-festival dry-run of the NU view and rain advice.
- `?rain=demo` injects a synthetic rain event 30 min ahead to test the banner without waiting for weather.
- Acceptance: (1) opens and renders fully with network disabled after one prior load; (2) all three days render < 1 s on iPhone; (3) scores recompute when `?now=` changes; (4) rain demo produces a correct "move by" time; (5) picks from the source file are preserved 1:1.

## 11. Deployment

```
gh repo create tml-energy --public --clone
# add index.html (+ /source/tomorrowland-final2.html)
git add -A && git commit -m "TML W1 energy tool v1" && git push
gh api -X POST repos/{owner}/tml-energy/pages -f 'source[branch]=main' -f 'source[path]=/'
```
URL → Bart adds to iPhone homescreen via Safari share sheet. Iteration during the festival = edit + push; his phone gets the update on reload.

## 12. Implementation order

1. Parse `/source/tomorrowland-final2.html` → TIMETABLE JSON (verify counts: 3 days, 16 stages, 330+ acts, all picks).
2. STAGES table → present to Bart for verification of `cover` flags.
3. ARTISTS energy profiles → review table for Bart.
4. Scoring engine + unit-style sanity checks (a 23:00 Ben Klock set in a dark hall must outscore a 15:00 live act on an open XL stage).
5. Static UI (Dag-schema view) reusing the existing visual recipe.
6. Weather module + NU view + rain banner + `?now=`/`?rain=` simulators.
7. Deploy to Pages, test on iPhone Safari, tune CONFIG with Bart against his memory of past editions ("was the floor moving at set X?").

## 13. Open items (ask Bart)

- Confirm indoor/covered status per 2026 stage (he has been to TML; his knowledge beats guesses).
- Review artist energy table — his corrections calibrate the model.
- Whether he wants the PWA/service-worker phase-2 layer.
