#!/usr/bin/env python3
"""Generate tillatec/index.html — Tillatec x WorldPride, 1-3 aug 2026 Amsterdam.
34-hour marathon: needs a night-based day model and a night energy curve."""
import re, os

SRC = "/home/user/Festival-energy-tracker/index.html"
OUT = "/home/user/Festival-energy-tracker/tillatec"
os.makedirs(OUT, exist_ok=True)
s = open(SRC, encoding="utf-8").read()

# (day, room, start, end, artist, genre, energy, pick)
# day 1 = za 1 aug 22:00 -> zo 11:00 | day 2 = zo 11:00 -> ma 08:00
T = [
 # ---------------- NACHT 1 ----------------
 (1,"washroom","23:00","01:00","Gian Battista","Trance / techno",70,""),
 (1,"washroom","01:00","05:00","Tommy Hart b2b FKA.M4A","Hard trance / techno",86,"must"),
 (1,"washroom","05:00","08:00","HAAI","Breaks / euforische techno",82,"must"),
 (1,"washroom","08:00","11:00","Onbekend (poster bedekt)","?",50,""),
 (1,"teclab","23:00","03:00","Mystral","Trance / techno",72,"rec"),
 (1,"teclab","03:00","06:00","Slim Soledad","Hard trance / techno",80,"rec"),
 (1,"teclab","06:00","09:00","MCMLXXXV","Hard techno / rave",78,""),
 (1,"teclab","09:00","12:00","Cem","Techno",70,""),
 (1,"yard","23:00","02:00","Emma Champagne","Drag / club",58,""),
 (1,"yard","02:00","05:00","Carista","House / eclectic",74,"rec"),
 (1,"yard","05:00","08:00","Cormac","House / disco / techno",78,"rec"),
 (1,"yard","08:00","11:00","Narciss","Hard / fast techno",78,"rec"),
 (1,"switchroom","00:00","03:00","Magdo","Techno",66,""),
 (1,"switchroom","03:00","06:00","Andres Soria","Hard techno",76,"rec"),
 (1,"switchroom","06:00","09:00","Lara Renner","Hypnotic techno",76,"rec"),
 (1,"switchroom","09:00","13:00","Maze","Techno",68,""),
 # ---------------- ZONDAG -> MAANDAG ----------------
 (2,"washroom","11:00","14:00","Djooke","Techno",68,""),
 (2,"washroom","14:00","17:00","Jaspol","Techno",66,""),
 (2,"washroom","17:00","20:00","Moody Mehran","Techno / house",68,""),
 (2,"washroom","20:00","22:30","Isabella","Techno",70,""),
 (2,"washroom","22:30","02:00","Cybersex","Hard techno / EBM",74,"rec"),
 (2,"washroom","02:00","05:00","Marie Malarie b2b Byron Yeates","Hard house / trance",78,"rec"),
 (2,"washroom","05:00","08:00","Pablo Bozzi","EBM / italo / hard",80,"rec"),
 (2,"teclab","12:00","22:00","Onbekend (poster bedekt)","?",50,""),
 (2,"teclab","22:00","01:00","Vani Vachi b2b Nastya Muravyova","Hard trance / techno",82,"rec"),
 (2,"teclab","01:00","03:00","Bjarki","Techno / rave",78,"rec"),
 (2,"teclab","03:00","05:00","Tweeman","Club / eclectic",68,""),
 (2,"teclab","05:00","08:00","Mama Snake","Hard trance / techno",80,"rec"),
 (2,"yard","11:00","15:00","Eurotic","Club / eclectic",70,""),
 (2,"yard","15:00","19:00","Husc","House",68,""),
 (2,"yard","19:00","22:00","Kilopatrah Jones","House / club",66,""),
 (2,"yard","22:00","01:00","Di After","Club / house",66,""),
 (2,"yard","01:00","04:00","Pedro Gariani","Hard / fast techno",72,""),
]

