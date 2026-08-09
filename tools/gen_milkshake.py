#!/usr/bin/env python3
"""Generate milkshake/index.html — Milkshake Festival Sunday 26 July 2026,
Westerpark Amsterdam. Same engine as the TML tool."""
import re, os

SRC = "/home/user/Festival-energy-tracker/index.html"
OUT = "/home/user/Festival-energy-tracker/milkshake"
os.makedirs(OUT, exist_ok=True)
s = open(SRC, encoding="utf-8").read()

# (stage, start, end, artist, genre, energy, pick) — ends afgeleid van volgende set
T = [
 ("supertoys","13:00","15:00","Bestley","House",62,""),
 ("supertoys","15:00","15:10","Kyara","Drag / show",55,""),
 ("supertoys","15:30","15:40","Babette & Katja","Drag / show",55,""),
 ("supertoys","15:40","17:10","Juliana X","House",64,""),
 ("supertoys","17:10","17:30","Amanda Lepore","Drag / show",58,""),
 ("supertoys","17:30","19:00","Pabllo Vittar presents Club Vittar","Pop / club show",70,""),
 ("supertoys","19:00","19:05","Sasha Colby","Drag / show",60,""),
 ("supertoys","19:05","20:10","Byron Yeates","Hard house / trance",74,"rec"),
 ("supertoys","20:10","20:15","Envy Peru","Drag / show",58,""),
 ("supertoys","20:15","20:20","Milkshake Finale","Show",65,""),
 ("supertoys","20:20","21:30","Dee Diggs b2b Ultra Naté","House / vocal",72,"rec"),
 ("supertoys","21:30","23:00","Todd Terry","House",78,"rec"),
 ("poezendek","13:00","14:30","Jazz Dalia","House / disco",58,""),
 ("poezendek","14:30","15:30","Soulfania","Soul / house",58,""),
 ("poezendek","15:30","17:00","PGLTM SS","Club / eclectic",56,""),
 ("poezendek","17:00","18:00","Motie van Wanvrouwen","Club / eclectic",56,""),
 ("poezendek","18:00","18:20","Cakes Da Killa","Rap / club",62,""),
 ("poezendek","18:20","19:15","Lordesius","Eclectic",60,""),
 ("poezendek","19:15","20:30","Mixturess","Club / eclectic",60,""),
 ("poezendek","20:30","22:30","Shug La Sheedah","House / club",62,""),
 ("janey","13:00","13:30","Krioro","Club",54,""),
 ("janey","13:30","14:00","Cleyani","Club",54,""),
 ("janey","14:00","14:45","Shaniqua Devine","Club / vogue",56,""),
 ("janey","14:45","15:25","Raphaella Brown","Club / vogue",56,""),
 ("janey","15:25","15:35","Zaya Sabrina","Drag / show",54,""),
 ("janey","15:35","16:15","Chocolat","Club",56,""),
 ("janey","16:15","17:00","Blue","Club",56,""),
 ("janey","17:00","17:45","Doris Bae","Club / house",58,""),
 ("janey","17:45","18:30","Charlie","Club / house",58,""),
 ("janey","18:30","19:15","Rockefellababe","Eclectic",60,""),
 ("janey","19:15","20:00","Nina Sanetti","House",60,""),
 ("janey","20:00","20:45","Lotte","House",60,""),
 ("janey","20:45","21:15","Emma Champagne Queen","Drag / show",58,""),
 ("janey","21:15","22:30","Jennifer Cooke (live)","Live / club",58,""),
 ("heisas-house","13:00","14:30","The Heart Breaks","Pop / club",56,""),
 ("heisas-house","14:30","16:00","Puma Hilton","Club / house",60,""),
 ("heisas-house","16:00","17:10","Heisa Jynx","Club / house",60,""),
 ("heisas-house","17:10","17:15","Soundos","Show",54,""),
 ("heisas-house","17:15","17:30","King Faisel","Show",54,""),
 ("heisas-house","17:30","19:00","Emma Champagne Queen","Drag / club",58,""),
 ("heisas-house","19:00","20:20","Kroes Control","House / club",62,""),
 ("heisas-house","20:20","20:30","Danny Beard","Drag / show",58,""),
 ("heisas-house","20:30","22:30","Hollywood Tramp","House / club",62,""),
 ("poofdoof","13:00","14:00","Nic Holland","House",58,""),
 ("poofdoof","14:00","15:00","Erfaan","House",58,""),
 ("poofdoof","15:00","16:00","Dingo Disco","Disco / house",60,""),
 ("poofdoof","16:00","17:00","Alaika","House",58,""),
 ("poofdoof","17:00","18:00","Atomic Blonde","House / club",60,""),
 ("poofdoof","18:00","19:00","MRCL","House",62,""),
 ("poofdoof","19:00","20:00","Argonaut","House / techno",64,""),
 ("poofdoof","20:00","21:00","Jimi The Kween","House / club",62,""),
 ("poofdoof","21:00","22:30","Baiin Twins","House / techno",64,""),
 ("bear-necessity","13:00","15:00","Bram Sterdam & Big General","House / disco",58,""),
 ("bear-necessity","15:00","17:00","Sergio Cardoso","House",60,""),
 ("bear-necessity","17:00","19:30","Be-Rik","House / trance",62,""),
 ("bear-necessity","19:30","23:00","Chris Bekker","Trance",68,"rec"),
 ("drag-tastic","13:00","13:30","Marja van Katendrecht","Drag / show",56,""),
 ("drag-tastic","13:30","17:45","Buuf Helen","Drag / show",56,""),
 ("drag-tastic","17:45","22:30","Abby OMG","Drag / show",58,""),
 ("yas-karaoke","14:00","15:00","DJ Linde Schöne","Karaoke / party",56,""),
 ("yas-karaoke","15:00","17:00","Beyoncé Karaoke by Davey","Karaoke / party",60,""),
 ("yas-karaoke","17:00","20:30","The Aiscream Karaoke Show","Karaoke / party",58,""),
 ("the-attic","13:00","14:30","Juna","House / club",58,""),
 ("the-attic","14:30","16:00","Cleo","House / club",60,""),
 ("the-attic","16:00","18:00","Dey.Rey","House / techno",62,""),
 ("the-attic","18:00","20:00","Armana Khan","House / techno",64,""),
 ("the-attic","20:00","22:00","Alyosha","Techno",66,""),
 ("spikey-lee","13:00","14:00","Tweeman","Club / eclectic",56,""),
 ("spikey-lee","14:00","16:00","Vinvar","House",58,""),
 ("spikey-lee","16:00","18:00","Laure Croft","House / club",60,""),
 ("spikey-lee","18:00","20:00","Spikey Lee","House / club",64,""),
 ("spikey-lee","20:00","22:00","Volvox","Techno / acid",74,"rec"),
]

