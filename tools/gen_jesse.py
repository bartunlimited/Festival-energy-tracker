#!/usr/bin/env python3
"""Generate jesse/index.html — TML W2 Friday 24 July, for Jesse.
Same engine + verified stage metadata as Bart's W1 app."""
import re, os

SRC = "/home/user/Festival-energy-tracker/index.html"
OUT = "/home/user/Festival-energy-tracker/jesse"
os.makedirs(OUT, exist_ok=True)
s = open(SRC, encoding="utf-8").read()

# reuse W1 knowledge: artist -> (energy, note) and artist -> genre
art_w1 = {}
for m in re.finditer(r'"((?:[^"\\]|\\.)*)": \{ energy:(\d+)(?:, note:"((?:[^"\\]|\\.)*)")? \}', s):
    art_w1[m.group(1)] = (int(m.group(2)), m.group(3) or "")
genre_w1 = {}
for m in re.finditer(r'artist:"((?:[^"\\]|\\.)*)"[^}]*genre:"((?:[^"\\]|\\.)*)"', s):
    genre_w1.setdefault(m.group(1), m.group(2))

# (stage, start, end, artist, genre-if-new, energy-if-new)
T = [
 ("mainstage","14:00","15:30","Volkoder","Techno",74),
 ("mainstage","15:30","16:30","Ely Oaks","EDM",60),
 ("mainstage","16:30","17:30","Yves V",None,None),
 ("mainstage","17:30","17:45","Openingsshow",None,None),
 ("mainstage","17:35","18:35","Miss Monique",None,None),
 ("mainstage","18:40","19:40","Indira Paganotto",None,None),
 ("mainstage","19:40","20:40","Nicky Romero",None,None),
 ("mainstage","20:40","21:40","Kölsch","Melodic techno",68),
 ("mainstage","21:45","22:45","Alok","EDM",66),
 ("mainstage","22:50","23:50","Steve Angello",None,None),
 ("mainstage","23:50","00:50","Hardwell","Big room EDM",80),
 ("freedom","13:30","15:00","JOA","House",58),
 ("freedom","15:00","16:00","Aaron Hibell","Melodic techno",62),
 ("freedom","16:00","17:30","Amber Broos b2b Juliet Fox","Techno",68),
 ("freedom","17:30","19:00","Enrico Sangiuliano","Techno",82),
 ("freedom","19:00","20:00","John Newman",None,None),
 ("freedom","20:00","20:30","B...","?",50),
 ("freedom","20:30","21:30","James Hype","Tech house",78),
 ("freedom","21:30","23:00","Fisher",None,None),
 ("freedom","23:00","00:30","Alesso",None,None),
 ("great-library","13:00","14:00","Meaghan","House",58),
 ("great-library","14:00","15:00","NOME.","EDM",60),
 ("great-library","15:00","16:00","5NAPBACK","EDM",62),
 ("great-library","16:00","17:00","Merow",None,None),
 ("great-library","17:00","18:00","B Jones",None,None),
 ("great-library","18:00","19:00","Regi","Pop / dance",56),
 ("great-library","19:00","20:00","MANDY",None,None),
 ("great-library","20:00","21:00","Omdat Het Ka...",None,None),
 ("great-library","21:00","22:00","HALÒ",None,None),
 ("great-library","22:00","23:00","Kaskade","Progressive house",68),
 ("great-library","23:00","23:55","Alan Walker","Melodic EDM",66),
 ("great-library","23:55","00:50","Illenium",None,None),
 ("crystal-garden","13:30","15:30","Capoon","Afro house",60),
 ("crystal-garden","15:30","17:00","Malive","Melodic house",62),
 ("crystal-garden","17:00","18:30","Joezi","Afro house",64),
 ("crystal-garden","18:30","20:00","Kitty Amor b2b Curol","Afro house",64),
 ("crystal-garden","20:00","21:30","Shimza","Afro house",70),
 ("crystal-garden","21:30","23:00","Hugel","House",72),
 ("crystal-garden","23:00","00:30","Mahmut Orhan","Melodic house",66),
 ("core","13:00","15:00","Sixsixties","Eclectic",60),
 ("core","15:00","17:00","Kamma","Melodic / deep house",62),
 ("core","17:00","19:00","Bibi Seck b2b Faisal","House / techno",62),
 ("core","19:00","20:30","Ogazón","Deep house",58),
 ("core","20:30","22:00","Bullet Tooth","House / rave",66),
 ("core","22:00","23:45","Mall Grab","House / rave",76),
 ("core","23:45","00:50","Oscar and the...",None,None),
 ("atmosphere","14:00","15:30","BOY&GIRL","Techno",62),
 ("atmosphere","15:30","17:00","Mha Iri","Melodic techno",68),
 ("atmosphere","17:00","18:30","Callush","Hard techno",70),
 ("atmosphere","18:30","19:30","Hannah Laing",None,None),
 ("atmosphere","19:30","20:30","BYORN",None,None),
 ("atmosphere","20:30","21:30","Dyen b2b Mad...","Hard techno",78),
 ("atmosphere","21:30","23:00","Azyr","Hard techno",84),
 ("atmosphere","23:00","00:00","Onlynumbers","Hard techno",76),
 ("atmosphere","00:00","00:50","Holy Priest",None,None),
 ("planaxis","13:00","14:00","Domi Re","Psytrance",60),
 ("planaxis","14:00","15:00","Beat Controllers","Psytrance",62),
 ("planaxis","15:00","16:00","Vitor Falabella","Psytrance",64),
 ("planaxis","16:00","17:00","Firaga",None,None),
 ("planaxis","17:00","18:00","Somnia",None,None),
 ("planaxis","18:00","19:00","Phaxe","Psytrance",68),
 ("planaxis","19:00","20:00","Blazy","Psytrance",66),
 ("planaxis","20:00","21:00","Blastoyz","Psytrance",74),
 ("planaxis","21:00","22:00","Vegas","Psytrance",70),
 ("planaxis","22:00","23:00","Avalon","Psytrance",72),
 ("planaxis","23:00","00:00","Electric Universe","Psytrance",70),
 ("rose-garden","13:30","15:00","LICIA","Bass",58),
 ("rose-garden","15:00","16:00","Lucky Luke","Bass house",64),
 ("rose-garden","16:00","17:00","Goddard. & Dr...","Bass house",62),
 ("rose-garden","17:00","18:00","Ghengar","Dubstep / bass",64),
 ("rose-garden","18:00","19:00","ALLEYCVT","Dubstep / bass",64),
 ("rose-garden","19:00","20:00","Basstripper","Drum & bass",68),
 ("rose-garden","20:00","21:00","Jessica Audiff...","Bass",62),
 ("rose-garden","21:00","22:00","Riot Ten","Dubstep",68),
 ("rose-garden","22:00","23:00","BOU + B LIVE ...","Drum & bass",70),
 ("rose-garden","23:00","00:00","Borgore","Dubstep",66),
 ("rose-garden","00:00","01:00","Sullivan King","Dubstep / metal",66),
 ("celestia","13:30","15:00","Saar Kuus","House",58),
 ("celestia","15:00","16:30","AAT","Melodic techno",60),
 ("celestia","16:30","18:30","Mark Knight","House",74),
 ("celestia","18:30","20:00","Belters Only","House / rave",68),
 ("celestia","20:00","21:30","Ruze b2b Ranger Trucco","House",64),
 ("celestia","21:30","23:00","Mr. Belt & Wezol","House",70),
 ("cage","13:00","14:00","TOXIC TWINS","Hard techno",70),
 ("cage","14:00","15:00","TODIEFOR","Techno",66),
 ("cage","15:00","16:00","IMHAPPY","Hard techno",68),
 ("cage","16:00","17:00","NATTE VISSTICK","Hard / fun",72),
 ("cage","17:00","18:00","DJ FURAX",None,None),
 ("cage","18:00","19:00","PARTYRAISER ...","Uptempo hardcore",76),
 ("cage","19:00","20:00","DRS b2b SAN...","Hardcore",72),
 ("cage","20:00","21:00","LEKKERFACES","Hard techno",70),
 ("cage","21:00","22:00","YOSHIKO","Hard techno",72),
 ("cage","22:00","23:00","TERRORCLOWN","Uptempo hardcore",74),
 ("elixir","13:00","14:30","Rosh","Eclectic",58),
 ("elixir","14:30","16:00","Brooke Bailey b2b Taliyah ...","Eclectic",60),
 ("elixir","16:00","17:00","Valentino Ignoto","House",60),
 ("elixir","17:00","18:00","Iris Rooth","House",62),
 ("elixir","18:00","19:00","Miro","Eclectic",60),
 ("elixir","19:00","20:00","Nems","Eclectic",62),
 ("elixir","20:00","21:00","$hirak","Club / urban",66),
 ("elixir","21:00","22:00","Flash","Eclectic",62),
 ("elixir","22:00","23:00","Dany Neville","Eclectic",64),
 ("elixir","23:00","00:00","Irwan","Club / urban",62),
 ("elixir","00:00","01:00","Cham b...","Eclectic",58),
 ("melodia","14:00","15:30","Joulie","Melodic house",58),
 ("melodia","15:30","17:00","L-Fêtes","House",58),
 ("melodia","17:00","19:15","Planet Groove DJ's","House / disco",60),
 ("melodia","19:15","20:00","Eko Roo...","House",58),
 ("melodia","20:00","22:00","John Noseda","House",64),
 ("melodia","22:00","00:00","Jeroen Delodder","House",62),
 ("house-of-fortune","13:00","14:00","Reygel","House",58),
 ("house-of-fortune","14:00","15:00","Alan Alvarez ...","House",58),
 ("house-of-fortune","15:00","16:00","Martin Trevy","House",60),
 ("house-of-fortune","16:00","17:00","Vinne","EDM",62),
 ("house-of-fortune","17:00","18:00","Ely Oaks","EDM",60),
 ("house-of-fortune","18:00","19:00","ELFIGO",None,None),
 ("house-of-fortune","19:00","20:00","Telykast","EDM",62),
 ("house-of-fortune","20:00","21:00","Didi Han","House",64),
 ("house-of-fortune","21:00","22:00","MEGURU","House",62),
 ("rave-cave","13:00","14:30","Sanne Dammers","Tech house",60),
 ("rave-cave","14:30","16:00","Leesa","Tech house",60),
 ("rave-cave","16:00","17:30","VIKTÖR b2b MZDZ","Tech house",64),
 ("rave-cave","17:30","18:30","Lou8","Tech house",62),
 ("rave-cave","18:30","19:30","Jared","Tech house",62),
 ("rave-cave","19:30","20:30","Xijaro & Pitch","Trance",64),
 ("rave-cave","20:30","22:00","Mr. Joy","Tech house",64),
 ("rave-cave","22:00","23:00","Mairee","Tech house",66),
 ("rave-cave","23:00","00:00","Bisoux b2b Je...","Tech house",62),
 ("moose-bar","16:00","19:00","Jo Cox","Eclectic",60),
 ("moose-bar","19:00","20:00","Otto Wunderbar","Après / party",64),
 ("moose-bar","20:00","00:00","The Bobmeister","Après / party",66),
]

