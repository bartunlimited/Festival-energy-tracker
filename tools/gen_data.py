#!/usr/bin/env python3
"""Generate ARTISTS energy profiles + STAGES, splice DATA into index.html,
and emit a review table for Bart."""
import json, re

records = json.load(open("timetable.json"))

# ---------- genre intensity (0-40), §6 ----------
GENRE_RULES = [
    ("hard / industrial", 39), ("industrial", 38), ("hard / dark", 38),
    ("hard / fast", 39), ("hard / hypnotic", 38), ("psy / hard", 37),
    ("hard techno", 38), ("dark / hypnotic", 36), ("hypnotic", 35),
    ("dark melodic", 27), ("dark techno", 36),
    ("hardstyle / raw", 37), ("hardstyle / classics", 33), ("hardstyle", 36),
    ("acid / live techno", 36),
    ("techno / rave", 34), ("rave", 33),
    ("melodic techno", 25), ("minimal / melodic", 24),
    ("psytrance", 34),
    ("trance / techno", 32), ("trance", 30),
    ("drum & bass", 32),
    ("melodic dubstep", 22), ("dubstep", 26),
    ("tech / bass house", 30), ("bass house", 30), ("tech house", 31),
    ("afro / melodic", 23), ("afro house", 24), ("afro", 23),
    ("melodic / organic", 20), ("melodic / deep", 21), ("melodic house", 22),
    ("melodic edm", 24), ("melodic", 22),
    ("house / techno", 30), ("house / rave", 32), ("house / bass", 28),
    ("house / edm", 28), ("house / pop", 22), ("house / progressive", 26),
    ("edm / hardstyle", 33), ("edm / pop", 24), ("pop / edm", 24), ("edm", 28),
    ("house", 27), ("eclectic", 24),
    ("baile funk", 26), ("bass / melodic", 24), ("bass / electronic", 26),
    ("electronic / techno", 30), ("electronic / pop", 20), ("bass", 26),
    ("disco / retro", 22), ("retro / classics", 24),
    ("funk / soul", 16), ("reggae", 18), ("orkest / live", 8), ("pop", 18),
]

def genre_intensity(g):
    gl = g.lower()
    for key, v in GENRE_RULES:
        if key in gl:
            return v
    return 20  # unknown / "?"

# ---------- set type (0-15) ----------
def set_type(artist, genre):
    al, gl = artist.lower(), genre.lower()
    if "(live)" in al or "orkest" in gl:
        return 4
    if "(hybrid)" in al or "hybrid" in al:
        return 8
    return 13

# ---------- familiarity (0-20) ----------
def familiarity(genre):
    gl = genre.lower()
    if any(k in gl for k in ("hard", "hypnotic", "industrial", "psytrance", "dark")):
        return 16
    if "techno" in gl and "melodic" not in gl:
        return 15
    if any(k in gl for k in ("edm", "pop", "classics", "retro")):
        return 8
    if "eclectic" in gl:
        return 9
    return 11

