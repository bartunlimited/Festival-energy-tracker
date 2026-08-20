#!/usr/bin/env python3
"""Generate lowlands/index.html — Lowlands 2026, 21-23 aug, Biddinghuizen.
Alleen Alpha is buiten (Bart); de rest is tent/hal."""
import re, os

SRC = "/home/user/Festival-energy-tracker/index.html"
OUT = "/home/user/Festival-energy-tracker/lowlands"
os.makedirs(OUT, exist_ok=True)
s = open(SRC, encoding="utf-8").read()

# (dag, stage, start, eind, artiest, genre, energie, pick)
T = [
 # ---------------- VRIJDAG 21 ----------------
 (1,"alpha","14:00","15:30","Amyl and the Sniffers","Punk",72,""),
 (1,"alpha","16:00","17:30","Antoon","NL pop / rap",62,""),
 (1,"alpha","18:15","19:45","Kneecap","Hiphop",76,""),
 (1,"alpha","20:15","21:45","Parcels","Disco / live",70,""),
 (1,"alpha","22:40","00:00","New Wave","NL hiphop",74,""),
 (1,"bravo","13:00","15:00","Nusantara Beat","Psych / world",55,""),
 (1,"bravo","15:00","17:00","Adéla","Pop",55,""),
 (1,"bravo","17:00","19:15","Nu Genea Live Band","Italo disco / live",68,""),
 (1,"bravo","19:15","21:30","Willem","NL pop",60,""),
 (1,"bravo","21:30","23:00","Viagra Boys","Post-punk",74,""),
 (1,"bravo","23:00","00:30","S-Candalo","Club",68,""),
 (1,"bravo","00:30","02:00","Chloé Caillet","House",76,"rec"),
 (1,"bravo","02:00","03:30","Ben UFO","Eclectic / techno",80,"rec"),
 (1,"bravo","03:30","05:00","Identified Patient","Industrial / EBM",78,"rec"),
 (1,"heineken","13:15","15:15","Skye Newman","Soul / pop",55,""),
 (1,"heineken","15:15","17:15","Leisure","Indie / soul",55,""),
 (1,"heineken","17:15","19:30","JPEGMAFIA","Experimental hiphop",70,""),
 (1,"heineken","19:30","21:30","Blood Orange","R&B / indie",58,""),
 (1,"heineken","21:30","00:00","Richie Hawtin: DEX EFX X0X","Minimal techno",80,"rec"),
 (1,"heineken","00:00","03:00","Basshall: Kybba, Tribal Kush & Nems","Global bass",66,""),
 (1,"lima","12:15","13:15","Romy","Dance pop",64,""),
 (1,"lima","13:15","14:15","Liz Rose","Pop",55,""),
 (1,"lima","14:15","16:15","Susobrino","Global club",62,""),
 (1,"lima","16:15","18:30","Dove Ellis","Pop",55,""),
 (1,"lima","18:30","20:30","Ana Frango Elétrico","Brazilian pop",58,""),
 (1,"lima","20:30","22:30","Zeyne","Arabic pop",55,""),
 (1,"lima","22:30","00:00","Fulu Miziki","Afro punk / live",66,""),
 (1,"lima","00:00","01:30","Het Alternatief","NL feest",68,""),
 (1,"india","11:30","14:00","Yoga","Yoga",12,""),
 (1,"india","14:00","16:00","Jet van der Steen","NL pop",58,""),
 (1,"india","16:00","18:15","Joy (Anonymous)","House / live",70,""),
 (1,"india","18:15","20:30","COBRAH","Hyperpop / club",72,""),
 (1,"india","20:30","22:30","President","Club",60,""),
 (1,"india","22:30","00:00","FCUKERS","Dance-punk",70,""),
 (1,"india","00:00","01:30","Mary Lake","Techno",74,""),
 (1,"india","01:30","03:00","Freddy K","Hard techno",84,"must"),
 (1,"india","03:00","05:00","Marrøn","Hard techno",82,"must"),
 (1,"x-ray","12:30","14:30","Chalk","Post-punk / electronic",60,""),
 (1,"x-ray","14:30","16:15","Radio Z","Indie",58,""),
 (1,"x-ray","16:15","18:00","Rose Gray","Dance pop",66,""),
 (1,"x-ray","18:00","19:50","Sons","Rock",60,""),
 (1,"x-ray","19:50","21:45","Gurriers","Post-punk",64,""),
 (1,"x-ray","21:45","23:00","James K","Experimenteel",52,""),
 (1,"x-ray","23:00","00:30","Bassvictim","Club / hyper",68,""),
 (1,"x-ray","00:30","02:00","Violent Magic Orchestra","Black metal / rave",70,""),
 (1,"x-ray","02:00","03:00","Kaboutertje Put Lucht","Rave",72,""),
 (1,"x-ray","03:00","05:00","Gysèle","Club",70,""),
 (1,"hacienda","12:30","14:30","Kim","Club",58,""),
 (1,"hacienda","14:30","16:30","Josefine","Club",58,""),
 (1,"hacienda","16:30","18:30","Charmaine","Club",60,""),
 (1,"hacienda","18:30","20:30","Lashanti","Afro / club",62,""),
 (1,"hacienda","20:30","22:00","Jea","Club",60,""),
 (1,"hacienda","22:00","23:30","Tins","Club",62,""),
 (1,"hacienda","23:30","01:00","Tienson","House",66,""),
 (1,"hacienda","01:00","03:00","Dam Swindle","House",76,"rec"),
 (1,"hacienda","03:00","05:00","Laura Meester","House / club",70,""),
 (1,"adonis","10:45","12:00","Bakkie LLit","Literatuur",10,""),
 (1,"adonis","12:00","13:30","Flip the Script!","Literatuur",10,""),
 (1,"adonis","13:30","15:00","Wat Nu? Verzet!","Literatuur",10,""),
 (1,"adonis","15:00","16:30","Mensen Zeggen Dingen","Literatuur",10,""),
 (1,"adonis","16:30","17:30","Ayoub Kharkhach","Comedy",20,""),
 (1,"adonis","17:30","18:30","Janneke de Bijl","Comedy",24,"rec"),
 (1,"adonis","18:30","19:30","Mark Waumans","Comedy",20,""),
 (1,"adonis","22:00","04:00","Adonis Queer Club","Queer club / dance",76,"rec"),
 (1,"adonis","19:30","20:30","Marie Koet","Comedy",20,""),
 # ---------------- ZATERDAG 22 ----------------
 (2,"alpha","14:00","15:30","Kelis","Pop / R&B",70,""),
 (2,"alpha","16:00","17:30","S10","NL pop",64,""),
 (2,"alpha","18:15","19:45","Major Lazer","EDM / dancehall",82,"rec"),
 (2,"alpha","20:30","22:00","Sombr","Indie pop",62,""),
 (2,"alpha","22:30","00:00","Tyler, The Creator","Hiphop",80,""),
 (2,"bravo","13:00","15:00","José González","Folk",45,""),
 (2,"bravo","15:00","17:00","Zimmer90","NL pop",58,""),
 (2,"bravo","17:00","19:15","IJsland","NL indie",58,""),
 (2,"bravo","19:15","21:15","Geese","Rock",62,""),
 (2,"bravo","21:15","23:00","Eefje de Visser","NL electropop",66,""),
 (2,"bravo","23:00","00:30","Afra","Club",70,""),
 (2,"bravo","00:30","02:00","Helena Hauff","Electro / industrial",86,"must"),
 (2,"bravo","02:00","03:30","Héctor Oaks","Hard techno",84,"rec"),
 (2,"bravo","03:30","05:00","Boys Noize","Electro / techno",80,"rec"),
 (2,"heineken","11:30","13:15","Soul Line Dance Workshop","Workshop",30,""),
 (2,"heineken","13:15","15:15","Milo Laat Het Lukken","NL pop",52,""),
 (2,"heineken","15:15","17:15","Ravyn Lenae","R&B",55,""),
 (2,"heineken","17:15","19:30","Pale Jay","Soul",50,""),
 (2,"heineken","19:30","21:45","Nia Archives","Jungle / dnb",74,""),
 (2,"heineken","21:45","00:00","Royal Blood","Rock",72,""),
 (2,"heineken","00:00","01:30","Lambrini Girls","Punk",70,""),
 (2,"heineken","01:30","03:00","TLM","Club",66,""),
 (2,"lima","12:15","14:15","La Tanya Alberto","Soul",55,""),
 (2,"lima","14:15","16:15","Koshin Moon","Psych / world",55,""),
 (2,"lima","16:15","18:25","Il Mago del Gelato","Italo / world",58,""),
 (2,"lima","18:25","20:40","Tyler Ballgame","Pop",58,""),
 (2,"lima","20:40","22:30","Fauna","World",58,""),
 (2,"lima","22:30","00:00","Ácido Pantera","Latin club",66,""),
 (2,"lima","00:00","01:30","Olá Brazil!","Braziliaans feest",68,""),
 (2,"india","11:30","14:15","Yoga","Yoga",12,""),
 (2,"india","14:15","16:15","Violet Grohl","Rock",58,""),
 (2,"india","16:15","18:20","Keo","Pop",58,""),
 (2,"india","18:20","20:30","Chloe Qisha","Pop",60,""),
 (2,"india","20:30","22:30","Zep","NL rap",60,""),
 (2,"india","22:30","00:00","Maey","NL pop",62,""),
 (2,"india","00:00","01:00","SMIB","NL rap / club",68,""),
 (2,"india","01:00","02:15","S!RENE","Hard club",74,""),
 (2,"india","02:15","03:30","Waxfiend","Hard techno",78,"rec"),
 (2,"india","03:30","05:00","Nala","Hard techno",80,"rec"),
 (2,"x-ray","14:00","15:40","Terzij de Horde","Black metal",58,""),
 (2,"x-ray","15:40","17:10","Guilt Trip","Hardcore",64,""),
 (2,"x-ray","17:10","18:45","Sophia Stel","Indie",55,""),
 (2,"x-ray","18:45","20:30","Tracey","Indie",58,""),
 (2,"x-ray","20:30","22:00","Speed","Hardcore",66,""),
 (2,"x-ray","22:00","23:30","Voices From The Lake","Ambient techno",55,""),
 (2,"x-ray","23:30","01:30","Skee Mask","Breaks / techno",70,""),
 (2,"x-ray","01:30","03:15","DJRUM","Experimenteel",62,""),
 (2,"x-ray","03:15","05:00","upsammy","Experimentele club",62,""),
 (2,"hacienda","12:30","16:30","Ketama Man","Reggae / dub",58,""),
 (2,"hacienda","16:30","18:30","Folake","Afro",60,""),
 (2,"hacienda","18:30","21:00","Yůsu","Afro / club",62,""),
 (2,"hacienda","21:00","23:30","Fiesta Macumba Soundsystem","Latin / afro feest",74,"rec"),
 (2,"hacienda","23:30","01:30","Rockefellababe","Club / eclectic",70,""),
 (2,"hacienda","01:30","03:00","Tera Kòrá","Afro club",70,""),
 (2,"hacienda","03:00","05:00","Lamsi","Club",68,""),
 (2,"adonis","10:45","12:00","Bakkie LLit","Literatuur",10,""),
 (2,"adonis","12:00","13:30","Rocking Books: Giphart × Goldbach","Literatuur",10,""),
 (2,"adonis","13:30","15:00","Wat Nu? Mystiek!","Literatuur",10,""),
 (2,"adonis","15:00","16:30","VPRO Club Lees","Literatuur",10,""),
 (2,"adonis","16:30","17:30","Alina Sharipova","Comedy",20,""),
 (2,"adonis","17:30","18:30","Teun de Vries","Comedy",20,""),
 (2,"adonis","18:30","19:30","Kees van Amstel","Comedy",24,"rec"),
 (2,"adonis","22:00","04:00","Adonis Queer Club","Queer club / dance",76,"rec"),
 (2,"adonis","19:30","20:30","Chicks in Dialogue","Comedy",20,""),
 # ---------------- ZONDAG 23 ----------------
 (3,"alpha","13:30","15:30","Noord Nederlands Orkest","Orkest",35,""),
 (3,"alpha","15:30","17:30","Hermanos Gutiérrez","Instrumentaal",45,""),
 (3,"alpha","17:30","19:30","Maribou State","Electronic live",70,"rec"),
 (3,"alpha","19:30","21:30","Turnstile","Hardcore",82,""),
 (3,"alpha","21:30","23:00","Lorde","Pop",76,""),
 (3,"bravo","12:30","14:30","Steel Pulse","Reggae",60,""),
 (3,"bravo","14:30","16:30","Sophie Straat","NL levenslied",66,""),
 (3,"bravo","16:30","18:30","Celeste","Soul",50,""),
 (3,"bravo","18:30","20:30","2hollis","Hyperpop / rage",70,""),
 (3,"bravo","20:30","22:30","Clipse","Hiphop",72,""),
 (3,"bravo","22:30","00:30","Saidah","Club",68,""),
 (3,"bravo","00:30","02:00","Benny Rodrigues","Classic house",82,"must"),
 (3,"bravo","02:00","03:30","KETTAMA","House / rave",80,"rec"),
 (3,"bravo","03:30","05:00","Nene H","Hard techno",80,"rec"),
 (3,"heineken","12:45","14:45","Merijn Scholten","NL pop",48,""),
 (3,"heineken","14:45","16:45","Buraka Som Sistema","Kuduro / global bass",76,""),
 (3,"heineken","16:45","18:45","Wunderhorse","Rock",62,""),
 (3,"heineken","18:45","20:45","Dijon","Soul / indie",55,""),
 (3,"heineken","20:45","23:00","Floating Points (live)","Electronic live",68,""),
 (3,"heineken","23:00","00:30","Iconic","Club",66,""),
 (3,"lima","12:00","13:45","Politie Warnsveld","Curiosum",40,""),
 (3,"lima","13:45","15:50","Anaiis","Soul",50,""),
 (3,"lima","15:50","17:45","Erin LeCount","Pop",55,""),
 (3,"lima","17:45","19:45","El Pony Pisador","Folk",55,""),
 (3,"lima","19:45","21:45","Bassolino","Italo / funk",60,""),
 (3,"lima","21:45","23:15","Compagnia La Giostra","World",58,""),
 (3,"lima","23:15","00:30","Vlooiencircus","Curiosum",55,""),
 (3,"india","11:30","13:30","Yoga","Yoga",12,""),
 (3,"india","13:30","15:30","Brother Wallace","Indie",55,""),
 (3,"india","15:30","17:30","Dikke","NL rap",62,""),
 (3,"india","17:30","19:30","Maruja","Post-punk / jazz",62,""),
 (3,"india","19:30","21:45","Naomi Sharon","Soul",50,""),
 (3,"india","21:45","23:15","Sor","Club",60,""),
 (3,"india","23:15","00:30","Flava D","UKG / bass",70,""),
 (3,"india","00:30","02:00","Skream & Benga","Dubstep",72,""),
 (3,"india","02:00","03:15","Andromedik","Drum & bass",72,""),
 (3,"india","03:15","05:00","Tantu Beats","Afro club",68,""),
 (3,"x-ray","12:45","14:45","Teen Mortgage","Rock",58,""),
 (3,"x-ray","14:45","15:20","World Peace","Hardcore",58,""),
 (3,"x-ray","15:20","16:45","DMT Femcels","Punk",55,""),
 (3,"x-ray","16:45","18:30","The Jane Remover","Hyperpop / experimenteel",60,""),
 (3,"x-ray","18:30","20:15","Teen Jesus and the Jean Teasers","Rock",60,""),
 (3,"x-ray","20:15","22:00","Ninajirachi","Club / hyperpop",70,""),
 (3,"x-ray","22:00","23:15","Geordie Greep","Art rock",64,""),
 (3,"x-ray","23:15","02:00","This Must Be The Pace w/ Theo Parrish","Deep house",72,"rec"),
 (3,"hacienda","12:30","14:30","Abiba","Club",58,""),
 (3,"hacienda","14:30","16:30","Sokoto b2b Pelanoir","Afro / club",64,""),
 (3,"hacienda","16:30","18:30","Eileen","Club",60,""),
 (3,"hacienda","18:30","20:30","Shady Lady","Club",62,""),
 (3,"hacienda","20:30","22:30","Kingdom Sound","Soundsystem",66,""),
 (3,"hacienda","22:30","00:30","AK Soundsystem","Soundsystem",68,""),
 (3,"hacienda","00:30","02:30","Deejay Abstract","Club",68,""),
 (3,"hacienda","02:30","04:00","Yucky","Club",66,""),
 (3,"adonis","10:45","12:00","Bakkie LLit","Literatuur",10,""),
 (3,"adonis","12:00","13:30","Darling, Dearest, Dead","Literatuur",10,""),
 (3,"adonis","13:30","15:00","Wat Nu? Fantasy!","Literatuur",10,""),
 (3,"adonis","15:00","16:30","Eindeloos Vertier","Literatuur",10,""),
 (3,"adonis","16:30","17:30","David van Rosmalen","Comedy",20,""),
 (3,"adonis","17:30","18:30","Martijn Crins","Comedy",20,""),
 (3,"adonis","18:30","19:30","Davine Perik","Comedy",20,""),
 (3,"adonis","22:00","04:00","Adonis Queer Club","Queer club / dance",76,"rec"),
 (3,"adonis","19:30","20:30","Jasper van der Veen","Comedy",20,""),
]

