# Muziek-DNA — Bart

> **Status:** gereconstrueerd op 1 augustus 2026 uit de picks, energie-profielen en
> kalibraties in alle vijf de apps. Het oorspronkelijke design-document is verloren
> gegaan (nooit gecommit). **Bart: corrigeer wat niet klopt** — dit bestand is
> vanaf nu de bron voor alle toekomstige aanbevelingen.

---

## De kern in één alinea

Bart heeft een **brede** smaak met een duidelijk zwaartepunt in **techno**, maar hij
is geen purist: grote mainstage-namen met een show staan even hard in zijn musts als
Berghain-residents. De rode draad is niet één genre maar **de vloer**: muziek waar
gedanst wordt. Wat hij écht mijdt is een klein, scherp afgebakend hoekje —
hardstyle, dubstep/bass en psytrance — en dat mijdt hij consequent.

---

## Trefkans per genre (gemeten, niet geraden)

Uit de 391 sets van Tomorrowland W1, waarvan Bart er 127 markeerde:

| Genre-familie | Gemarkeerd | Sets | Trefkans |
|---|---:|---:|---:|
| Show / live (orkest, opening) | 5 | 5 | **100 %** |
| Techno (algemeen) | 21 | 26 | **81 %** |
| Hard / dark techno | 26 | 33 | **79 %** |
| Melodic techno | 14 | 24 | **58 %** |
| Trance | 2 | 4 | 50 % |
| Mainstage EDM / pop | 19 | 49 | 39 % |
| House / tech house | 37 | 140 | 26 % |
| Hardstyle / raw | 1 | 29 | **3 %** |
| Dubstep / bass / drum & bass | 0 | 17 | **0 %** |
| Psytrance | 0 | 11 | **0 %** |

**Lees dit zo:** techno in alle vormen is bijna altijd raak. House is zó ruim
vertegenwoordigd dat de lage trefkans niets zegt over de smaak — daar selecteert hij
op naam, niet op genre. Hardstyle, bass en psytrance zijn geen "minder vaak", maar
**vrijwel nooit** — die drie zijn de echte uitsluiting.

---

## Twee losse assen: energie ≠ pick

Dit is de belangrijkste nuance en het makkelijkst verkeerd te begrijpen:

- **Energie** = waar de *crowd* danst. Dat is de voorspelling van de app.
- **Pick** = wat *Bart* wil zien. Dat is iets anders.

Bewijs uit zijn eigen data: **Symphony Of Harmony** heeft energie **31** met de notitie
*"orkest — kijken, niet dansen"* en staat toch als **must**. **John Newman** (energie 49,
*"zang, geen dansvloer"*) staat als tip. Andersom scoort **Dimitri Vegas & Like Mike**
energie 65 met de notitie *"crowd beweegt, Bart-dislike staat los van energie"* — hoge
energie, bewust géén pick.

→ **Nooit een lage energie-score gebruiken als argument om iets niet aan te bevelen,
en nooit een hoge score als argument om iets wél aan te bevelen.** Het zijn twee vragen.

---

## Ankerpunten — zijn eigen musts

**Techno-kern:** Sara Landry · Amelie Lens · Nico Moreno · Anetha · Ben Klock ·
Charlotte de Witte · Indira Paganotto · BIIA b2b Charlie Sparks

**Mainstage/EDM-kern:** Martin Garrix · Calvin Harris · Alesso · Sebastian Ingrosso ·
The Chainsmokers · Armin van Buuren · John Summit · Lost Frequencies · Afrojack (tip)

**Buiten categorie:** Ofenbach · Olive Anguz · Symphony Of Harmony · de Mainstage-
openingsshow (17:30, elke dag een tip)

Die twee kernen naast elkaar zijn typerend: wie alleen de eerste rij ziet, beveelt
te smal aan.

---

## Uitsluitingen

1. **Dubstep, bass en drum & bass** — 0 van de 17 sets gemarkeerd. Nooit aanbevelen.
   (Borgore, Sullivan King, Riot Ten, ALLEYCVT, Camo & Krooked, de hele Rose Garden
   op W2-vrijdag.)
2. **Hardstyle / raw** — 1 van de 29. Behandel als uitgesloten, met één uitzondering:
   **rave-classics met een nostalgie-lading** wél (Mark With A K & MC Chucky:
   Classics Set is een tip).
3. **Psytrance** — 0 van de 11, ondanks hoge energie-scores. Vini Vici, Blastoyz,
   Neelix: niet markeren.
4. **Dimitri Vegas & Like Mike** — expliciete, persoonlijke dislike. Staat los van de
   energie-score en van de rest van zijn EDM-voorkeur.

---

## Wat hij zelf heeft gekalibreerd

Deze correcties komen rechtstreeks van Bart en zijn hard bewijs voor hoe hij denkt:

- **Atmosphere is binnen**, geen tent (TML).
- **Mainstage krijgt fit-override 0.8** — te groot om overal vol te dansen.
- **Lichtshow-bonus +0.20** voor de closing op Mainstage ná donker.
- **Regen telt op het slechtste kwartier** van een set, niet op het gemiddelde.
- **Awakenings:** Area Y is tent, B en C hebben een dak, de rest is buiten.
- **The Gathering** (TML donderdag) is buiten.
- **Henri PFR** ging van must naar tip zodra hij twee sets bleek te hebben — een pick
  hoort bij een moment, niet bij een naam.
- **Olive Anguz en Ofenbach** promoveerde hij zelf naar must; beide house/melodic op
  vrijdagavond, beide op hetzelfde tijdslot.
- **Illenium** staat als tip met het label *"eens kijken of het wat is"* — dat is
  nieuwsgierigheid, **geen** bewijs dat melodic bass in zijn smaak zit.

---

## Scoring-heuristiek (energie-as)

```
energie = genre-intensiteit (0–40)
        + settype (0–15)          b2b / live / closing
        + bekendheid (0–20)
        + reputatie (0–25)        default 12
```

De engine vermenigvuldigt dat vervolgens met stage-fit, tijdslot (dag- of nachtcurve),
weer (regen/zon/hitte/kou) en concurrentie van gelijktijdige sets. Zie
`docs/artist-energy-review.md` voor de volledige tabel van W1.

---

## Vuistregels voor een volgende sessie

1. **Markeer nooit stilzwijgend.** Picks die Claude bedenkt zijn *suggesties* en moeten
   als zodanig benoemd worden; Barts eigen picks zijn heilig en worden 1-op-1
   overgenomen bij nieuwe timetables.
2. **Techno na 21:00 in een donkere binnenzaal** is bijna altijd raak.
3. **Closing-slot van een grote mainstage-naam** is bijna altijd raak.
4. **Dubstep, hardstyle, psytrance** overslaan.
5. **Show/live/orkest** mag je aanbevelen als kijk-moment, maar zeg erbij dat het geen
   dansvloer is — die eerlijkheid waardeert hij (zie Illenium).
6. **Bij twijfel over een onbekende naam:** geef de aanbeveling mét de reden, dan
   corrigeert hij zelf. Dat werkt aantoonbaar goed.
