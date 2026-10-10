#!/usr/bin/env python3
"""ade_watch.py — scrape de ADE-programmapagina en meld wat er veranderd is.

    python3 tools/ade_watch.py                # scrapen + diffen tegen de snapshot
    python3 tools/ade_watch.py --save         # idem, en de nieuwe snapshot wegschrijven
    python3 tools/ade_watch.py --render       # via Playwright renderen (JS-pagina's)
    python3 tools/ade_watch.py --dump out.html   # ruwe HTML bewaren om selectors te fixen

Exit codes: 0 = niets veranderd · 1 = wijzigingen gevonden · 2 = fout of 0 events.
Zo kun je hem in cron of GitHub Actions hangen en op exit 1 laten alarmeren.
"""
import argparse, json, os, re, subprocess, sys, time, traceback, unicodedata, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from html import unescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "ade-2026")
SNAPSHOT = os.path.join(DATA_DIR, "snapshot.json")

DEFAULT_URL = (
    "https://www.amsterdam-dance-event.nl/en/program/filter/"
    "?section=events&type=8262%2C8263&from=2026-10-21&to=2026-10-25"
)
UA = "festival-energy-tracker/1.0 (persoonlijke ADE-agenda; contact via GitHub)"

# Detailpagina's hebben de vorm /en/program/2026/<slug>/<id>/ — dat id is de sleutel.
EVENT_HREF = re.compile(
    r'href=["\'](?P<url>(?:https?://[^"\']*?)?/(?:en|nl)/program/'
    r'(?P<year>\d{4})/(?P<slug>[^/"\'\s]+)/(?P<id>\d+)/?)["\']',
    re.I,
)
LD_JSON = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I
)


# ---------------------------------------------------------------- ophalen

def safe_url(url):
    """Niet-ASCII in een URL percent-coderen.

    Slugs kunnen emoji en andere tekens bevatten ("…batter-my-️-3-personed-g0d",
    "cosmic-navigation-๑-…"); urllib weigert die in de request-regel en gooit
    een UnicodeEncodeError in plaats van de pagina op te halen.
    """
    return urllib.parse.quote(url, safe=":/?&=%#+@,;~")


def fetch(url, tries=4):
    """GET met retry-backoff. Geen Accept-Encoding, dan komt het onverpakt binnen."""
    url = safe_url(url)
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en,nl;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
    raise SystemExit(f"FOUT: {url} niet op te halen — {last}")


