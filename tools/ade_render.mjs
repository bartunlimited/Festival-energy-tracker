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
const countEvents = () =>
  page.evaluate(() => document.querySelectorAll('a[href*="/program/"]').length);
let previous = -1;
for (let round = 0; round < 25; round++) {
  const now = await countEvents();
  if (now === previous) break;
  previous = now;
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  const more = page.getByRole('button', { name: /load more|meer|show more/i }).first();
  if (await more.count().catch(() => 0)) {
    await more.click({ timeout: 3000 }).catch(() => {});
  }
  await page.waitForTimeout(1200);
}

process.stdout.write(await page.content());
await browser.close();
