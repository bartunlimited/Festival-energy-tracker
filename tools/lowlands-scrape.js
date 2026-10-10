// Lowlands acts uitlezen vanuit je eigen browser.
//
// Waarom: de container waarin Claude draait mag lowlands.nl niet benaderen
// (netwerkpolicy van de remote omgeving). Jouw browser mag dat wel. Dit script
// leest de pagina die je toch al open hebt en zet het resultaat op je klembord,
// zodat je het in de chat kunt plakken.
//
// GEBRUIK
//   1. Open https://lowlands.nl/acts/ in Chrome of Safari
//   2. F12 (of ⌥⌘I) → tabblad "Console"
//   3. Plak het blok hieronder en druk op Enter
//   4. Wacht tot "→ gekopieerd naar klembord" verschijnt, dan ⌘V in de chat
//
// Chrome vraagt de eerste keer om "allow pasting" te typen. Safari: schakel
// eerst het ontwikkelaarsmenu in via Instellingen → Geavanceerd.

// ─────────────── 1. OVERZICHTSPAGINA: alle acts ───────────────
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // Lowlands laadt acts bij tijdens het scrollen: doorscrollen tot de pagina
  // niet meer groeit, en onderweg op een eventuele "laad meer"-knop klikken.
  let hoogte = 0, stabiel = 0;
  while (stabiel < 3) {
    window.scrollTo(0, document.body.scrollHeight);
    const meer = [...document.querySelectorAll("button, a")].find(
      (el) => /meer|more|load|toon/i.test(el.textContent || "") && el.offsetParent
    );
    if (meer) meer.click();
    await sleep(700);
    const nu = document.body.scrollHeight;
    stabiel = nu === hoogte ? stabiel + 1 : 0;
    hoogte = nu;
  }

  // Elke act heeft een eigen /acts/<slug>/ link. Pak per link de langste
  // tekst — dat is meestal naam + genre/dag-label.
  const gevonden = new Map();
  for (const a of document.querySelectorAll('a[href*="/acts/"]')) {
    const url = a.href.split("?")[0].replace(/\/$/, "");
    const slug = url.split("/acts/")[1];
    if (!slug || slug.includes("/")) continue;          // indexpagina zelf overslaan
    const tekst = (a.innerText || a.textContent || "").trim().replace(/\s+/g, " ");
    if (!tekst) continue;
    if (!gevonden.has(slug) || gevonden.get(slug).length < tekst.length) {
      gevonden.set(slug, tekst);
    }
  }

  const regels = [...gevonden].map(([slug, tekst]) => `${tekst}\t${slug}`).sort();
  const uit = regels.join("\n");
  console.log(`${regels.length} acts gevonden:\n\n${uit}`);
  try {
    await navigator.clipboard.writeText(uit);
    console.log("→ gekopieerd naar klembord");
  } catch {
    console.log("→ klembord geweigerd; selecteer de tekst hierboven en kopieer handmatig");
  }
})();

// ─────────────── 2. LOSSE ACT-PAGINA: omschrijving ───────────────
// Draai dit op bijvoorbeeld https://lowlands.nl/acts/adonis-ll26/
/*
(async () => {
  const titel = document.querySelector("h1")?.innerText?.trim() || document.title;
  const hoofd = document.querySelector("main, article, [role=main]") || document.body;
  const tekst = hoofd.innerText.replace(/\n{3,}/g, "\n\n").trim().slice(0, 4000);
  const uit = `# ${titel}\n${location.href}\n\n${tekst}`;
  console.log(uit);
  try { await navigator.clipboard.writeText(uit); console.log("→ gekopieerd naar klembord"); }
  catch { console.log("→ klembord geweigerd; kopieer handmatig"); }
})();
*/