def fetch_rendered(url):
    """Zelfde, maar door een echte browser. Vereist de Node-helper ernaast."""
    helper = os.path.join(ROOT, "tools", "ade_render.mjs")
    if not os.path.exists(helper):
        raise SystemExit(f"FOUT: {helper} ontbreekt (nodig voor --render)")
    env = dict(os.environ)
    env.setdefault("NODE_PATH", "/opt/node22/lib/node_modules")
    p = subprocess.run(["node", helper, url], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise SystemExit(f"FOUT: renderen mislukt —\n{p.stderr.strip()}")
    return p.stdout


# ---------------------------------------------------------------- parsen

def strip_tags(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(html)).strip()


def abs_url(href):
    if href.startswith("http"):
        return href
    return "https://www.amsterdam-dance-event.nl" + href


def title_from_slug(slug):
    return unescape(slug.replace("-", " ")).strip().title()


def slugify(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


# De kaarttekst is één blob: titel, genretags, zaal en tijden aan elkaar geplakt.
# "… Acid / Techno / Trance Ziggo Dome · 23:00 - 06:00 Ziggo Dome"
# De zaal staat er dus twee keer in. Die ná de tijden is de schone: daar loopt
# geen genretag tegenaan. Die vóór de punt is de reserve, want tussen de laatste
# tag en de zaalnaam staat geen scheidingsteken ("… / Trance Ziggo Dome").
CARD_AFTER = re.compile(
    r"(?P<start>\d{1,2}:\d{2})\s*-\s*(?P<end>\d{1,2}:\d{2})\s+(?P<venue>[^<]{2,60}?)\s*$"
)
CARD_BEFORE = re.compile(
    r"(?P<venue>[^·]{2,80}?)\s*·\s*(?P<start>\d{1,2}:\d{2})\s*-\s*(?P<end>\d{1,2}:\d{2})"
)


def split_card(text, slug):
    """Haal titel, zaal en tijden uit de kaarttekst.

    De titel knippen we af met behulp van de slug uit de URL: we schuiven woord
    voor woord op zolang de geslugificeerde tekst nog een begin van die slug is.
    Zo weten we waar de titel ophoudt en de genretags beginnen, zonder te moeten
    raden hoe die tags eruitzien.
    """
    out = {"title": "", "venue": "", "start": "", "end": ""}

    before, after = CARD_BEFORE.search(text), CARD_AFTER.search(text)
    if before or after:
        m = before or after
        out["start"], out["end"] = m.group("start"), m.group("end")

        # Beide vindplaatsen combineren. Vóór de punt staat de zaalnaam compleet
        # maar met de laatste genretag ertegenaan; ná de tijden staat hij schoon
        # maar soms afgekapt. Het beste van beide: zoek in het volledige stuk
        # waar het schone stuk begint, en neem alles vanaf daar.
        head = before.group("venue").strip(" ·-") if before else ""
        tail = after.group("venue").strip(" ·-") if after else ""
        venue = head or tail
        if head and tail:
            at = head.rfind(tail)
            venue = head[at:] if at > 0 else (head if len(head) < len(tail) else tail)
        out["venue"] = venue.split(" / ")[-1].strip(" ·-")

    words, acc, best = text.split(), [], ""
    for w in words:
        acc.append(w)
        if slug.startswith(slugify(" ".join(acc))):
            best = " ".join(acc)
        else:
            break
    out["title"] = best or title_from_slug(slug)
    return out


def parse_jsonld(html):
    """Voorkeursroute: als de pagina Event-objecten meelevert, zijn die betrouwbaar."""
    found = {}
    for block in LD_JSON.findall(html):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
            types = node.get("@type", "")
            types = types if isinstance(types, list) else [types]
            if not any("Event" in str(t) for t in types):
                continue
            url = str(node.get("url") or "")
            m = re.search(r"/(\d+)/?$", url)
            if not m:
                continue
            loc = node.get("location") or {}
            if isinstance(loc, list):
                loc = loc[0] if loc else {}
            venue = loc.get("name") if isinstance(loc, dict) else str(loc)
            found[m.group(1)] = {
                "id": m.group(1),
                "title": str(node.get("name") or "").strip(),
                "url": abs_url(url),
                "start": str(node.get("startDate") or ""),
                "end": str(node.get("endDate") or ""),
                "venue": str(venue or "").strip(),
                "source": "jsonld",
            }
    return found


def parse_anchors(html):
    """Fallback: elke link naar een detailpagina is een event.

    Titel uit de linktekst, en een stuk omliggende tekst als vingerafdruk — die
    labelt datum en zaal niet, maar verandert er wél in mee, dus een wijziging
    valt alsnog op.
    """
    found = {}
    for m in EVENT_HREF.finditer(html):
        eid = m.group("id")
        if eid in found:
            continue
        # m.end() staat op het slotquote van href; door naar het eind van de <a>-tag.
        open_tag_end = html.find(">", m.end())
        body = html[open_tag_end + 1:] if open_tag_end != -1 else html[m.end():]
        close = body.find("</a>")
        label = strip_tags(body[:close]) if close != -1 else ""
        # Context loopt tot de volgende event-link, zodat een buur-event er niet
        # in meelekt — anders meldt elke wijziging ook zijn buren als gewijzigd.
        ctx_from = open_tag_end + 1 if open_tag_end != -1 else m.end()
        nxt = EVENT_HREF.search(html, m.end())
        stop = min(nxt.start() if nxt else len(html), ctx_from + 1200)
        context = strip_tags(html[ctx_from:stop])[:500]
        card = split_card(label or context, m.group("slug"))
        found[eid] = {
            "id": eid,
            "url": abs_url(m.group("url")),
            "slug": m.group("slug"),
            "context": context,
            "source": "anchor",
            **card,
        }
    return found


def parse(html):
    events = parse_jsonld(html)
    for eid, ev in parse_anchors(html).items():
        if eid in events:
            events[eid].setdefault("context", ev.get("context", ""))
            events[eid].setdefault("slug", ev.get("slug", ""))
        else:
            events[eid] = ev
    return events


def scrape(url, render=False, max_pages=40, dump=None):
    """Loop de paginering af tot er geen nieuwe id's meer bijkomen."""
    all_events, pages, raw = {}, 0, []
    for page in range(1, max_pages + 1):
        page_url = url if page == 1 else f"{url}{'&' if '?' in url else '?'}page={page}"
        try:
            html = fetch_rendered(page_url) if render else fetch(page_url)
        except SystemExit:
            if page == 1:
                raise  # pagina 1 moet het doen; verderop is het gewoon het einde
            print(f"  pagina {page}: niet beschikbaar — einde", file=sys.stderr)
            break
        raw.append(html)
        pages += 1
        batch = parse(html)
        new = {k: v for k, v in batch.items() if k not in all_events}
        print(f"  pagina {page}: {len(batch)} events, {len(new)} nieuw", file=sys.stderr)
        all_events.update(new)
        if not new:
            break
        time.sleep(1)  # niet rammen
    if dump:
        with open(dump, "w", encoding="utf-8") as f:
            f.write("\n<!-- ===== volgende pagina ===== -->\n".join(raw))
        print(f"  ruwe HTML → {dump}", file=sys.stderr)
    return all_events, pages


# ---------------------------------------------------------------- diffen

def day_urls(url):
    """Splits een from/to-bereik in losse dagen.

    De kaarten noemen wel een tijd maar geen datum; door per dag te filteren
    weten we alsnog op welke dag elk event valt.
    """
    from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
    from datetime import date, timedelta

    p = urlparse(url)
    q = parse_qs(p.query)
    first, last = q.get("from", [None])[0], q.get("to", [None])[0]
    if not first or not last:
        return [(None, url)]
    try:
        d, end = date.fromisoformat(first), date.fromisoformat(last)
    except ValueError:
        return [(None, url)]
    out = []
    while d <= end:
        q2 = dict(q, **{"from": [d.isoformat()], "to": [d.isoformat()]})
        out.append((d.isoformat(), urlunparse(p._replace(query=urlencode(q2, doseq=True)))))
        d += timedelta(days=1)
    return out


# ---------------------------------------------------------------- eventpagina's
#
# De programmalijst toont per event alleen een kaart: titel, tags, zaal, tijd —
# en bij 37% van de kaarten geen enkele artiest. De line-up staat op de eigen
# eventpagina, en die wordt server-side gerenderd, dus gewone requests volstaan.
# Opmaak (okt 2026):
#   <a href=".../artists-speakers/<slug>/<id>/" class="link link__line-up …">Naam (NL)</a>
#   <div class="ade-info-bar__item"><h2 …>Date</h2> … data-date">Fri, Oct 23, 2026</span><br/> 16:00 - 22:30
#   <div class="ade-info-bar__item"><h2 …>Location</h2> … /venues/<slug>/<id>/">Zaal</a> | <a …>Adres</a>
#   <div class="ade-info-bar__item"><h2 …>Interests</h2> … category=<id>…">Techno</a> / …

A_TAG = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.S | re.I)
LINEUP_BLOCK = re.compile(
    r"<h3[^>]*>\s*Line-up\s*</h3>\s*<p[^>]*>(.*?)</p>", re.S | re.I)
HREF = re.compile(r'href="([^"]+)"')
ARTIST_URL = re.compile(r"/artists-speakers/([^/]+)/(\d+)/?")
VENUE_URL = re.compile(r"/venues/([^/]+)/(\d+)/?")
NAME_COUNTRY = re.compile(r"^(.*?)\s*\(([A-Z]{2,3})\)\s*$")
TIME_RANGE = re.compile(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})")
DESCRIPTION = re.compile(
    r'<h2 class="ade-h2 ade-mbottom\s*">.*?</h2>\s*<div class="ade-text">(.*?)</div>', re.S
)