def js(v): return '"' + v.replace('"','\\"') + '"'
recs, artists = [], {}
for stage, st, en, a, g, e in T:
    if g is None: g = genre_w1.get(a, "?")
    pick = "rec" if a == "Openingsshow" else ""
    recs.append(f'  {{day:1, stage:{js(stage)}, artist:{js(a)}, start:"{st}", end:"{en}", pick:"{pick}", genre:{js(g)}}},')
    if a not in artists:
        artists[a] = art_w1.get(a) or (e if e is not None else 50, "")
TIMETABLE_JS = ("// TML Weekend 2 — Friday 24 July, transcribed from Bart's screenshot.\n"
  "// Picks: none yet — Jesse levert zijn favorieten aan.\n"
  "// Schema per set: {day, stage, artist, start, end, pick:\"must\"|\"rec\"|\"\", genre}\n"
  "// Times \"HH:MM\"; hours < 06:00 belong to the previous festival day.\n"
  "const TIMETABLE = [\n" + "\n".join(recs) + "\n];")
arts = "\n".join(f'  {js(a)}: {{ energy:{v[0]}{", note:"+js(v[1]) if v[1] else ""} }},'
                 for a, v in sorted(artists.items(), key=lambda kv: kv[0].lower()))
ARTISTS_JS = ("// Heuristic energy 0-100; W1 profiles reused where the artist matches.\n"
  "const ARTISTS = {\n" + arts + "\n};")