STAGES_JS = '''// Milkshake Westerpark — covers zijn GISSINGEN (verified:false, ?-badge)
// tot Bart ze bevestigt.
const STAGES = {
  "supertoys":      { name:"Supertoys",       cover:"open",    size:"L",  dark:false, verified:false, lightshow:true },  // main
  "poezendek":      { name:"Poezendek",       cover:"open",    size:"M",  dark:false, verified:false },
  "janey":          { name:"Janey",           cover:"covered", size:"S",  dark:true,  verified:false },
  "heisas-house":   { name:"Heisa's House",   cover:"covered", size:"M",  dark:true,  verified:false },
  "poofdoof":       { name:"Poofdoof",        cover:"covered", size:"M",  dark:true,  verified:false },
  "bear-necessity": { name:"Bear-Necessity",  cover:"covered", size:"S",  dark:true,  verified:false },
  "drag-tastic":    { name:"Drag-Tastic",     cover:"covered", size:"S",  dark:true,  verified:false },
  "yas-karaoke":    { name:"YAS! Karaoke",    cover:"covered", size:"S",  dark:true,  verified:false },
  "the-attic":      { name:"The Attic",       cover:"indoor",  size:"S",  dark:true,  verified:false },
  "spikey-lee":     { name:"Spikey Lee & Fr.",cover:"open",    size:"S",  dark:false, verified:false },
};'''

def js(v): return '"' + v.replace('"','\\"') + '"'
recs, artists = [], {}
for stage, st, en, a, g, e, pick in T:
    recs.append(f'  {{day:1, stage:{js(stage)}, artist:{js(a)}, start:"{st}", end:"{en}", pick:"{pick}", genre:{js(g)}}},')
    artists.setdefault(a, (e, ""))
TIMETABLE_JS = ("// Milkshake Festival — Sunday 26 July 2026, from Bart's poster screenshot.\n"
  "// Korte drag-optredens staan er als eigen (korte) sets in; eindtijden zijn\n"
  "// afgeleid van de volgende set. Onzekere leesbare tijden: zie chat.\n"
  "// Schema per set: {day, stage, artist, start, end, pick:\"must\"|\"rec\"|\"\", genre}\n"
  "const TIMETABLE = [\n" + "\n".join(recs) + "\n];")
arts = "\n".join(f'  {js(a)}: {{ energy:{v[0]} }},' for a, v in sorted(artists.items(), key=lambda kv: kv[0].lower()))
ARTISTS_JS = "// Heuristic energy 0-100 — veel lokale/drag-acts, defaults rond 55-65.\nconst ARTISTS = {\n" + arts + "\n};"

