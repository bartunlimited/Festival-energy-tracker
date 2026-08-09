#!/usr/bin/env python3
"""Generate awakenings/index.html from the TML tool: same engine, own data."""
import re, os

SRC = "/home/user/Festival-energy-tracker/index.html"
OUT_DIR = "/home/user/Festival-energy-tracker/awakenings"
os.makedirs(OUT_DIR, exist_ok=True)
s = open(SRC, encoding="utf-8").read()

# ---------------- timetable from Bart's screenshot ----------------
# (area, start, end, artist, genre, pick)  — picks are Claude's DNA-based
# suggestions for Bart to correct, NOT his own picks.
T = [
 ("area-v","13:00","14:30","SAMA","Techno",""),
 ("area-v","14:30","16:15","Bart Skils","Techno",""),
 ("area-v","16:15","17:45","Indira Paganotto","Psy / hard techno","rec"),
 ("area-v","17:45","19:45","Chris Liebing & Luke Slater","Hard / dark techno","rec"),
 ("area-v","19:45","21:30","Joseph Capriati","Techno","rec"),
 ("area-v","21:30","23:30","Reinier Zonneveld (live)","Acid / live techno","must"),
 ("area-w","13:00","15:00","Nicky Elisabeth","Melodic house",""),
 ("area-w","15:00","17:00","Kevin de Vries","Melodic techno",""),
 ("area-w","17:00","18:30","Anfisa Letyago","Techno",""),
 ("area-w","18:30","20:00","Stephan Bodzin (live)","Melodic techno (live)",""),
 ("area-w","20:00","21:30","Adriatique","Melodic techno",""),
 ("area-w","21:30","23:30","Tale Of Us","Melodic techno","rec"),
 ("area-x","13:00","14:30","Abstract Division","Techno",""),
 ("area-x","14:30","16:00","Shinedoe & Hemka","Techno",""),
 ("area-x","16:00","17:45","ROD","Techno",""),
 ("area-x","17:45","19:30","Freddy K","Hard techno",""),
 ("area-x","19:30","21:00","Speedy J","Techno","rec"),
 ("area-x","21:00","23:00","Amelie Lens","Dark techno","must"),
 ("area-y","13:00","14:30","Lee Ann Roberts","Hard techno",""),
 ("area-y","14:30","16:30","Charlie Sparks","Hard techno","rec"),
 ("area-y","16:30","18:00","Cera Khin","Hard techno",""),
 ("area-y","18:00","19:30","Rebekah","Hard / industrial techno",""),
 ("area-y","19:30","21:15","Paula Temple & SNTS","Industrial techno","rec"),
 ("area-y","21:15","23:30","I Hate Models","Hard / dark techno","must"),
 ("area-u","13:00","14:30","IGNEZ","Techno",""),
 ("area-u","14:30","16:00","Zenker Brothers","Techno",""),
 ("area-u","16:00","17:30","Adiel","Techno",""),
 ("area-u","17:30","19:00","Robert Hood","Techno","rec"),
 ("area-u","19:00","21:00","Daria Kolosova & Etapp Kyle","Techno",""),
 ("area-u","21:00","22:30","Ellen Allien","Techno",""),
 ("area-c","13:00","15:00","CINCITY","Afro house",""),
 ("area-c","15:00","17:00","AMÉMÉ","Afro house",""),
 ("area-c","17:00","18:30","Chloé Caillet","House",""),
 ("area-c","18:30","20:15","Chris Stussy","Tech house",""),
 ("area-d","13:00","14:30","BELLA","House",""),
 ("area-d","14:30","16:00","Fafi Abdel Nour","House",""),
 ("area-d","16:00","17:30","Sally C","House",""),
 ("area-d","17:30","19:00","Chaos In The CBD","Deep house",""),
 ("area-d","19:00","20:30","TSHA","House",""),
 ("area-d","20:30","22:00","Honey Dijon","House",""),
 ("area-h","14:00","16:00","PH Project","Deep house",""),
 ("area-h","16:00","17:30","Ogazón","Deep house",""),
 ("area-h","17:30","19:00","Samuel Deep","Deep house",""),
 ("area-h","19:00","20:30","Quest","Deep house",""),
 ("area-l","16:30","17:30","DJ Rush","Hard techno","rec"),
 ("area-l","17:30","18:30","Phara","Hard techno",""),
 ("area-l","18:30","19:30","Ben Klock","Dark techno","rec"),
 ("area-l","19:30","21:00","Fadi Mohem","Techno",""),
 ("area-l","21:00","22:00","Cera Khin","Hard techno",""),
]