s = s.replace("<title>TML W1 — Dance Energy</title>", "<title>TML W2 — Jesse</title>")
s = s.replace("<h1>TML W1 · DANCE ENERGY</h1>", "<h1>TML W2 · JESSE</h1>")
s = re.sub(r'const DAY_DATES = \{[^}]*\};', 'const DAY_DATES = { 1:"2026-07-24" };', s)
s = re.sub(r'const DAY_LABELS = \{[^}]*\};', 'const DAY_LABELS = { 1:"Vr 24" };', s)
s = re.sub(r'// Updated official W1 timetable.*?const TIMETABLE = \[.*?\n\];', lambda m: TIMETABLE_JS, s, flags=re.S)
s = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', lambda m: ARTISTS_JS, s, flags=re.S)
# countdown + sim buttons
s = s.replace('Do 16 juli (The Gathering) vanaf 14:00, hoofdterrein vanaf vr 17.`', 'Vr 24 juli (Weekend 2) vanaf 13:00.`')
s = s.replace('tot Tomorrowland W1.', 'tot Tomorrowland W2.')
s = s.replace('''        <a class="chip" href="?now=2026-07-17T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-07-18T23:00">▶︎ Za 23:00</a>
        <a class="chip" href="?now=2026-07-17T21:30&rain=demo">🌧 Regen-demo</a>''',
'''        <a class="chip" href="?now=2026-07-24T18:00">▶︎ Vr 18:00</a>
        <a class="chip" href="?now=2026-07-24T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-07-24T21:30&rain=demo">🌧 Regen-demo</a>''')