STAGES_JS = '''// Lowlands Biddinghuizen — Alpha is de enige buitenstage (Bart, aug 2026);
// alle andere podia zijn tent of hal.
const STAGES = {
  "alpha":    { name:"Alpha",         cover:"open",   size:"XL", dark:false, verified:true, fit:0.8, lightshow:true },
  "bravo":    { name:"Bravo",         cover:"indoor", size:"L",  dark:true,  verified:true },
  "heineken": { name:"Heineken Hall", cover:"indoor", size:"L",  dark:true,  verified:true },
  "india":    { name:"India",         cover:"indoor", size:"M",  dark:true,  verified:true },
  "x-ray":    { name:"X-Ray",         cover:"indoor", size:"M",  dark:true,  verified:true },
  "lima":     { name:"Lima",          cover:"indoor", size:"M",  dark:true,  verified:true },
  "hacienda": { name:"Hacienda",      cover:"indoor", size:"M",  dark:true,  verified:true },
  "adonis":   { name:"Adonis",        cover:"indoor", size:"M",  dark:true,  verified:true },  // overdag literatuur+comedy, vanaf 22:00 queer club
};'''

def js(v): return '"' + v.replace('"','\\"') + '"'
recs, artists = [], {}
for day, st, a, b, name, g, e, pick in T:
    recs.append(f'  {{day:{day}, stage:{js(st)}, artist:{js(name)}, start:"{a}", end:"{b}", pick:"{pick}", genre:{js(g)}}},')
    artists.setdefault(name, e)