ART = {
 "SAMA":(74,""), "Bart Skils":(75,""), "Indira Paganotto":(86,"psy-techno surge"),
 "Chris Liebing & Luke Slater":(82,"two legends b2b"), "Joseph Capriati":(80,"marathon groove"),
 "Reinier Zonneveld (live)":(81,"live acid marathon"), "Nicky Elisabeth":(58,""),
 "Kevin de Vries":(64,""), "Anfisa Letyago":(76,""), "Stephan Bodzin (live)":(60,"live melodic, kijkers"),
 "Adriatique":(66,""), "Tale Of Us":(70,"melodic spektakel"),
 "Abstract Division":(73,""), "Shinedoe & Hemka":(73,""), "ROD":(74,""),
 "Freddy K":(80,"relentless"), "Speedy J":(79,"NL veteraan"), "Amelie Lens":(89,"BE techno queen"),
 "Lee Ann Roberts":(80,""), "Charlie Sparks":(83,"rave hysteria"), "Cera Khin":(81,""),
 "Rebekah":(82,""), "Paula Temple & SNTS":(85,"industrial pressure"),
 "I Hate Models":(88,"rave hysteria"), "IGNEZ":(73,""), "Zenker Brothers":(72,""),
 "Adiel":(74,""), "Robert Hood":(81,"Detroit legend"), "Daria Kolosova & Etapp Kyle":(76,""),
 "Ellen Allien":(77,"Berlijn energie"), "CINCITY":(60,""), "AMÉMÉ":(61,""),
 "Chloé Caillet":(65,""), "Chris Stussy":(73,"NL tech house held"), "BELLA":(62,""),
 "Fafi Abdel Nour":(64,""), "Sally C":(64,""), "Chaos In The CBD":(61,""),
 "TSHA":(66,""), "Honey Dijon":(68,"house party"), "PH Project":(57,""),
 "Ogazón":(58,""), "Samuel Deep":(59,""), "Quest":(58,""),
 "DJ Rush":(83,"Chicago hard legend"), "Phara":(78,""), "Ben Klock":(85,"Berghain resident"),
 "Fadi Mohem":(74,""),
}

def js(v): return '"' + v.replace('"','\\"') + '"'

tt = "\n".join(
  f'  {{day:1, stage:{js(a)}, artist:{js(ar)}, start:"{st}", end:"{en}", pick:"{pk}", genre:{js(g)}}},'
  for (a,st,en,ar,g,pk) in T)
TIMETABLE_JS = ("// Extracted from Bart's screenshot of the official Awakenings Sunday timetable.\n"
  "// Picks are Claude's suggestions from Bart's music-DNA — Bart corrects.\n"
  "// Schema per set: {day, stage, artist, start, end, pick:\"must\"|\"rec\"|\"\", genre}\n"
  "// Times \"HH:MM\"; hours < 06:00 belong to the previous festival day.\n"
  "const TIMETABLE = [\n" + tt + "\n];")

STAGES_JS = '''// Awakenings Hilvarenbeek areas — cover/dark are GUESSES (verified:false,
// "?"-badge in UI) until Bart confirms the 2026 layout.
const STAGES = {
  "area-v": { name:"Area V", cover:"open",    size:"XL", dark:false, verified:false, fit:0.8, lightshow:true },  // main
  "area-w": { name:"Area W", cover:"open",    size:"L",  dark:false, verified:false, lightshow:true },
  "area-x": { name:"Area X", cover:"covered", size:"L",  dark:true,  verified:false },  // tent?
  "area-y": { name:"Area Y", cover:"covered", size:"M",  dark:true,  verified:false },  // tent?
  "area-u": { name:"Area U", cover:"covered", size:"M",  dark:true,  verified:false },  // tent?
  "area-c": { name:"Area C", cover:"open",    size:"M",  dark:false, verified:false },
  "area-d": { name:"Area D", cover:"covered", size:"M",  dark:true,  verified:false },  // tent?
  "area-h": { name:"Area H", cover:"covered", size:"S",  dark:false, verified:false },
  "area-l": { name:"Area L", cover:"covered", size:"S",  dark:true,  verified:false },  // tent?
};'''

arts = "\n".join(f'  {js(a)}: {{ energy:{e}{", note:"+js(n) if n else ""} }},' for a,(e,n) in sorted(ART.items(), key=lambda kv: kv[0].lower()))
ARTISTS_JS = ("// Heuristic energy 0-100 (genre + set type + familiarity + reputation).\n"
  "const ARTISTS = {\n" + arts + "\n};")

# ---------------- surgery on the copied tool ----------------
s = s.replace("<title>TML W1 — Dance Energy</title>", "<title>Awakenings — Dance Energy</title>")
s = s.replace("<h1>TML W1 · DANCE ENERGY</h1>", "<h1>AWAKENINGS · DANCE ENERGY</h1>")

s = re.sub(r'const DAY_DATES = \{[^}]*\};', 'const DAY_DATES = { 1:"2026-07-12" };', s)
s = re.sub(r'const DAY_LABELS = \{[^}]*\};', 'const DAY_LABELS = { 1:"Zo 12" };', s)

s = re.sub(r'// Extracted 1:1 from source/tomorrowland-final2\.html.*?const TIMETABLE = \[.*?\n\];', TIMETABLE_JS, s, flags=re.S)
s = re.sub(r'// All cover flags verified by Bart.*?const STAGES = \{.*?\n\};', STAGES_JS, s, flags=re.S)
s = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', ARTISTS_JS, s, flags=re.S)