# ---------- reputation overrides (0-25, default 12) ----------
REP = {
    # mainstage / EDM
    "Armin van Buuren": (22, "trance peak, proven mover"),
    "Martin Garrix": (20, "closing-level crowd control"),
    "David Guetta": (20, "hits but the whole field moves"),
    "Calvin Harris": (18, "hit machine"),
    "Hardwell b2b Sub Zero Project": (23, "big-room x hardstyle, explosive"),
    "Alesso": (16, ""), "Afrojack": (16, ""), "Steve Angello": (16, ""),
    "Sebastian Ingrosso": (16, ""), "Alok": (16, ""),
    "ALOK: Rave T...": (16, "afgekapte naam — check"),
    "Dimitri Vegas & Like Mike": (16, "crowd beweegt, Bart-dislike staat los van energie"),
    "Dimitri Vegas...": (14, "afgekapte naam — check"),
    "Steve Aoki": (14, "cake > dans"), "Nicky Romero": (14, ""), "R3hab": (14, ""),
    "Laidback Luke": (14, ""), "Will Sparks": (15, "melbourne bounce"),
    "The Chainsmokers": (14, ""), "Lost Frequencies": (14, "BE homecrowd"),
    "Henri PFR": (13, "BE"), "Bassjackers": (14, ""), "Blasterjaxx": (14, ""),
    "Gabry Ponte": (14, ""), "NERVO": (12, ""), "Kris Kross Am...": (14, "afgekapt — check"),
    # techno
    "Amelie Lens": (23, "BE techno queen, home crowd"),
    "Ben Klock": (20, "Berghain resident, pure floor"),
    "Anetha": (20, "relentless"), "I Hate Models": (20, "rave hysteria"),
    "Sara Landry": (22, "hard techno headliner"),
    "Indira Paganotto": (20, "psy-techno surge"),
    "Nico Moreno": (20, "industrial mosh"),
    "Reinier Zonneveld (live)": (21, "live acid marathon"),
    "999999999": (20, ""), "Space 92": (16, ""), "Maddix": (19, "techno-rave anthems"),
    "Hannah Laing": (16, ""), "Marlon Hoffstadt": (19, "DJ Daddy Trance hype"),
    "Kettama b2b Michael Bibi": (18, ""), "SHDW b2b ÜBERKIKZ": (16, ""),
    "Boris Brejcha": (18, "high-tech minimal show"), "Artbat": (16, ""),
    "Mind Against": (14, ""), "Kevin de Vries": (15, ""), "Agents Of Time": (14, ""),
    "Modeselektor (DJ-set)": (15, ""),
    # house / tech house
    "Fisher": (21, "circus, iedereen los"), "John Summit": (20, ""),
    "Vintage Culture": (17, ""), "Oliver Heldens": (16, ""),
    "Meduza³": (16, ""), "Franky Rizardo": (14, ""), "BLOND:ISH": (14, ""),
    "Morten b2b Malaa": (16, ""), "Malaa's Alter...": (15, "afgekapt — check"),
    "Avalon Emerson b2b Ben UFO": (16, "selectors, kenners-floor"),
    "Sasha b2b Young Marco": (14, ""), "Jazzy": (14, ""),
    "Chocolate Puma": (14, "BE/NL classic"), "Sam Feldt": (12, ""),
    # trance / psy
    "Vini Vici": (19, "psytrance mainstage proof"), "Neelix": (16, ""), "Push": (14, "BE trance legend"),
    # hardstyle
    "Da Tweekaz": (18, "party hardstyle"), "Sub Zero Project": (18, ""),
    "Rebelion": (16, ""), "Rooler": (16, ""), "DJ Ghost": (15, "BE cult"),
    "Pat B": (14, ""), "Da Capo b2b Caiiro b2b Enoo Napa": (15, ""),
    # dnb / bass
    "Chase & Status (DJ set)": (20, "dnb main-room pressure"),
    "Netsky": (18, "BE homecrowd"), "Camo & Krooked": (16, ""),
    "Subtronics": (16, "headbang crowd"), "Liquid Stranger": (14, ""),
    "Seven Lions": (14, ""), "Andromedik": (14, "BE"), "Murdock": (14, "BE dnb staple"),
    # misc
    "John Newman": (10, "zang, geen dansvloer"), "Gryffin": (12, ""),
    "Symphony Of Harmony": (8, "orkest — kijken, niet dansen"),
}

artists = {}
for r in records:
    a, g = r["artist"], r["genre"]
    if a in artists:
        continue
    gi = genre_intensity(g)
    st = set_type(a, g)
    fam = familiarity(g)
    rep, note = REP.get(a, (12, ""))
    if a.startswith("More to be") or a == "SURPRISE":
        e, note = 50, "TBA"
    else:
        e = max(0, min(100, gi + st + fam + rep))
    artists[a] = {"energy": e, "note": note, "_parts": (gi, st, fam, rep), "_genre": g}

# ---------- STAGES (2026 layout partly unverified -> verified:false) ----------
STAGES_JS = '''const STAGES = {
  "mainstage":        { name:"Mainstage",        cover:"open",    size:"XL", dark:false, verified:true  },
  "freedom":          { name:"Freedom",          cover:"indoor",  size:"L",  dark:true,  verified:true  },  // indoor hall, LED ceiling
  "atmosphere":       { name:"Atmosphere",       cover:"covered", size:"M",  dark:true,  verified:false },  // dome in eerdere edities
  "cage":             { name:"Cage",             cover:"covered", size:"M",  dark:true,  verified:false },
  "core":             { name:"CORE",             cover:"open",    size:"M",  dark:false, verified:true  },  // forest stage
  "crystal-garden":   { name:"Crystal Garden",   cover:"indoor",  size:"M",  dark:true,  verified:false },
  "celestia":         { name:"Celestia",         cover:"covered", size:"L",  dark:true,  verified:false },  // theaterzaal-stijl
  "melodia":          { name:"Melodia",          cover:"open",    size:"M",  dark:false, verified:false },
  "great-library":    { name:"Great Library",    cover:"indoor",  size:"S",  dark:true,  verified:false },
  "rave-cave":        { name:"Rave Cave",        cover:"covered", size:"S",  dark:true,  verified:true  },
  "rose-garden":      { name:"Rose Garden",      cover:"open",    size:"S",  dark:false, verified:false },
  "planaxis":         { name:"Planaxis",         cover:"open",    size:"M",  dark:false, verified:false },
  "elixir":           { name:"Elixir",           cover:"covered", size:"S",  dark:false, verified:false },
  "moose-bar":        { name:"Moose Bar",        cover:"covered", size:"M",  dark:true,  verified:true  },  // tent, altijd feest
  "house-of-fortune": { name:"House of Fortune", cover:"indoor",  size:"M",  dark:true,  verified:false },
};'''

