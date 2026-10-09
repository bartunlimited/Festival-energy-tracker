#!/usr/bin/env python3
"""Rangschik de ADE-snapshot tegen Barts profiel.

Waarom dit bestaat: de eerste selecties werden met de hand gemaakt tegen een
zelfgeschreven namenlijst. Dat ging twee keer mis op dezelfde manier:

1. Namen die wél in `docs/muziek-dna.md` staan maar niet in het lijstje
   (Eric Prydz, Paul Kalkbrenner, Kölsch, Benny Rodrigues) bleven onzichtbaar.
2. Kaarten die **geen enkele artiestennaam** bevatten — ADE toont dan alleen
   genretags — scoorden per definitie nul. Zo viel Ferry Corsten & Friends weg,
   en Awakenings Friday Sessions werd alleen gevonden omdat we er toevallig naar
   zochten.

Daarom: namen komen uit het profiel zelf, en een kaart zonder namen wordt op
zijn genretags beoordeeld en apart gemarkeerd, zodat hij opgezocht wordt in
plaats van stil te verdwijnen.

    python3 tools/ade_pick.py --window 8
    python3 tools/ade_pick.py --date 2026-10-23 --top 15
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "data" / "ade-2026" / "snapshot.json"
PROFILE = ROOT / "docs" / "muziek-dna.md"

# Outworld is het vaste punt waar de rustregel omheen gerekend wordt.
OUTWORLD = (datetime(2026, 10, 24, 23, 0), datetime(2026, 10, 25, 6, 0))

# Genregewichten volgen de trefkans-tabel in het profiel (bijlage §C).
GENRE_WEIGHTS = {
    "Hard Techno": 3, "Industrial Techno": 3, "Techno": 3,
    "Acid Techno": 2, "Melodic Techno": 2, "Melodic": 2,
    "Trance": 2, "Progressive": 2, "Minimal-Techno": 2, "Elektro": 2,
    "Big Room House": 1, "Deep House": 1, "House": 1, "Tech-house": 1,
    # Genres die hij niet danst; negatief zodat ze niet via de tags omhoog komen.
    "Hard Dance": -3, "Hardstyle": -3, "Bass": -2, "Drum & Bass": -2,
    "Dubstep": -3, "Psytrance": -2, "Ambient": -3, "Disco": 0,
}

# Locaties die in oktober afvallen: tent of buitenterrein. Zie muziek-dna.md §I.
OUTDOOR = ("thuishaven", "havenpark", "fik garden", "garden")

# ADE tagt buitenevents zelf; betrouwbaarder dan zaalnamen raden.
OUTDOOR_TAGS = {"Outdoor events", "Rooftop venues", "Boat venues"}

# Geen dansvloer: conferentie, expo, borrel. Die scoren anders mee op hun
# genretags en dringen de lijst binnen.
NON_DANCEFLOOR = {
    "Music Culture", "Masterclasses", "Networking events", "Conference",
    "Panel", "Workshop", "Talks", "Film", "Visual Arts", "Expo", "Exhibition",
    "Art", "Awards", "Markets", "Food", "Wellness", "Sports",
}

# Namen die het profiel expliciet afkeurt.
REJECTED = ("honey dijon", "horse meat disco", "angerfist")

ORGANISATIONAL = {
    "Nighttime events", "Daytime events", "Evening starters", "Morning events",
    "Large venues", "Intimate venues", "Unique venues", "Warehouses",
    "Club nights", "All night long", "Events", "Free Events", "Live",
    "Live Performances", "DJ", "Producer", "Labels & Publishing",
}

# Woorden die in het profiel vetgedrukt of in lijstjes staan maar geen artiest
# zijn. Zonder deze filter scoort elk event met de tag "Techno" als een match.
NOT_A_NAME = {
    "ade", "festival", "festivals", "mood", "bart", "claude", "crowd", "weer",
    "tent", "binnen", "buiten", "plus", "min", "techno", "house", "trance",
    "melodic", "melodic techno", "deep house", "tech house", "tech-house",
    "hard techno", "industrial techno", "acid techno", "progressive", "disco",
    "elektro", "minimal", "psytrance", "hardstyle", "dubstep", "bass", "ambient",
    "big room", "big room house", "edm", "mainstage", "vinyl", "live", "show",
    "energie", "factor", "effect", "pick", "picks", "must", "tip", "tips", "zomer", "oktober",
    "openstaand", "dislikes", "spotify", "halfweg", "awakenings", "milkshake",
    "tomorrowland", "drumcode", "intercell", "verknipt", "outworld", "tillatec",
}

TAGS_RE = re.compile(r"((?:[A-Za-z&\- ]+ / )+[A-Za-z&\- ]+)\s+[^·]{2,40}·")


def nfc(text):
    """Unicode gelijktrekken.

    De ADE-pagina levert gedecomponeerde tekens (o + los streepje) waar het
    profiel de samengestelde vorm heeft. Zonder normaliseren matcht "Rødhåd"
    op de ene kaart wel en op de andere niet — stil, en juist bij de namen die
    er het meest toe doen.
    """
    return unicodedata.normalize("NFC", text)


def load_artists(path=PROFILE):
    """Haal artiestennamen uit het profiel.

    Namen staan daar in `·`-lijstjes, in tabelkolommen en vetgedrukt. We pakken
    die drie vormen en gooien alles weg wat op lopende tekst lijkt, zodat de
    lijst meegroeit met het profiel in plaats van hier te verstenen.
    """
    text = nfc(path.read_text(encoding="utf-8"))
    cand = set()
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        cand.add(m.group(1))
    for line in text.splitlines():
        if line.startswith(("#", ">", "*Afgeleid")):
            continue
        line = re.sub(r"^[\s\-*+]+", "", line)
        # Ook op ":" splitsen, anders blijft een lijstkop aan de eerste naam
        # plakken ("Milkshake: Todd Terry").
        for part in re.split(r"·|\||,|:", line):
            cand.add(part)

    out = {}
    for c in cand:
        c = re.sub(r"[*_`]", "", c).strip(" .:—-")
        c = re.sub(r"\s*\(.*?\)\s*", " ", c).strip()
        if not (2 < len(c) <= 32) or " / " in c:
            continue
        if c in ORGANISATIONAL or c.lower() in REJECTED:
            continue
        if c.lower() in NOT_A_NAME or c.lower() in {g.lower() for g in GENRE_WEIGHTS}:
            continue
        # Lopende tekst eruit: te veel woorden, of woorden die geen naam zijn.
        words = c.split()
        if not 1 <= len(words) <= 4:
            continue
        if not re.match(r"^[A-ZÀ-ÿ0-9]", c):
            continue
        if re.search(r"\b(de|het|een|en|dat|die|niet|voor|zijn|wordt|is|van"
                     r"|bij|als|aan|met|uit|naar|maar|ook|per|geen)\b", c.lower()):
            continue
        out.setdefault(c.lower(), c)
    return sorted(out.values())


def tags_of(event):
    m = TAGS_RE.search(event.get("context", ""))
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(" / ") if t.strip() not in ORGANISATIONAL]


def span(event):
    day = event["date"].split(",")[0]
    base = datetime.fromisoformat(day)
    h, m = map(int, event["start"].split(":"))
    start = base.replace(hour=h, minute=m)
    h2, m2 = map(int, event["end"].split(":"))
    end = base.replace(hour=h2, minute=m2)
    if end <= start:
        end += timedelta(days=1)
    return start, end


def usable(start, end, block):
    """Het deel van een set dat buiten het rustvenster valt, plus de instaptijd.

    Hij hoeft er niet vanaf het begin bij te zijn, dus een event dat het venster
    raakt wordt afgeknipt in plaats van weggegooid.
    """
    b_start, b_end = block
    if end <= b_start or start >= b_end:
        return start, end
    if start < b_start:
        return start, b_start
    if end > b_end:
        return b_end, end
    return None, None


def score(event, artists):
    blob = nfc(f"{event['title']} {event.get('context', '')}")
    low = blob.lower()
    if any(r in low for r in REJECTED):
        return 0, [], [], False
    names = sorted({a for a in artists
                    if re.search(r"\b" + re.escape(a), blob, re.I)})
    tags = tags_of(event)
    genre = sum(GENRE_WEIGHTS.get(t, 0) for t in tags)

    # Heeft de kaart überhaupt een line-up? ADE laat die vaak weg; dan is de
    # tekst vóór de tags niet veel meer dan de titel zelf.
    head = blob.split(tags[0])[0] if tags and tags[0] in blob else blob
    head = head.replace(event["title"], "").strip(" -·")
    nameless = len(head) < 12
    return 3 * len(names) + genre, names, tags, nameless


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--window", type=float, default=8.0,
                    help="uren rust rond Outworld (standaard 8)")
    ap.add_argument("--min-hours", type=float, default=2.0,
                    help="minimaal bruikbaar deel buiten dat venster")
    ap.add_argument("--top", type=int, default=10, help="per dag tonen")
    ap.add_argument("--date", help="alleen deze dag (YYYY-MM-DD)")
    ap.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = ap.parse_args()

    data = json.loads(args.snapshot.read_text(encoding="utf-8"))
    artists = load_artists()
    block = (OUTWORLD[0] - timedelta(hours=args.window),
             OUTWORLD[1] + timedelta(hours=args.window))
    print(f"{len(artists)} namen uit het profiel · snapshot {data['fetched_at']} "
          f"· {data['count']} events", file=sys.stderr)
    print(f"geblokkeerd: {block[0]:%a %d %b %H:%M} → {block[1]:%a %d %b %H:%M}\n",
          file=sys.stderr)

    by_day = {}
    for ev in data["events"].values():
        if not ev.get("start") or not ev.get("venue"):
            continue
        if any(o in ev["venue"].lower() for o in OUTDOOR):
            continue
        ev_tags = tags_of(ev)
        if OUTDOOR_TAGS & set(ev_tags) or NON_DANCEFLOOR & set(ev_tags):
            continue
        try:
            start, end = span(ev)
        except ValueError:
            continue
        a, b = usable(start, end, block)
        if a is None or (b - a).total_seconds() / 3600 < args.min_hours:
            continue
        sc, names, tags, nameless = score(ev, artists)
        if sc <= 0:
            continue
        by_day.setdefault(ev["date"].split(",")[0], []).append(
            (sc, start, end, a, b, ev, names, tags, nameless))

    for day in sorted(by_day):
        if args.date and day != args.date:
            continue
        print(f"===== {datetime.fromisoformat(day):%A %d oktober} =====")
        rows = sorted(by_day[day], key=lambda r: -r[0])
        for sc, s, e, a, b, ev, names, tags, nameless in rows[:args.top]:
            slice_ = "" if (a == s and b == e) else f" →[{a:%H:%M}-{b:%H:%M}]"
            print(f" [{sc:3}] {s:%H:%M}-{e:%H:%M}{slice_} {ev['title'][:34]:34}"
                  f"| {ev['venue'][:20]:20}")
            if names:
                print(f"       {', '.join(names)[:100]}")
            elif tags:
                print(f"       tags: {' / '.join(tags[:5])[:70]}")

        # Kaarten zonder line-up kunnen nooit op namen scoren, dus ze zakken
        # altijd onder de afkapgrens. Apart tonen: dit is precies hoe Ferry
        # Corsten & Friends eerder onzichtbaar bleef.
        blind = [r for r in rows if r[8]][:args.top]
        if blind:
            print(" ── geen line-up op de kaart; zelf opzoeken ──")
            for sc, s, e, a, b, ev, names, tags, nameless in blind:
                print(f" [{sc:3}] {s:%H:%M}-{e:%H:%M} {ev['title'][:34]:34}"
                      f"| {ev['venue'][:20]:20} {' / '.join(tags[:4])[:44]}")
        print()


if __name__ == "__main__":
    main()