STAGES_JS = '''// Tillatec — alles binnen behalve Yard (Bart, 2026-08-01).
const STAGES = {
  "washroom":   { name:"Washroom",   cover:"indoor", size:"L", dark:true,  verified:true },  // main
  "teclab":     { name:"Teclab",     cover:"indoor", size:"M", dark:true,  verified:true },
  "yard":       { name:"Yard",       cover:"open",   size:"M", dark:false, verified:true },  // buiten
  "switchroom": { name:"Switchroom", cover:"indoor", size:"S", dark:true,  verified:true },
};'''

def js(v): return '"' + v.replace('"','\\"') + '"'
recs, artists = [], {}
for day, room, st, en, a, g, e, pick in T:
    recs.append(f'  {{day:{day}, stage:{js(room)}, artist:{js(a)}, start:"{st}", end:"{en}", pick:"{pick}", genre:{js(g)}}},')
    artists.setdefault(a, e)
TIMETABLE_JS = ("// Tillatec x WorldPride, za 1 - ma 3 aug 2026 (Knit x Herrensauna x Veselka).\n"
  "// Afgeleid van de uur-as op de poster: de acts staan er zonder tijden bij,\n"
  "// blokken vallen op hele uren (+/- 15 min). Twee blokken zijn onleesbaar\n"
  "// door de artwork-overlay en staan als 'Onbekend'.\n"
  "// dag 1 = za 22:00 -> zo 11:00 | dag 2 = zo 11:00 -> ma 08:00\n"
  "const TIMETABLE = [\n" + "\n".join(recs) + "\n];")
ARTISTS_JS = ("// Heuristic energy 0-100; veel underground/lokale namen -> voorzichtige schattingen.\n"
  "const ARTISTS = {\n" + "\n".join(f'  {js(a)}: {{ energy:{e} }},' for a, e in sorted(artists.items(), key=lambda kv: kv[0].lower())) + "\n};")

def rep(old, new, cnt=1):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, cnt)

# ---- identity ----
rep("<title>TML W1 — Dance Energy</title>", "<title>Tillatec — Dance Energy</title>")
rep("<h1>TML W1 · DANCE ENERGY</h1>", "<h1>TILLATEC · DANCE ENERGY</h1>")

# ---- day model: night-based ----
s = re.sub(r'const DAY_DATES = \{[^}]*\};',
  'const DAY_DATES  = { 1:"2026-08-01", 2:"2026-08-02" };\n'
  '// festival-uur waarop een "dag" begint/eindigt (uren >= 24 = volgende ochtend)\n'
  'const DAY_START  = { 1:22, 2:11 };\n'
  'const DAY_END    = { 1:35, 2:32 };', s)
s = re.sub(r'const DAY_LABELS = \{[^}]*\};',
  'const DAY_LABELS = { 1:"Nacht 1", 2:"Zo → Ma" };', s)
s = re.sub(r'// Extracted 1:1.*?const TIMETABLE = \[.*?\n\];|// Updated official W1 timetable.*?const TIMETABLE = \[.*?\n\];', lambda m: TIMETABLE_JS, s, flags=re.S)
s = re.sub(r'// All cover flags verified by Bart.*?const STAGES = \{.*?\n\};', lambda m: STAGES_JS, s, flags=re.S)
s = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', lambda m: ARTISTS_JS, s, flags=re.S)

# ---- night energy curve (piek 02:00-06:00) ----
s = re.sub(r'  slotCurve: \[.*?\],\n',
  '  // nachtcurve in festival-uur (11..37): piek 02:00-06:00, dip zondagmiddag\n'
  '  slotCurve: [ [11,17,0.62],[17,20,0.72],[20,22,0.82],[22,24,0.90],[24,26,0.96],\n'
  '               [26,30,1.00],[30,32,0.94],[32,34,0.82],[34,38,0.66] ],\n', s, flags=re.S)

# ---- toMin per day + helper ----
rep('function toMin(hhmm){ const [h,m]=hhmm.split(":").map(Number); return ((h<6?h+24:h)*60)+m; }',
'''function toMin(hhmm, day){
  const [h,m] = hhmm.split(":").map(Number);
  const st = DAY_START[day||1];          // uren vóór de dagstart horen bij de volgende ochtend
  return ((h<st ? h+24 : h)*60)+m;
}
// minuten van een set in de tijdruimte van zijn eigen dag
function sMin(set, which){ return toMin(which==="end"?set.end:set.start, set.day); }''')

