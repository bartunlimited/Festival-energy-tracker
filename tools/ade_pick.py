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

Daarom: namen en gewichten komen uit het blok `artiesten` in bijlage §J van
het profiel, en een event zonder line-up wordt op zijn genretags beoordeeld en
apart gemarkeerd, zodat het opgezocht wordt in plaats van stil te verdwijnen.

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

# Genregewichten volgen de trefkans-tabel (§C) en de dislikes (deel 1, §F) in
# het profiel. Alleen de beste en de slechtste tag van een event tellen: als
# alle tags werden opgeteld, won een event met vijf brede tags en geen enkele
# naam van Eric Prydz in de Gashouder.
GENRE_WEIGHTS = {
    # techno: 79–81% trefkans
    "Techno": 3, "Hard Techno": 3, "Industrial Techno": 3, "Raw Techno": 3,
    "Peak Time Techno": 3, "Hypnotic Techno": 3, "Acid Techno": 3,
    "Detroit Techno": 3, "Hard Groove": 3,
    # melodic, trance, progressive: 50–58%
    "Melodic Techno": 2, "Melodic": 2, "Melodic House": 2, "Trance": 2,
    "Progressive": 2, "Progressive House": 2, "Progressive Trance": 2,
    "Uplifting Trance": 2, "Tech Trance": 2, "Hard Trance": 2,
    "Big Room House": 2, "Minimal-Techno": 2, "Elektro": 2, "Electro & Wave": 2,
    "Acid": 2, "Acid House": 2,
    # house: 26%
    "House": 1, "Deep House": 1, "Tech-house": 1, "Afro House": 1,
    "Chicago House": 1, "Disco House": 1, "Organic House": 1, "Minimal": 1,
    "Dub Techno": 1, "Ambient Techno": 1,
    # dislikes: experimenteel/ambient en dubstep
    "Ambient": -3, "Ambient & Listening": -3, "Deep Listening & Spatial Sound": -3,
    "Drone": -3, "IDM": -3, "Chillout": -3, "Downtempo": -3, "Dubstep": -3,
    # 0% trefkans: drum & bass / bass
    "Drum & Bass": -2, "Jungle": -2, "Neurofunk": -2, "Bass": -2, "Bass & UK": -2,
    # 3% trefkans: hardstyle / hard dance
    "Hard Dance": -2, "Hardstyle": -2, "Hardcore": -2, "Happy Hardcore": -2,
    # richting van de Honey Dijon-dislike: R&B-doordrenkte vocal house
    "Soulful House": -2, "R&B": -2,
}

# Locaties die in oktober afvallen: tent of buitenterrein. Zie muziek-dna.md §I.
OUTDOOR = ("thuishaven", "havenpark", "fik garden", "garden")

# ADE tagt buitenevents zelf; betrouwbaarder dan zaalnamen raden.
OUTDOOR_TAGS = {"Outdoor events", "Rooftop venues"}

# Geen dansvloer: conferentie, expo, winkel, borrel. Die scoren anders mee op
# hun genretags en dringen de lijst binnen.
NON_DANCEFLOOR = {
    "Music Culture", "Masterclasses", "Networking events", "Networking",
    "Workshops, Talks & Networking", "Keynotes, Talks & Panels", "Exhibitions",
    "Showcases & Expo's", "Instore Session", "Record Store Events",
    "Film & Documentaries", "Wellbeing", "Brunch, Bites & Beats", "Sports",
    "Sports & other activities", "Gear", "Labels, Publishing & Sync",
    "Meet the... Sessions", "Marketing & Media", "Business", "Brand demo",
    "ADE Startups", "ADE Pro", "Radio & Livestreams",
    # Pop-ups en winkels; LA ROCHE BOUTIQUE verkoopt merch van Indira Paganotto
    # en scoorde daardoor als haar optreden.
    "Lifestyle",
}

# Kinderraves hebben geen eigen tag; de titel zegt het wel.
NOT_FOR_HIM = re.compile(r"\b(kids?|family|familie)\b|\(\d+\+\)", re.I)

