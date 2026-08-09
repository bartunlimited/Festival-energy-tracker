#!/usr/bin/env python3
"""ade_watch.py — scrape de ADE-programmapagina en meld wat er veranderd is.

    python3 tools/ade_watch.py                # scrapen + diffen tegen de snapshot
    python3 tools/ade_watch.py --save         # idem, en de nieuwe snapshot wegschrijven
    python3 tools/ade_watch.py --render       # via Playwright renderen (JS-pagina's)
    python3 tools/ade_watch.py --dump out.html   # ruwe HTML bewaren om selectors te fixen

Exit codes: 0 = niets veranderd · 1 = wijzigingen gevonden · 2 = fout of 0 events.
Zo kun je hem in cron of GitHub Actions hangen en op exit 1 laten alarmeren.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.error, urllib.request
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

def fetch(url, tries=4):
    """GET met retry-backoff. Geen Accept-Encoding, dan komt het onverpakt binnen."""
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
        stop = min(nxt.start() if nxt else len(html), ctx_from + 600)
        found[eid] = {
            "id": eid,
            "title": label or title_from_slug(m.group("slug")),
            "url": abs_url(m.group("url")),
            "slug": m.group("slug"),
            "context": strip_tags(html[ctx_from:stop])[:300],
            "source": "anchor",
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

DIFF_FIELDS = ("title", "url", "start", "end", "venue")


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
    ap.add_argument("--json", action="store_true", help="diff als JSON naar stdout")
    args = ap.parse_args()

    print(f"Ophalen: {args.url}", file=sys.stderr)
    events, pages = scrape(args.url, args.render, args.max_pages, args.dump)
    print(f"Totaal: {len(events)} events over {pages} pagina('s)", file=sys.stderr)

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
    sys.exit(main())