def js_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

tt_lines = []
for r in records:
    tt_lines.append(
        f'  {{day:{r["day"]}, stage:{js_str(r["stage"])}, artist:{js_str(r["artist"])}, '
        f'start:"{r["start"]}", end:"{r["end"]}", pick:"{r["pick"]}", genre:{js_str(r["genre"])}}},')
TIMETABLE_JS = ("// Extracted 1:1 from source/tomorrowland-final2.html — "
                f"{len(records)} sets, picks preserved.\n"
                "// Schema per set: {day, stage, artist, start, end, pick:\"must\"|\"rec\"|\"\", genre}\n"
                "// Times \"HH:MM\"; hours < 06:00 belong to the previous festival day.\n"
                "const TIMETABLE = [\n" + "\n".join(tt_lines) + "\n];")

ar_lines = []
for a, v in sorted(artists.items(), key=lambda kv: kv[0].lower()):
    note = f', note:{js_str(v["note"])}' if v["note"] else ""
    ar_lines.append(f'  {js_str(a)}: {{ energy:{v["energy"]}{note} }},')
ARTISTS_JS = ("// Heuristic energy 0-100 (genre intensity + set type + familiarity + reputation).\n"
              "// Generated per design doc §6 — Bart calibrates via docs/artist-energy-review.md.\n"
              "const ARTISTS = {\n" + "\n".join(ar_lines) + "\n};")

# ---------- splice into index.html ----------
idx_path = "/home/user/Festival-energy-tracker/index.html"
idx = open(idx_path, encoding="utf-8").read()

idx = re.sub(r'const DEMO_DATA = true;', 'const DEMO_DATA = false;', idx)
idx = re.sub(r'// !!! DEMO DATA !!!.*?const DEMO_DATA', '// Real W1 timetable extracted from source/tomorrowland-final2.html.\nconst DEMO_DATA', idx, flags=re.S)
idx = re.sub(r'// Schema per set:.*?const TIMETABLE = \[.*?\n\];', TIMETABLE_JS, idx, flags=re.S)
idx = re.sub(r'// cover: indoor \| covered \| open.*?const STAGES = \{.*?\n\};',
             '// cover: indoor | covered | open · size XS-XL · dark: enclosed/dark inside\n'
             '// verified:false => 2026 layout not confirmed by Bart yet (shown with "?" badge)\n'
             + STAGES_JS, idx, flags=re.S)
idx = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', ARTISTS_JS, idx, flags=re.S)

open(idx_path, "w", encoding="utf-8").write(idx)
print(f"index.html updated: {len(records)} sets, {len(artists)} artists")

# sanity: file still contains exactly one TIMETABLE/ARTISTS/STAGES
for name in ("const TIMETABLE", "const ARTISTS", "const STAGES", "const CONFIG"):
    assert idx.count(name) == 1, name

# ---------- review table ----------
rows = []
for a, v in sorted(artists.items(), key=lambda kv: -kv[1]["energy"]):
    gi, st, fam, rep = v["_parts"]
    rows.append(f'| {a} | {v["_genre"]} | {v["energy"]} | {gi} | {st} | {fam} | {rep} | {v["note"]} |')
md = f"""# Artist energy review — Tomorrowland W1 2026

Heuristische energie-scores (0–100) voor alle {len(artists)} acts, gesorteerd hoog → laag.
Formule per design doc §6: **genre-intensiteit (0–40) + settype (0–15) + bekendheid (0–20) + reputatie (0–25)**.

Bart: corrigeer de kolom *energie* waar je het oneens bent (jouw geheugen van
eerdere edities is de kalibratie). Reputatie-default is 12; handmatige
overrides staan in de laatste kolom toegelicht.

| Artiest | Genre | **Energie** | Genre-int. | Settype | Bekendheid | Reputatie | Notitie |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"
open("/home/user/Festival-energy-tracker/docs/artist-energy-review.md", "w", encoding="utf-8").write(md)
print("wrote docs/artist-energy-review.md")

musts = [r for r in records if r["pick"] == "must"]
print(f"verify: {len(musts)} musts, sample: {[m['artist'] for m in musts[:5]]}")