rep('  return new Date(base.getTime() + toMin(which==="start"?set.start:set.end)*60000);',
    '  return new Date(base.getTime() + sMin(set, which)*60000);')
rep('''  const s0 = toMin(set.start);
  return !TIMETABLE.some(o => o!==set && o.day===set.day && o.stage===set.stage && toMin(o.start)>s0);''',
'''  const s0 = sMin(set,"start");
  return !TIMETABLE.some(o => o!==set && o.day===set.day && o.stage===set.stage && sMin(o,"start")>s0);''')
rep('  const s0=toMin(set.start), e0=toMin(set.end), fam=genreFam(set.genre);',
    '  const s0=sMin(set,"start"), e0=sMin(set,"end"), fam=genreFam(set.genre);')
rep('    const s1=toMin(o.start), e1=toMin(o.end);', '    const s1=sMin(o,"start"), e1=sMin(o,"end");')
rep('  const fh = live && t ? festHour(t) : (toMin(set.start)+toMin(set.end))/2/60;',
    '  const fh = live && t ? festHour(t) : (sMin(set,"start")+sMin(set,"end"))/2/60;')
rep('  return new Date(base.getTime() + (toMin(set.start)+toMin(set.end))/2*60000);',
    '  return new Date(base.getTime() + (sMin(set,"start")+sMin(set,"end"))/2*60000);')
rep('    .filter(s=>toMin(s.start) >= filt.fromHour*60)', '    .filter(s=>sMin(s,"start") >= filt.fromHour*60)')
rep('    .sort((a,b)=>toMin(a.set.start)-toMin(b.set.start));', '    .sort((a,b)=>sMin(a.set,"start")-sMin(b.set,"start"));')
rep('    const b = Math.floor(toMin(r.set.start)/15)*15;', '    const b = Math.floor(sMin(r.set,"start")/15)*15;')

# ---- festHour: clockuur -> zelfde 11..37-ruimte ----
rep('function festHour(t){ const h = t.getHours()+t.getMinutes()/60; return h<6 ? h+24 : h; }',
    'function festHour(t){ const h = t.getHours()+t.getMinutes()/60; return h<11 ? h+24 : h; }')

# ---- festivalDay op basis van DAY_START/DAY_END ----
rep('''  for(const d of Object.keys(DAY_DATES).map(Number)){
    const base = new Date(DAY_DATES[d]+"T00:00:00").getTime();
    if(t.getTime() >= base+11*3600e3 && t.getTime() < base+30*3600e3) return d;
  }''',
'''  for(const d of Object.keys(DAY_DATES).map(Number)){
    const base = new Date(DAY_DATES[d]+"T00:00:00").getTime();
    if(t.getTime() >= base+DAY_START[d]*3600e3 && t.getTime() < base+DAY_END[d]*3600e3) return d;
  }''')

# ---- uur-chips uit de data zelf (marathon loopt over middernacht heen) ----
rep('''  const hours=[]; for(let h=12;h<=25;h++) hours.push(h);
  const hourChips = hours.map(h=>{
    const label = h>=24 ? String(h-24).padStart(2,"0") : String(h);
    return `<button class="chip ${filt.fromHour===h?"on":""}" onclick="filt.fromHour=${h};render()">${label}</button>`;
  }).join("");''',
'''  const hours = [...new Set(TIMETABLE.filter(s=>s.day===filt.day).map(s=>Math.floor(sMin(s,"start")/60)))].sort((a,b)=>a-b);
  const hourChips = [`<button class="chip ${filt.fromHour===0?"on":""}" onclick="filt.fromHour=0;render()">alles</button>`]
    .concat(hours.map(h=>`<button class="chip ${filt.fromHour===h?"on":""}" onclick="filt.fromHour=${h};render()">${String(h%24).padStart(2,"0")}</button>`)).join("");''')
rep('fromHour:12, picksOnly:false, minEnergy:false, showPast:false };', 'fromHour:0, picksOnly:false, minEnergy:false, showPast:false };')

