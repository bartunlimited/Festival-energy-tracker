// Render-helper voor ade_watch.py --render: haalt een JS-pagina op en dumpt de DOM.
//   node tools/ade_render.mjs <url>          → volledige HTML naar stdout
// NODE_PATH wijst naar de globale playwright (zie ade_watch.py).
import { existsSync } from 'node:fs';
import { createRequire } from 'node:module';

// Via require i.p.v. import: ESM negeert NODE_PATH, dus een globaal geïnstalleerde
// playwright zou anders niet gevonden worden.
const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  try {
    ({ chromium } = require('playwright-core'));
  } catch {
    console.error(
      'playwright niet gevonden. Installeer het (npm i -g playwright) of zet\n' +
      'NODE_PATH naar de map met node_modules (lokaal: /opt/node22/lib/node_modules).'
    );
    process.exit(1);
  }
}

const url = process.argv[2];
if (!url) {
  console.error('gebruik: node tools/ade_render.mjs <url>');
  process.exit(1);
}

// Lokaal staat chromium op een vast pad; in CI regelt Playwright dat zelf.
const exe = process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser = await chromium.launch(existsSync(exe) ? { executablePath: exe } : {});
const page = await browser.newPage({ viewport: { width: 1280, height: 2000 } });

await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });

// Cookiemuur wegklikken als die er is — anders blijft de lijst leeg.
for (const label of [/accept/i, /akkoord/i, /agree/i, /alles toestaan/i]) {
  const btn = page.getByRole('button', { name: label }).first();
  if (await btn.count().catch(() => 0)) {
    await btn.click({ timeout: 3000 }).catch(() => {});
    break;
  }
}

// Lazy loading: scrollen en "load more" klikken tot de lijst niet meer groeit.
//
// Let op: één ronde zonder groei betekent níét dat de lijst compleet is — het
// kan ook zijn dat het volgende blok nog onderweg is. Daarop afbreken leverde
// elke run een andere, afgekapte subset op (1246 events op 4 okt, 1197 op 9 okt,
// met 159 "verdwenen" events die gewoon nooit geladen waren). Pas afbreken na
// meerdere stabiele rondes achter elkaar, en na elke klik op het netwerk wachten
// in plaats van op een vaste timeout.
const countEvents = () =>
  page.evaluate(() => document.querySelectorAll('a[href*="/program/"]').length);

const STABLE_ROUNDS = 3;
let previous = -1;
let stable = 0;

for (let round = 0; round < 80; round++) {
  const now = await countEvents();
  if (now === previous) {
    if (++stable >= STABLE_ROUNDS) break;
  } else {
    stable = 0;
    previous = now;
  }

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  const more = page.getByRole('button', { name: /load more|meer|show more/i }).first();
  if (await more.count().catch(() => 0)) {
    await more.click({ timeout: 3000 }).catch(() => {});
  }
  // Wacht op de XHR van het volgende blok; valt terug op een vaste pauze als
  // het netwerk al stil was.
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(600);
}

const total = await countEvents();
if (stable < STABLE_ROUNDS) {
  // Niet stilgevallen binnen 80 rondes: de lijst is mogelijk nog niet compleet.
  // Hard falen, want een stil afgekapte lijst ziet er in de diff uit als
  // geannuleerde events.
  console.error(`ade_render: lijst groeide nog na 80 rondes (${total} events) — mogelijk incompleet`);
  await browser.close();
  process.exit(3);
}
console.error(`ade_render: ${total} event-links, stabiel na ${STABLE_ROUNDS} rondes`);

process.stdout.write(await page.content());
await browser.close();