ORGANISATIONAL = {
    "Nighttime events", "Daytime events", "Evening starters", "Morning events",
    "Large venues", "Intimate venues", "Unique venues", "Warehouses",
    "Club nights", "All night long", "Events", "Free Events", "Live",
    "Live Performances", "DJ", "Producer", "Labels & Publishing",
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


ARTIST_BLOCK = re.compile(r"```artiesten\n(.*?)```", re.S)


def load_artists(path=PROFILE):
    """Lees namen en gewichten uit het blok `artiesten` in muziek-dna.md §J.

    Geeft (gewichten, afgewezen): {naam: 1|2|3} en een set namen die een event
    op nul zetten. Bewust een expliciete lijst: namen uit lopende tekst halen
    pakte "2025" en "Trefkans" als artiest en miste Charlotte de Witte.
    """
    text = nfc(path.read_text(encoding="utf-8"))
    m = ARTIST_BLOCK.search(text)
    if not m:
        raise SystemExit(f"FOUT: geen ```artiesten-blok in {path}")
    weights, rejected = {}, set()
    for n, line in enumerate(m.group(1).splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        w, _, name = (x.strip() for x in line.partition("|"))
        if not name:
            raise SystemExit(f"FOUT: artiestenlijst regel {n} onleesbaar: {line!r}")
        if w.lower() == "x":
            rejected.add(name)
        elif w in ("1", "2", "3"):
            weights[name] = int(w)
        else:
            raise SystemExit(f"FOUT: onbekend gewicht {w!r} bij {name!r}")
    return weights, rejected


def tags_of(event):
    # Van de eventpagina: schoon en volledig. Alleen als die er (nog) niet is,
    # terugvallen op het raden uit de kaarttekst.
    if event.get("tags"):
        return [t for t in event["tags"] if t not in ORGANISATIONAL]
    m = TAGS_RE.search(event.get("context", ""))
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(" / ") if t.strip() not in ORGANISATIONAL]


# "SPIELRAUM 55hrs", "The Final Stretch 30h", "8HRS Live": de duur in de titel.
TITLE_HOURS = re.compile(r"(?<![\w.])(\d{1,3})\s*(?:hrs?|hours?|h|uur)(?!\w)", re.I)


def span(event):
    day = event["date"].split(",")[0]
    base = datetime.fromisoformat(day)
    h, m = map(int, event["start"].split(":"))
    start = base.replace(hour=h, minute=m)
    h2, m2 = map(int, event["end"].split(":"))
    end = base.replace(hour=h2, minute=m2)
    if end <= start:
        end += timedelta(days=1)
    # Marathons: ADE geeft soms alleen een startslot op. SPIELRAUM 55hrs stond
    # als "23:00 - 00:00" en viel als event van één uur weg, met Rødhåd, JakoJako
    # en DVS1 in de line-up. Alleen corrigeren als het opgegeven tijdvak
    # onwaarschijnlijk kort is: "WAX 100H LIVE RADIO" staat als losse slots van
    # zes uur, en "The Final Stretch 30h" is het laatste deel van een reeks —
    # daar klopt het opgegeven slot en zou de titelduur het juist verpesten.
    m = TITLE_HOURS.search(event.get("title_full") or event["title"])
    if m and end - start < timedelta(hours=2) and int(m.group(1)) >= 2:
        end = start + timedelta(hours=int(m.group(1)))
        event["_duration_from_title"] = True
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


def _found(names, text):
    # (?<!\w) / (?!\w) in plaats van \b: werkt ook voor namen die met een
    # niet-woordteken eindigen of beginnen, en "Ben Klock" matcht niet in
    # "Ben Klockworks".
    return {a for a in names
            if re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", text, re.I)}


def score(event, artists):
    # Namen staan op drie plekken: de line-up op de eventpagina, de kaarttekst
    # op de lijst, en de beschrijving. Geen van drieën is volledig (Marcel
    # Dettmann staat bij Fabric alleen op de kaart en in de tekst), maar de
    # beschrijving noemt ook wie er níét speelt: "founded by Above & Beyond",
    # "we sell merchandise for … Indira Paganotto". Daarom telt een naam die
    # alléén in de beschrijving staat zwak mee, en wordt hij gemarkeerd.
    weights, rejected = artists
    lineup = " · ".join(a["name"] for a in event.get("lineup", []))
    strong = nfc(f"{event.get('title_full') or event['title']} {lineup} "
                 f"{event.get('context', '')}")
    weak = nfc(event.get("description", ""))
    # Afwijzing alleen op line-up, titel en kaart: een beschrijving die "in de
    # traditie van Dimitri Vegas" zegt is geen optreden van Dimitri Vegas.
    if _found(rejected, strong):
        return 0, [], [], False

    hard = _found(weights, strong)
    soft = _found(weights, weak) - hard
    names = sorted(hard) + sorted(f"{a}*" for a in soft)
    tags = tags_of(event)
    ws = [GENRE_WEIGHTS[t] for t in tags if t in GENRE_WEIGHTS]
    genre = max([w for w in ws if w > 0], default=0) + min([w for w in ws if w < 0], default=0)

    # Heeft de kaart überhaupt een line-up? ADE laat die vaak weg; dan is de
    # tekst vóór de tags niet veel meer dan de titel zelf.
    if "lineup" in event and not event.get("detail_stale"):
        # Eventpagina gelezen: naamloos betekent nu echt dat ADE geen artiesten
        # noemt, niet dat we ze niet hebben opgehaald.
        nameless = not event["lineup"]
    else:
        head = strong.split(tags[0])[0] if tags and tags[0] in strong else strong
        head = head.replace(event["title"], "").strip(" -·")
        nameless = len(head) < 12
    # Namen wegen zwaar (must = 9), tags hooguit +3: zijn smaak gaat voor het
    # genre-etiket van de organisator.
    return 3 * sum(weights[a] for a in hard) + len(soft) + genre, names, tags, nameless


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
    print(f"{len(artists[0])} namen uit het profiel · snapshot {data['fetched_at']} "
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
        if NOT_FOR_HIM.search(ev["title"]):
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
            slice_ = "" if (a == s and b == e) else f" →[{a:%a %H:%M}-{b:%a %H:%M}]"
            if ev.get("_duration_from_title"):
                slice_ += " ⚠duur uit titel"
            print(f" [{sc:3}] {s:%H:%M}-{e:%H:%M}{slice_} {(ev.get('title_full') or ev['title'])[:34]:34}"
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
                print(f" [{sc:3}] {s:%H:%M}-{e:%H:%M} {(ev.get('title_full') or ev['title'])[:34]:34}"
                      f"| {ev['venue'][:20]:20} {' / '.join(tags[:4])[:44]}")
        print()


if __name__ == "__main__":
    main()