TIMETABLE_JS = ("// Lowlands 2026, 21-23 aug, Biddinghuizen — getranscribeerd uit het officiële\n"
  "// blokkenschema (pdf). Eindtijden zijn afgeleid van de volgende set; de laatste\n"
  "// set per podium loopt tot sluitingstijd. Picks zijn Claude-suggesties uit Barts\n"
  "// muziek-DNA, niet zijn eigen markeringen.\n"
  "const TIMETABLE = [\n" + "\n".join(recs) + "\n];")
ARTISTS_JS = ("// Heuristische energie 0-100; Lowlands is deels een bandfestival, dus veel\n"
  "// acts scoren bewust laag (kijken, niet dansen).\n"
  "const ARTISTS = {\n" + "\n".join(f'  {js(a)}: {{ energy:{e} }},' for a,e in sorted(artists.items(), key=lambda kv: kv[0].lower())) + "\n};")

def rep(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new, 1)

rep("<title>TML W1 — Dance Energy</title>", "<title>Lowlands — Dance Energy</title>")
rep("<h1>TML W1 · DANCE ENERGY</h1>", "<h1>LOWLANDS · DANCE ENERGY</h1>")
s = re.sub(r'const DAY_DATES = \{[^}]*\};',
  'const DAY_DATES = { 1:"2026-08-21", 2:"2026-08-22", 3:"2026-08-23" };', s)
