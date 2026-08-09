#!/usr/bin/env python3
"""Parse source/tomorrowland-final2.html -> TIMETABLE records + verification."""
import re, html, json, sys

SRC = "/home/user/Festival-energy-tracker/source/tomorrowland-final2.html"
raw = open(SRC, encoding="utf-8").read()

STAGE_SLUG = {
    "Mainstage": "mainstage", "Freedom": "freedom", "Atmosphere": "atmosphere",
    "Cage": "cage", "Core": "core", "Crystal Garden": "crystal-garden",
    "Celestia": "celestia", "Melodia": "melodia", "Great Library": "great-library",
    "Rave Cave": "rave-cave", "Rose Garden": "rose-garden", "Planaxis": "planaxis",
    "Elixir": "elixir", "Moose Bar": "moose-bar", "House of Fortune": "house-of-fortune",
}

# split into day sections
days = {}
for d in (1, 2, 3):
    m = re.search(rf'<div class="day" id="day{d}">(.*?)(?=<div class="day" id="day{d+1}">|</body>)', raw, re.S)
    if not m:
        sys.exit(f"day{d} section not found")
    days[d] = m.group(1)

card_re = re.compile(
    r'<div class="card (must|rec|none) h(\d+) s(\d+)">\s*'
    r'<div class="ct"><span class="a">(.*?)</span>(?:<span class="bdg[^>]*>.*?</span>)?</div>\s*'
    r'<div class="cm"><span class="tm">(.*?)</span><span class="st">(.*?)</span></div>\s*'
    r'<div class="gm"><span class="g">(.*?)</span></div>', re.S)

def clean(s):
    s = html.unescape(s)
    s = re.sub(r'^[\U0001F534\U0001F7E0]\s*', '', s)  # strip pick emoji prefix
    return re.sub(r'\s+', ' ', s).strip()

records, problems = [], []
for d, chunk in days.items():
    for m in card_re.finditer(chunk):
        pick_cls, hcls, scls, artist, tm, stage_name, genre = m.groups()
        artist, tm, stage_name, genre = clean(artist), clean(tm), clean(stage_name), clean(genre)
        t = re.match(r'^(\d{1,2}:\d{2})[–-](\d{1,2}:\d{2})$', tm.replace('–', '-'))
        if not t:
            problems.append(f"bad time '{tm}' for {artist}"); continue
        slug = STAGE_SLUG.get(stage_name)
        if not slug:
            problems.append(f"unknown stage '{stage_name}' for {artist}"); continue
        records.append({
            "day": d, "stage": slug, "artist": artist,
            "start": t.group(1).zfill(5), "end": t.group(2).zfill(5),
            "pick": {"must": "must", "rec": "rec", "none": ""}[pick_cls],
            "genre": genre,
        })

total_cards = len(re.findall(r'<div class="card ', raw))
musts = sum(1 for r in records if r["pick"] == "must")
recs = sum(1 for r in records if r["pick"] == "rec")
src_musts = raw.count('class="card must')
src_recs = raw.count('class="card rec')
stages_seen = sorted({r["stage"] for r in records})

print(f"cards in source: {total_cards}, parsed: {len(records)}")
print(f"musts: parsed {musts} / source {src_musts}   tips: parsed {recs} / source {src_recs}")
print(f"days: {sorted({r['day'] for r in records})}, stages: {len(stages_seen)}")
for p in problems: print("PROBLEM:", p)
assert len(records) == total_cards and musts == src_musts and recs == src_recs and not problems

json.dump(records, open("timetable.json", "w"), ensure_ascii=False, indent=1)
print("wrote timetable.json")

# distinct artists with their genres, for the energy pass
artists = {}
for r in records:
    artists.setdefault(r["artist"], set()).add(r["genre"])
print(f"distinct artists: {len(artists)}")
with open("artists_raw.txt", "w") as f:
    for a in sorted(artists):
        f.write(f"{a}\t{' | '.join(sorted(artists[a]))}\n")