def _text(fragment):
    return unicodedata.normalize("NFC", strip_tags(fragment))


def parse_detail(html):
    """Haal line-up, datum, tijd, zaal, adres en tags uit een eventpagina."""
    out = {"lineup": [], "tags": []}

    # Het line-upblok is één alinea na de kop "Line-up", met namen gescheiden
    # door " / ". Niet alleen de links lezen: een artiest zonder ADE-pagina
    # staat er als platte tekst tussen en zou anders onzichtbaar zijn.
    block = LINEUP_BLOCK.search(html)
    out["lineup_heading"] = bool(block)
    linked = {}
    for attrs, inner in A_TAG.findall(block.group(1) if block else html):
        if "link__line-up" not in attrs:
            continue
        href = (HREF.search(attrs) or [None, ""])[1]
        am = ARTIST_URL.search(href)
        linked[_text(inner)] = am.group(2) if am else ""
    labels = ([x.strip() for x in _text(block.group(1)).split(" / ") if x.strip()]
              if block else list(linked))
    for label in labels:
        m = NAME_COUNTRY.match(label)
        name, country = (m.group(1), m.group(2)) if m else (label, "")
        out["lineup"].append({"name": name, "country": country,
                              "artist_id": linked.get(label, "")})

    # De info-balk bestaat uit blokken met een kop; op de kop splitsen is
    # robuuster dan op volgorde vertrouwen.
    for block in html.split('class="ade-info-bar__item"')[1:]:
        head = re.search(r"<h2[^>]*>(.*?)</h2>", block, re.S)
        if not head:
            continue
        key = _text(head.group(1)).lower()
        body = block[head.end():]
        if key == "date":
            d = re.search(r'data-date">([^<]+)<', body)
            if d:
                out["date_label"] = d.group(1).strip()
                try:
                    out["date_iso"] = datetime.strptime(
                        out["date_label"], "%a, %b %d, %Y").date().isoformat()
                except ValueError:
                    pass
            t = TIME_RANGE.search(_text(body[:600]))
            if t:
                out["start"], out["end"] = t.group(1), t.group(2)
        elif key == "location":
            links = A_TAG.findall(body[:1500])
            for attrs, inner in links:
                href = (HREF.search(attrs) or [None, ""])[1]
                vm = VENUE_URL.search(href)
                if vm and "venue" not in out:
                    out["venue"] = _text(inner)
                    out["venue_id"] = vm.group(2)
                elif "google.com/maps" in href:
                    out["address"] = _text(inner)
        elif key == "interests":
            for attrs, inner in A_TAG.findall(body[:4000]):
                if "category=" in attrs:
                    out["tags"].append(_text(inner))

    # De volledige titel. Op de lijst wordt hij uit de kaart geraden en raakt
    # hij soms afgekapt ("DGTL |", "IPSO by", "Dave").
    t = re.search(r'<h1 class="[^"]*ade-events-entry__title[^"]*">(.*?)</h1>', html, re.S)
    if t:
        out["title_full"] = _text(t.group(1))

    d = DESCRIPTION.search(html)
    if d:
        # Ruim bewaren: namen staan soms alleen hier. Marcel Dettmann wordt bij
        # Fabric x Loud Contact wel in de tekst genoemd, maar niet gelinkt.
        out["description"] = _text(d.group(1))[:2000]
    return out


