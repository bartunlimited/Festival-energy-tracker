#!/usr/bin/env python3
"""Apply the updated official W1 timetable to index.html, carrying Bart's
picks + genres + energies from the previous verified data."""
import json, re, sys, unicodedata
from new_tt import NEW, NEW_INFO

IDX = "/home/user/Festival-energy-tracker/index.html"
old_recs = json.load(open("timetable.json"))  # old day numbering: 1=Fri..3=Sun
idx = open(IDX, encoding="utf-8").read()

# old ARTISTS {name: (energy, note)}
old_art = {}
art_block = re.search(r'const ARTISTS = \{(.*?)\n\};', idx, re.S).group(1)
for m in re.finditer(r'"((?:[^"\\]|\\.)*)": \{ energy:(\d+)(?:, note:"((?:[^"\\]|\\.)*)")? \}', art_block):
    old_art[m.group(1).replace('\\"','"')] = (int(m.group(2)), (m.group(3) or "").replace('\\"','"'))

def norm(s):
    s = s.replace("…", "...").strip()
    s = s[:-3].strip() if s.endswith("...") else s
    s = s.replace("ø","o").replace("Ø","O")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())

ALIAS = {"MAE.LIE": "MAE.LIEN"}
old_names = list(old_art.keys())
old_by_norm = {}
for n in old_names: old_by_norm.setdefault(norm(n), n)

def resolve(shown):
    if shown in ALIAS: return ALIAS[shown]
    if shown in old_art: return shown
    n = norm(shown)
    if n in old_by_norm: return old_by_norm[n]
    truncated = shown.replace("…","...").endswith("...")
    if truncated and n:
        cands = [o for o in old_names if norm(o).startswith(n) or n.startswith(norm(o))]
        if len(set(cands)) == 1: return cands[0]
        if cands:
            # prefer longest common; ambiguous -> keep shown
            print(f"  AMBIGU: {shown!r} -> {sorted(set(cands))}", file=sys.stderr)
    return shown.replace("…","...")

# old lookup: genre/pick per (old_day, artist) and per artist
by_day_art, by_art = {}, {}
for r in old_recs:
    by_day_art[(r["day"], r["artist"])] = r
    by_art.setdefault(r["artist"], r)

records, new_artists, unresolved = [], {}, []
for day, stage, start, end, shown in NEW:
    name = resolve(shown)
    old = by_day_art.get((day-1, name)) or by_art.get(name)
    if old:
        genre, pick = old["genre"], (by_day_art.get((day-1, name)) or {}).get("pick", old["pick"])
    elif name in NEW_INFO:
        genre, pick = NEW_INFO[name][0], ""
    else:
        genre, pick = "?", ""
        unresolved.append(name)
    records.append({"day":day, "stage":stage, "artist":name, "start":start, "end":end, "pick":pick, "genre":genre})

# merged artists: keep old entries still present, add new
present = {r["artist"] for r in records}
merged = {}
for a in sorted(present, key=str.lower):
    if a in old_art:
        merged[a] = old_art[a]
    elif a in NEW_INFO:
        merged[a] = (NEW_INFO[a][1], NEW_INFO[a][2])
    else:
        merged[a] = (50, "nieuw — check")

# ---- diff report ----
old_set = {(r["day"]+1, r["artist"], r["start"], r["stage"]) for r in old_recs}
new_set = {(r["day"], r["artist"], r["start"], r["stage"]) for r in records}
removed_artists = sorted({r["artist"] for r in old_recs} - present)
added_artists = sorted(present - {r["artist"] for r in old_recs})
moved = sorted(x for x in (new_set - old_set) if x[1] in {r["artist"] for r in old_recs} and x[0] > 1)
musts = sum(1 for r in records if r["pick"]=="must"); tips = sum(1 for r in records if r["pick"]=="rec")
old_musts = sum(1 for r in old_recs if r["pick"]=="must"); old_tips = sum(1 for r in old_recs if r["pick"]=="rec")
print(f"sets: {len(old_recs)} -> {len(records)} | musts {old_musts}->{musts} | tips {old_tips}->{tips}")
print(f"per dag: " + ", ".join(f"d{d}:{sum(1 for r in records if r['day']==d)}" for d in (1,2,3,4)))
print(f"nieuwe artiesten ({len(added_artists)}): {added_artists}")
print(f"verdwenen artiesten ({len(removed_artists)}): {removed_artists}")
print(f"verplaatste/gewijzigde sets van bestaande artiesten: {len(moved)}")
if unresolved: print("ONBEKEND zonder info:", unresolved)