s = re.sub(r'const DAY_LABELS = \{[^}]*\};',
  'const DAY_LABELS = { 1:"Vr 21", 2:"Za 22", 3:"Zo 23" };', s)
s = re.sub(r'// Updated official W1 timetable.*?const TIMETABLE = \[.*?\n\];', lambda m: TIMETABLE_JS, s, flags=re.S)
s = re.sub(r'// Alle cover flags.*?const STAGES = \{.*?\n\};|// All cover flags verified by Bart.*?const STAGES = \{.*?\n\};', lambda m: STAGES_JS, s, flags=re.S)
s = re.sub(r'// Heuristic energy 0-100.*?const ARTISTS = \{.*?\n\};', lambda m: ARTISTS_JS, s, flags=re.S)

# nachtcurve: clubprogramma loopt tot 05:00
s = re.sub(r'  slotCurve: \[.*?\],\n',
  '  // Lowlands: overdag bands, na 00:30 clubprogramma tot 05:00\n'
  '  slotCurve: [ [12,15,0.35],[15,17,0.50],[17,19,0.65],[19,21,0.80],[21,24,1.00],\n'
  '               [24,27,0.95],[27,29,0.85],[29,31,0.70] ],\n', s, flags=re.S)

# weer: Biddinghuizen
rep('lat:51.087, lon:4.379, tz:"Europe/Brussels"', 'lat:52.441, lon:5.719, tz:"Europe/Amsterdam"')
rep("latitude=51.087&longitude=4.379", "latitude=52.441&longitude=5.719")
rep("timezone=Europe%2FBrussels", "timezone=Europe%2FAmsterdam")
rep('patroon van vandaag (Boom)', 'patroon van vandaag (Biddinghuizen)')