def fetch_quiet(url, tries=3):
    """Zoals fetch(), maar geeft None in plaats van het proces te stoppen:
    één onbereikbare eventpagina mag de hele run niet slopen."""
    try:
        return fetch(url, tries=tries)
    except (SystemExit, Exception) as e:  # noqa: BLE001 — bewust breed
        # Breed afvangen: één rare URL nam eerder de hele run mee, omdat hier
        # alleen SystemExit werd gevangen en een UnicodeEncodeError doorschoot.
        print(f"  eventpagina mislukt: {url} — {type(e).__name__}: {e}", file=sys.stderr)
        return None


def enrich(events, old, workers=6):
    """Haal van elk event de eventpagina op en voeg de details toe.

    Lukt een pagina niet, dan nemen we de details van de vorige snapshot over
    en markeren ze als verouderd. Anders verschijnt een tijdelijke netwerkfout
    in de diff als een line-up die is leeggehaald.
    """
    from concurrent.futures import ThreadPoolExecutor

    def one(item):
        eid, ev = item
        html = fetch_quiet(ev["url"])
        return eid, (parse_detail(html) if html else None)

    ok = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for eid, det in pool.map(one, list(events.items())):
            ev = events[eid]
            if det is None:
                failed += 1
                prev = old.get(eid, {})
                for k in ("lineup", "lineup_names", "lineup_heading", "tags", "address",
                          "venue_id", "description", "title_full"):
                    if k in prev:
                        ev[k] = prev[k]
                ev["detail_stale"] = True
                continue
            ok += 1
            ev.pop("detail_stale", None)
            ev["lineup"] = det["lineup"]
            ev["lineup_heading"] = det.get("lineup_heading", False)
            ev["lineup_names"] = " · ".join(sorted(a["name"] for a in det["lineup"]))
            ev["tags"] = det["tags"]
            for k in ("address", "venue_id", "description", "title_full"):
                if det.get(k):
                    ev[k] = det[k]
            # De eventpagina is de bron; de kaart op de lijst was een benadering.
            for k in ("venue", "start", "end"):
                if det.get(k):
                    ev[k] = det[k]
    print(f"Eventpagina's: {ok} gelezen, {failed} mislukt", file=sys.stderr)
    return ok, failed