# tests
NEW_TESTS = '''function runTests(){
  const get=(a)=>TIMETABLE.find(s=>s.artist===a);
  const results=[];
  const ok=(name,cond)=>results.push((cond?"✅ ":"❌ ")+name);
  ok(`131 sets geladen`, TIMETABLE.length===131);
  ok(`alle stages bekend`, TIMETABLE.every(s=>STAGES[s.stage]));
  ok(`alle artiesten hebben energie`, TIMETABLE.every(s=>ARTISTS[s.artist]));
  const azyr = scoreSet(get("Azyr"), null, wx, false);
  const joa = scoreSet(get("JOA"), null, wx, false);
  ok(`avond Azyr (binnen) [${azyr}] > middag-opener [${joa}]`, azyr>joa);
  const tL = new Date("2026-07-24T22:00:00");
  const rainWx = { minutely:[{t:tL, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  ok(`binnen stijgt bij regen`, scoreSet(get("Azyr"), tL, rainWx, true) > scoreSet(get("Azyr"), tL, {minutely:[],hourly:[]}, true));
  ok(`open main stort in bij regen`, scoreSet(get("Alok"), tL, {minutely:[],hourly:[]}, true) > scoreSet(get("Alok"), tL, rainWx, true));
  const mk = get("Mark Knight");
  const ms = setDate(mk,"start");
  const earlyRain = { minutely:[0,15,30].map(m=>({t:new Date(ms.getTime()+m*60000), mm:1.0})), hourly:[], ts:new Date(), stale:false };
  ok(`slechtste kwartier telt over hele set`, scoreSetWx(mk, earlyRain) < scoreSet(mk, null, wx, false));
  console.log("W2-Jesse engine tests:\\n"+results.join("\\n"));
  if(results.some(r=>r.startsWith("❌"))) alert("Engine tests FAILED — zie console");
}'''
s = re.sub(r'function runTests\(\)\{.*?\n\}', lambda m: NEW_TESTS, s, flags=re.S)

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
for f in ["2026-07-24", "Vr 24", "Azyr", "W2 · JESSE"]:
    assert f in s, f
print(f"jesse/index.html: {len(recs)} sets, {len(artists)} artiesten")