# uren 11..29 (11:00 -> 05:00)
rep("const hours=[]; for(let h=12;h<=25;h++) hours.push(h);",
    "const hours=[]; for(let h=11;h<=29;h++) hours.push(h);")
rep("fromHour:12, picksOnly:false, minEnergy:false, showPast:false };",
    "fromHour:11, picksOnly:false, minEnergy:false, showPast:false };")

# aftellen + simulatieknoppen
rep('const start = new Date(DAY_DATES[1]+"T12:00:00");', 'const start = new Date(DAY_DATES[1]+"T11:30:00");')
rep('tot Tomorrowland W1.<br>Do 16 juli (The Gathering) vanaf 14:00, hoofdterrein vanaf vr 17.`',
    'tot Lowlands.<br>Vr 21 aug vanaf 11:30, Biddinghuizen.`')
rep('`Weekend 1 zit erop. 🖤`', '`Lowlands zit erop. 🖤`')
rep('''        <a class="chip" href="?now=2026-07-17T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-07-18T23:00">▶︎ Za 23:00</a>
        <a class="chip" href="?now=2026-07-17T21:30&rain=demo">🌧 Regen-demo</a>''',
'''        <a class="chip" href="?now=2026-08-21T22:00">▶︎ Vr 22:00</a>
        <a class="chip" href="?now=2026-08-22T01:30">▶︎ Za nacht 01:30</a>
        <a class="chip" href="?now=2026-08-23T02:30">▶︎ Zo nacht 02:30</a>
        <a class="chip" href="?now=2026-08-21T20:00&rain=demo">🌧 Regen-demo</a>''')