DIFF_FIELDS = ("title", "date", "url", "start", "end", "venue", "lineup_names")


def fields_for(event):
    """Met structured data diffen we op schone velden; zonder is de ruwe
    contexttekst de enige vingerafdruk die we hebben."""
    if event.get("start") or event.get("venue"):
        return DIFF_FIELDS
    return DIFF_FIELDS + ("context",)


def diff(old, new):
    added = [new[k] for k in new if k not in old]
    removed = [old[k] for k in old if k not in new]
    changed = []
    for k in new:
        if k not in old:
            continue
        deltas = {
            f: (old[k].get(f, ""), new[k].get(f, ""))
            for f in fields_for(new[k])
            if old[k].get(f, "") != new[k].get(f, "")
            # De eerste keer dat we eventpagina's lezen is geen wijziging van
            # de line-up; zonder deze uitzondering zou elk event "gewijzigd" zijn.
            and not (f == "lineup_names" and "lineup_names" not in old[k])
        }
        if deltas:
            changed.append((new[k], deltas))
    return added, removed, changed


def report(added, removed, changed):
    lines = []
    if added:
        lines.append(f"### ➕ Nieuw ({len(added)})")
        lines += [f"- **{e['title']}** — {e['url']}" for e in sorted(added, key=lambda e: e["title"])]
    if removed:
        lines.append(f"### ➖ Verdwenen ({len(removed)})")
        lines += [f"- **{e['title']}** — {e['url']}" for e in sorted(removed, key=lambda e: e["title"])]
    if changed:
        lines.append(f"### ✏️ Gewijzigd ({len(changed)})")
        for ev, deltas in sorted(changed, key=lambda c: c[0]["title"]):
            lines.append(f"- **{ev['title']}** — {ev['url']}")
            for field, (was, now) in deltas.items():
                if field == "lineup_names":
                    a = set(filter(None, was.split(" · ")))
                    b = set(filter(None, now.split(" · ")))
                    if b - a:
                        lines.append(f"    - line-up **+** {', '.join(sorted(b - a))}")
                    if a - b:
                        lines.append(f"    - line-up **−** {', '.join(sorted(a - b))}")
                    continue
                lines.append(f"    - `{field}`: {was!r} → {now!r}")
    return "\n".join(lines)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Scrape het ADE-programma en meld wijzigingen.")
    ap.add_argument("--url", default=DEFAULT_URL, help="filter-URL (default: ADE 2026, 21–25 okt)")
    ap.add_argument("--save", action="store_true", help="snapshot en changelog bijwerken")
    ap.add_argument("--render", action="store_true", help="via Playwright renderen")
    ap.add_argument("--dump", metavar="BESTAND", help="ruwe HTML wegschrijven")
    ap.add_argument("--snapshot", default=SNAPSHOT, help="pad naar de snapshot")
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument("--max-shrink", type=float, default=0.10,
                    help="krimp t.o.v. de vorige snapshot die nog acceptabel is "
                         "(0.10 = 10%%); daarboven wordt niet weggeschreven")
    ap.add_argument("--details", action="store_true",
                    help="ook elke eventpagina ophalen (line-up, adres, tags)")
    ap.add_argument("--workers", type=int, default=6,
                    help="gelijktijdige requests voor --details")
    ap.add_argument("--split-days", action="store_true",
                    help="per dag scrapen zodat elk event een datum krijgt")
    ap.add_argument("--json", action="store_true", help="diff als JSON naar stdout")
    args = ap.parse_args()

    def scrape_all(url):
        got, pages = scrape(url, args.render, args.max_pages, args.dump)
        # De programmalijst laadt via JavaScript: statisch levert 0 events op.
        # Val dan vanzelf terug op de browser in plaats van de gebruiker een
        # vlag te laten opzoeken.
        if not got and not args.render:
            print("  statisch 0 events — opnieuw met een echte browser…", file=sys.stderr)
            try:
                got, pages = scrape(url, True, args.max_pages, args.dump)
            except SystemExit as e:
                print(f"  renderen lukte niet: {e}", file=sys.stderr)
        return got

    print(f"Ophalen: {args.url}", file=sys.stderr)

    # Hoeveel events had de vorige snapshot per dag? Daarmee kunnen we zien of
    # een dagpagina deze keer te weinig opleverde.
    prev_per_day = {}
    if os.path.exists(args.snapshot):
        with open(args.snapshot, encoding="utf-8") as f:
            for ev in json.load(f).get("events", {}).values():
                for day in (ev.get("date") or "").split(","):
                    if day:
                        prev_per_day[day] = prev_per_day.get(day, 0) + 1

    events = {}
    for day, day_url in (day_urls(args.url) if args.split_days else [(None, args.url)]):
        if day:
            print(f"— {day}", file=sys.stderr)

        # Lazy loading valt soms op één dagpagina te vroeg stil. Dat is puur
        # verlies: twee runs verschilden 39 events, allemaal op dezelfde dag, en
        # de kleinere was een strikte deelverzameling van de grotere. Dus: nog
        # eens proberen zolang de dag minder oplevert dan de vorige snapshot, en
        # de pogingen samenvoegen in plaats van de laatste te geloven.
        got = {}
        for attempt in range(1, 4):
            batch = scrape_all(day_url)
            got.update(batch)
            target = prev_per_day.get(day or "", 0)
            if len(got) >= target or attempt == 3:
                if target and len(got) < target:
                    print(f"  let op: {len(got)} events, vorige keer {target}",
                          file=sys.stderr)
                break
            print(f"  {len(got)} events, vorige keer {target} — poging "
                  f"{attempt + 1}", file=sys.stderr)

        for eid, ev in got.items():
            if eid in events:
                # Meerdaags event: alle dagen bewaren, niet overschrijven.
                seen = events[eid].get("date", "")
                if day and day not in seen.split(","):
                    events[eid]["date"] = f"{seen},{day}".strip(",")
            else:
                ev["date"] = day or ""
                events[eid] = ev
        if day:
            print(f"  {len(got)} events", file=sys.stderr)

    print(f"Totaal: {len(events)} events", file=sys.stderr)

    if not events:
        print(
            "\nFOUT: 0 events gevonden. Waarschijnlijk rendert de pagina via JavaScript,\n"
            "of de markup is veranderd. Probeer:\n"
            "  python3 tools/ade_watch.py --render\n"
            "  python3 tools/ade_watch.py --dump /tmp/ade.html   (en kijk in de HTML)",
            file=sys.stderr,
        )
        return 2

    old = {}
    if os.path.exists(args.snapshot):
        with open(args.snapshot, encoding="utf-8") as f:
            old = json.load(f).get("events", {})
    first_run = not old

    # Vangnet tegen een stil afgekapte scrape. De programmalijst laadt lazy; als
    # het laden halverwege stilvalt krijg je een kleinere lijst die er in de diff
    # uitziet als massaal geannuleerde events. Dat is één keer gebeurd (1246 →
    # 1197, met 159 "verdwenen" events die gewoon niet geladen waren), dus een
    # forse krimp is reden om níét weg te schrijven.
    if old and len(events) < len(old) * (1 - args.max_shrink):
        print(
            f"\nFOUT: {len(events)} events tegen {len(old)} in de vorige snapshot "
            f"({(1 - len(events) / len(old)) * 100:.0f}% minder).\n"
            "Dat is vrijwel zeker een afgekapte scrape, geen afgelaste events.\n"
            "Snapshot NIET bijgewerkt. Draai opnieuw, of forceer met "
            "--max-shrink 1.0 als de krimp echt klopt.",
            file=sys.stderr,
        )
        return 2

    if args.details:
        ok, failed = enrich(events, old, workers=args.workers)
        # Lukt een flink deel niet, dan is de site of het netwerk de oorzaak,
        # niet ADE. Niet wegschrijven: anders zijn alle line-ups "verouderd".
        if failed > max(20, 0.05 * len(events)):
            print(f"\nFOUT: {failed} van {len(events)} eventpagina's mislukt. "
                  "Snapshot NIET bijgewerkt.", file=sys.stderr)
            return 2

    added, removed, changed = diff(old, events)
    text = report(added, removed, changed)

    if args.json:
        json.dump({"added": added, "removed": removed,
                   "changed": [{"event": e, "deltas": d} for e, d in changed]},
                  sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif first_run:
        print(f"Eerste run — {len(events)} events vastgelegd, niets om mee te vergelijken.")
    elif text:
        print(text)
    else:
        print(f"Niets veranderd ({len(events)} events).")

    if args.save:
        os.makedirs(os.path.dirname(args.snapshot), exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(args.snapshot, "w", encoding="utf-8") as f:
            json.dump({"source_url": args.url, "fetched_at": stamp,
                       "count": len(events),
                       "events": dict(sorted(events.items(), key=lambda kv: int(kv[0])))},
                      f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        # Changelog naast de snapshot, zodat een testrun met --snapshot niet in
        # de echte historie schrijft. Op de eerste run niets loggen: dan is
        # alles per definitie "nieuw" en zegt dat niets.
        if text and not first_run:
            changelog = os.path.join(os.path.dirname(args.snapshot) or ".", "changelog.md")
            os.makedirs(os.path.dirname(changelog) or ".", exist_ok=True)
            head = "" if os.path.exists(changelog) else "# ADE-programma — wijzigingen\n"
            with open(changelog, "a", encoding="utf-8") as f:
                f.write(f"{head}\n## {stamp}\n\n{text}\n")
        print(f"Snapshot bijgewerkt: {args.snapshot}", file=sys.stderr)

    return 1 if (text and not first_run) else 0


if __name__ == "__main__":
    # Exitcodes: 0 = niets veranderd, 1 = wijzigingen, 2 = fout. Een Python-
    # crash geeft standaard óók 1, en dan opent de workflow een leeg
    # "gewijzigd"-issue en slaat niets op. Een crash moet dus 2 zijn.
    try:
        code = main()
    except SystemExit as e:
        # fetch() stopt met SystemExit("FOUT: …"); een tekst als exitcode
        # wordt door Python óók 1. Alleen een expliciete int laten staan.
        if isinstance(e.code, int):
            raise
        print(e.code, file=sys.stderr)
        sys.exit(2)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(2)
    sys.exit(code)