# ---- emit JS ----
def js(v): return '"' + v.replace('\\','\\\\').replace('"','\\"') + '"'
tt = "\n".join(f'  {{day:{r["day"]}, stage:{js(r["stage"])}, artist:{js(r["artist"])}, start:"{r["start"]}", end:"{r["end"]}", pick:"{r["pick"]}", genre:{js(r["genre"])}}},' for r in records)
TIMETABLE_JS = (f"// Updated official W1 timetable ({len(records)} sets incl. The Gathering do 16/7),\n"
  "// transcribed from Bart's screenshots; picks/genres carried over from the\n"
  "// previous verified data by artist match.\n"
  "// Schema per set: {day, stage, artist, start, end, pick:\"must\"|\"rec\"|\"\", genre}\n"
  "// Times \"HH:MM\"; hours < 06:00 belong to the previous festival day.\n"
  "const TIMETABLE = [\n" + tt + "\n];")
arts = "\n".join(f'  {js(a)}: {{ energy:{e}{", note:"+js(n) if n else ""} }},' for a,(e,n) in merged.items())
ARTISTS_JS = ("// Heuristic energy 0-100 (genre intensity + set type + familiarity + reputation).\n"
  "const ARTISTS = {\n" + arts + "\n};")

# ---- patch index.html ----
idx = re.sub(r'const DAY_DATES = \{[^}]*\};',
  'const DAY_DATES = { 1:"2026-07-16", 2:"2026-07-17", 3:"2026-07-18", 4:"2026-07-19" };', idx)
idx = re.sub(r'const DAY_LABELS = \{[^}]*\};',
  'const DAY_LABELS = { 1:"Do 16", 2:"Vr 17", 3:"Za 18", 4:"Zo 19" };', idx)
idx = re.sub(r'// Extracted 1:1 from source/tomorrowland-final2\.html.*?const TIMETABLE = \[.*?\n\];', lambda m: TIMETABLE_JS, idx, flags=re.S)
idx = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', lambda m: ARTISTS_JS, idx, flags=re.S)

# add The Gathering stages (campsite, cover unverified)
idx = idx.replace('''  "house-of-fortune": { name:"House of Fortune", cover:"indoor",  size:"S",  dark:true,  verified:true },  // binnen, klein''',
'''  "house-of-fortune": { name:"House of Fortune", cover:"indoor",  size:"S",  dark:true,  verified:true },  // binnen, klein
  "the-gathering":    { name:"The Gathering",    cover:"open",    size:"L",  dark:false, verified:false },  // DreamVille, do 16/7
  "the-gathering-ii": { name:"Gathering II",     cover:"open",    size:"M",  dark:false, verified:false },  // DreamVille, do 16/7''', 1)

# generalize hardcoded day lists
idx = idx.replace("for(const d of [1,2,3]){", "for(const d of Object.keys(DAY_DATES).map(Number)){")
idx = idx.replace("const dayChips = [1,2,3].map(d=>", "const dayChips = Object.keys(DAY_DATES).map(Number).map(d=>")

# countdown text
idx = idx.replace("Vr 17 juli vanaf 12:00.`", "Do 16 juli (The Gathering) vanaf 14:00, hoofdterrein vanaf vr 17.`")

# tests: counts + day-shifted references
idx = idx.replace("ok(`368 sets geladen`, TIMETABLE.length===368);", f"ok(`{len(records)} sets geladen`, TIMETABLE.length==={len(records)});")
idx = idx.replace("ok(`19 musts / 101 tips`, TIMETABLE.filter(s=>s.pick===\"must\").length===19 && TIMETABLE.filter(s=>s.pick===\"rec\").length===101);",
  f"ok(`{musts} musts / {tips} tips`, TIMETABLE.filter(s=>s.pick===\"must\").length==={musts} && TIMETABLE.filter(s=>s.pick===\"rec\").length==={tips});")
idx = idx.replace('const openSet22 = TIMETABLE.find(s=>s.day===1 && STAGES[s.stage].cover==="open" && toMin(s.start)===22*60);',
                  'const openSet22 = TIMETABLE.find(s=>s.day===2 && STAGES[s.stage].cover==="open" && toMin(s.start)===22*60);')
# Guetta moved to day 3 (Sat) but tests use find-by-artist + fixed dates: fix dates
idx = idx.replace('const t2 = new Date("2026-07-18T23:45:00");', 'const t2 = new Date("2026-07-18T23:45:00");')

open(IDX, "w", encoding="utf-8").write(idx)
for frag in ["2026-07-16", "the-gathering", "Do 16"]:
    assert frag in idx, frag
print("\nindex.html bijgewerkt")
json.dump(records, open("timetable_new.json","w"), ensure_ascii=False, indent=1)