# ---- weer: Amsterdam; alleen Yard buiten ----
rep('lat:51.087, lon:4.379, tz:"Europe/Brussels"', 'lat:52.379, lon:4.900, tz:"Europe/Amsterdam"')
rep("latitude=51.087&longitude=4.379", "latitude=52.379&longitude=4.900")
rep("timezone=Europe%2FBrussels", "timezone=Europe%2FAmsterdam")
rep('patroon van vandaag (Boom)', 'patroon van vandaag (Amsterdam)')

# ---- pre-party scherm ----
rep('const start = new Date(DAY_DATES[1]+"T12:00:00");', 'const start = new Date(DAY_DATES[1]+"T22:00:00");')
rep('tot Tomorrowland W1.<br>Do 16 juli (The Gathering) vanaf 14:00, hoofdterrein vanaf vr 17.`',
    'tot Tillatec.<br>Za 1 aug 22:00 → ma 3 aug 08:00.`')
rep('`Weekend 1 zit erop. 🖤`', '`Tillatec zit erop. 🖤`')
rep('''        <a class="chip" href="?now=2026-07-17T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-07-18T23:00">▶︎ Za 23:00</a>
        <a class="chip" href="?now=2026-07-17T21:30&rain=demo">🌧 Regen-demo</a>''',
'''        <a class="chip" href="?now=2026-08-02T03:00">▶︎ Nacht 1, 03:00</a>
        <a class="chip" href="?now=2026-08-02T06:30">▶︎ Zonsopgang 06:30</a>
        <a class="chip" href="?now=2026-08-03T02:00">▶︎ Nacht 2, 02:00</a>
        <a class="chip" href="?now=2026-08-02T03:00&rain=demo">🌧 Regen-demo</a>''')

# ---- tests ----
NEW_TESTS = '''function runTests(){
  const get=(a)=>TIMETABLE.find(s=>s.artist===a);
  const results=[];
  const ok=(name,cond)=>results.push((cond?"✅ ":"❌ ")+name);
  ok(`''' + str(len(T)) + ''' sets geladen`, TIMETABLE.length===''' + str(len(T)) + ''');
  ok(`alle rooms bekend`, TIMETABLE.every(s=>STAGES[s.stage]));
  ok(`alle artiesten hebben energie`, TIMETABLE.every(s=>ARTISTS[s.artist]));
  ok(`nacht-uren kloppen: 05:00 op nacht 1 = zo-ochtend`,
     setDate(get("HAAI"),"start").getDate()===2 && setDate(get("HAAI"),"start").getHours()===5);
  ok(`23:00 op nacht 1 = za-avond`, setDate(get("Gian Battista"),"start").getDate()===1);
  ok(`08:00 op dag 2 = ma-ochtend`, setDate(get("Pablo Bozzi"),"end").getDate()===3);
  const peak = scoreSet(get("Tommy Hart b2b FKA.M4A"), null, wx, false);
  const mid  = scoreSet(get("Jaspol"), null, wx, false);
  ok(`nachtpiek [${peak}] > zondagmiddag [${mid}]`, peak>mid);
  const t = new Date("2026-08-02T03:00:00");
  const rainWx = { minutely:[{t, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  const car = get("Carista"), tom = get("Tommy Hart b2b FKA.M4A");
  ok(`Yard (buiten) stort in bij regen`, scoreSet(car, t, {minutely:[],hourly:[]}, true) > scoreSet(car, t, rainWx, true));
  ok(`binnen stijgt bij regen`, scoreSet(tom, t, rainWx, true) > scoreSet(tom, t, {minutely:[],hourly:[]}, true));
  ok(`festivaldag klopt om 03:00 zo`, festivalDay(t)===1);
  ok(`festivaldag klopt om 02:00 ma`, festivalDay(new Date("2026-08-03T02:00:00"))===2);
  console.log("Tillatec engine tests:\\n"+results.join("\\n"));
  if(results.some(r=>r.startsWith("❌"))) alert("Engine tests FAILED — zie console");
}'''
s = re.sub(r'function runTests\(\)\{.*?\n\}', lambda m: NEW_TESTS, s, flags=re.S)

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
assert "toMin(s.start)" not in s and "toMin(set.start)" not in s and "toMin(o.start)" not in s
print(f"tillatec/index.html: {len(T)} sets, {len(artists)} artiesten")