# weather: Beekse Bergen, Hilvarenbeek NL
s = s.replace('lat:51.087, lon:4.379, tz:"Europe/Brussels"', 'lat:51.523, lon:5.122, tz:"Europe/Amsterdam"')
s = s.replace("latitude=51.087&longitude=4.379", "latitude=51.523&longitude=5.122")
s = s.replace("timezone=Europe%2FBrussels", "timezone=Europe%2FAmsterdam")
s = s.replace('patroon van vandaag (Boom)', 'patroon van vandaag (Hilvarenbeek)')

# generic day handling (single day)
s = s.replace("for(const d of [1,2,3]){", "for(const d of Object.keys(DAY_DATES).map(Number)){")
s = s.replace("const dayChips = [1,2,3].map(d=>", "const dayChips = Object.keys(DAY_DATES).map(Number).map(d=>")

# hour chips 13..23 (festival runs 13:00-23:30)
s = s.replace("const hours=[]; for(let h=12;h<=25;h++) hours.push(h);",
              "const hours=[]; for(let h=13;h<=23;h++) hours.push(h);")
s = s.replace("let filt = { day: festivalDay(now()) || 1, stage:\"all\", fromHour:12, picksOnly:false, minEnergy:false };",
              "let filt = { day: festivalDay(now()) || 1, stage:\"all\", fromHour:13, picksOnly:false, minEnergy:false };")

# pre-festival NU: countdown + sim buttons for Sunday
s = s.replace('const start = new Date(DAY_DATES[1]+"T12:00:00");', 'const start = new Date(DAY_DATES[1]+"T13:00:00");')
s = s.replace('? `Nog <b>${days} ${days===1?"dag":"dagen"}</b> tot Tomorrowland W1.<br>Vr 17 juli vanaf 12:00.`',
              '? `Nog <b>${days} ${days===1?"dag":"dagen"}</b> tot Awakenings.<br>Zo 12 juli vanaf 13:00.`')
s = s.replace('`Weekend 1 zit erop. 🖤`', '`Awakenings zit erop. 🖤`')
s = s.replace('''        <a class="chip" href="?now=2026-07-17T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-07-18T23:00">▶︎ Za 23:00</a>
        <a class="chip" href="?now=2026-07-17T21:30&rain=demo">🌧 Regen-demo</a>''',
'''        <a class="chip" href="?now=2026-07-12T15:00">▶︎ Zo 15:00</a>
        <a class="chip" href="?now=2026-07-12T21:30">▶︎ Zo 21:30</a>
        <a class="chip" href="?now=2026-07-12T20:00&rain=demo">🌧 Regen-demo</a>''')

# tests: rewrite for this dataset
s = re.sub(r'function runTests\(\)\{.*?\n\}', '''function runTests(){
  const get=(a)=>TIMETABLE.find(s=>s.artist===a);
  const results=[];
  const ok=(name,cond)=>results.push((cond?"✅ ":"❌ ")+name);
  ok(`49 sets geladen`, TIMETABLE.length===49);
  ok(`alle stages bekend`, TIMETABLE.every(s=>STAGES[s.stage]));
  ok(`alle artiesten hebben energie`, TIMETABLE.every(s=>ARTISTS[s.artist]));
  const ihm = scoreSet(get("I Hate Models"), null, wx, false);
  const sama = scoreSet(get("SAMA"), null, wx, false);
  ok(`avond-tent I Hate Models [${ihm}] > 13:00 open main SAMA [${sama}]`, ihm>sama);
  const lens = get("Amelie Lens");
  const tL = new Date("2026-07-12T22:00:00");
  const rainWx = { minutely:[{t:tL, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  ok(`tent stijgt bij regen`, scoreSet(lens, tL, rainWx, true) > scoreSet(lens, tL, {minutely:[],hourly:[]}, true));
  const rz = get("Reinier Zonneveld (live)");
  ok(`open main stort in bij regen`, scoreSet(rz, tL, {minutely:[],hourly:[]}, true) > scoreSet(rz, tL, rainWx, true));
  const cl = get("Chris Liebing & Luke Slater");
  const cls = setDate(cl,"start");
  const earlyRain = { minutely:[0,15,30].map(m=>({t:new Date(cls.getTime()+m*60000), mm:1.0})), hourly:[], ts:new Date(), stale:false };
  ok(`slechtste kwartier telt over hele set`, scoreSetWx(cl, earlyRain) < scoreSet(cl, null, wx, false));
  ok(`Area V fit-override 0.8`, stageFit(STAGES["area-v"])===0.8);
  console.log("AWK engine tests:\\n"+results.join("\\n"));
  if(results.some(r=>r.startsWith("❌"))) alert("Engine tests FAILED — zie console");
}''', s, flags=re.S)

open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(s)
for frag in ["Awakenings — Dance Energy", "area-v", "2026-07-12", "51.523", "Europe%2FAmsterdam", "AWK engine tests"]:
    assert frag in s, frag
assert "tomorrowland-final2" not in s.split("const TIMETABLE")[1].split("];")[0]
print("awakenings/index.html written,", len(s), "bytes")