NEW_TESTS = '''function runTests(){
  const get=(a)=>TIMETABLE.find(s=>s.artist===a);
  const results=[];
  const ok=(name,cond)=>results.push((cond?"✅ ":"❌ ")+name);
  ok(`''' + str(len(T)) + ''' sets geladen`, TIMETABLE.length===''' + str(len(T)) + ''');
  ok(`alle podia bekend`, TIMETABLE.every(s=>STAGES[s.stage]));
  ok(`alle acts hebben energie`, TIMETABLE.every(s=>ARTISTS[s.artist]));
  ok(`Alpha is het enige buitenpodium`,
     Object.values(STAGES).filter(v=>v.cover==="open").length===1 && STAGES["alpha"].cover==="open");
  const fk = scoreSet(get("Freddy K"), null, wx, false);
  const mid = scoreSet(get("Adéla"), null, wx, false);
  ok(`nachtclub Freddy K [${fk}] > middagband [${mid}]`, fk>mid);
  ok(`03:00 loopt door naar de volgende ochtend`,
     setDate(get("Marrøn"),"start").getDate()===22 && setDate(get("Marrøn"),"start").getHours()===3);
  const t = new Date("2026-08-22T01:00:00");
  const rainWx = { minutely:[{t, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  const ben = get("Ben UFO");
  ok(`binnen stijgt bij regen`, scoreSet(ben, t, rainWx, true) > scoreSet(ben, t, {minutely:[],hourly:[]}, true));
  const tA = new Date("2026-08-21T22:50:00");
  const rainA = { minutely:[{t:tA, mm:1.0}], hourly:[], ts:new Date(), stale:false };
  const nw = get("New Wave");
  ok(`Alpha (buiten) stort in bij regen`, scoreSet(nw, tA, {minutely:[],hourly:[]}, true) > scoreSet(nw, tA, rainA, true));
  ok(`comedy zit onder de clubnacht in dezelfde tent`,
     scoreSet(get("Janneke de Bijl"), null, wx, false) < scoreSet(get("Adonis Queer Club"), null, wx, false));
  console.log("Lowlands engine tests:\\n"+results.join("\\n"));
  if(results.some(r=>r.startsWith("❌"))) alert("Engine tests FAILED — zie console");
}'''
s = re.sub(r'function runTests\(\)\{.*?\n\}', lambda m: NEW_TESTS, s, flags=re.S)

open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(s)
for f in ["2026-08-21","Vr 21","Freddy K","LOWLANDS"]:
    assert f in s, f
print(f"lowlands/index.html: {len(T)} sets, {len(artists)} acts, "
      f"{sum(1 for x in T if x[7]=='must')} musts, {sum(1 for x in T if x[7]=='rec')} tips")