s = s.replace("<title>TML W1 — Dance Energy</title>", "<title>Milkshake — Dance Energy</title>")
s = s.replace("<h1>TML W1 · DANCE ENERGY</h1>", "<h1>MILKSHAKE · DANCE ENERGY</h1>")
s = re.sub(r'const DAY_DATES = \{[^}]*\};', 'const DAY_DATES = { 1:"2026-07-26" };', s)
s = re.sub(r'const DAY_LABELS = \{[^}]*\};', 'const DAY_LABELS = { 1:"Zo 26" };', s)
s = re.sub(r'// Updated official W1 timetable.*?const TIMETABLE = \[.*?\n\];', lambda m: TIMETABLE_JS, s, flags=re.S)
s = re.sub(r'// All cover flags verified by Bart.*?const STAGES = \{.*?\n\};', lambda m: STAGES_JS, s, flags=re.S)
s = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', lambda m: ARTISTS_JS, s, flags=re.S)
# weather: Westerpark Amsterdam
s = s.replace('lat:51.087, lon:4.379, tz:"Europe/Brussels"', 'lat:52.387, lon:4.873, tz:"Europe/Amsterdam"')
s = s.replace("latitude=51.087&longitude=4.379", "latitude=52.387&longitude=4.873")
s = s.replace("timezone=Europe%2FBrussels", "timezone=Europe%2FAmsterdam")
s = s.replace('patroon van vandaag (Boom)', 'patroon van vandaag (Amsterdam)')
# hour chips 13..23
s = s.replace("const hours=[]; for(let h=12;h<=25;h++) hours.push(h);",
              "const hours=[]; for(let h=13;h<=23;h++) hours.push(h);")
s = s.replace('fromHour:12, picksOnly:false, minEnergy:false, showPast:false };',
              'fromHour:13, picksOnly:false, minEnergy:false, showPast:false };')
# countdown + sim buttons
s = s.replace('const start = new Date(DAY_DATES[1]+"T12:00:00");', 'const start = new Date(DAY_DATES[1]+"T13:00:00");')
s = s.replace('tot Tomorrowland W1.<br>Do 16 juli (The Gathering) vanaf 14:00, hoofdterrein vanaf vr 17.`',
              'tot Milkshake.<br>Zo 26 juli vanaf 13:00, Westerpark.`')
s = s.replace('''        <a class="chip" href="?now=2026-07-17T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-07-18T23:00">▶︎ Za 23:00</a>
        <a class="chip" href="?now=2026-07-17T21:30&rain=demo">🌧 Regen-demo</a>''',
'''        <a class="chip" href="?now=2026-07-26T16:00">▶︎ Zo 16:00</a>
        <a class="chip" href="?now=2026-07-26T21:00">▶︎ Zo 21:00</a>
        <a class="chip" href="?now=2026-07-26T20:00&rain=demo">🌧 Regen-demo</a>''')
NEW_TESTS = '''function runTests(){
  const get=(a)=>TIMETABLE.find(s=>s.artist===a);
  const results=[];
  const ok=(name,cond)=>results.push((cond?"✅ ":"❌ ")+name);
  ok(`''' + str(len(T)) + ''' sets geladen`, TIMETABLE.length===''' + str(len(T)) + ''');
  ok(`alle stages bekend`, TIMETABLE.every(s=>STAGES[s.stage]));
  ok(`alle artiesten hebben energie`, TIMETABLE.every(s=>ARTISTS[s.artist]));
  const todd = scoreSet(get("Todd Terry"), null, wx, false);
  const krioro = scoreSet(get("Krioro"), null, wx, false);
  ok(`avond Todd Terry [${todd}] > middag-opener [${krioro}]`, todd>krioro);
  const tL = new Date("2026-07-26T21:30:00");
  const rainWx = { minutely:[{t:tL, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  const aly = get("Alyosha");
  ok(`binnen/tent stijgt bij regen`, scoreSet(aly, tL, rainWx, true) > scoreSet(aly, tL, {minutely:[],hourly:[]}, true));
  const tt2 = get("Todd Terry");
  const t2 = new Date("2026-07-26T22:00:00");
  const rainWx2 = { minutely:[{t:t2, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  ok(`open main stort in bij regen`, scoreSet(tt2, t2, {minutely:[],hourly:[]}, true) > scoreSet(tt2, t2, rainWx2, true));
  const long = get("Bestley");
  const ls = setDate(long,"start");
  const earlyRain = { minutely:[0,15,30].map(m=>({t:new Date(ls.getTime()+m*60000), mm:1.0})), hourly:[], ts:new Date(), stale:false };
  ok(`slechtste kwartier telt over hele set`, scoreSetWx(long, earlyRain) < scoreSet(long, null, wx, false));
  console.log("Milkshake engine tests:\\n"+results.join("\\n"));
  if(results.some(r=>r.startsWith("❌"))) alert("Engine tests FAILED — zie console");
}'''
s = re.sub(r'function runTests\(\)\{.*?\n\}', lambda m: NEW_TESTS, s, flags=re.S)

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
for f in ["2026-07-26", "Zo 26", "Todd Terry", "MILKSHAKE"]:
    assert f in s, f
print(f"milkshake/index.html: {len(T)} sets, {len(artists)} artiesten")
