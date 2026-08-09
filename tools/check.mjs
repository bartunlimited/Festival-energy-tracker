import { chromium } from 'playwright-core';

const file = 'file:///home/user/Festival-energy-tracker/index.html';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
const logs = [];
page.on('console', m => logs.push(m.text()));
page.on('pageerror', e => logs.push('PAGEERROR: ' + e.message));

// 1. tests + simulated Friday 22:00 + demo rain
await page.goto(file + '?test=1&now=2026-07-17T22:00&rain=demo');
await page.waitForTimeout(1500);
console.log('--- console ---\n' + logs.join('\n'));
console.log('\n--- clockline ---\n' + await page.textContent('#clockline'));
console.log('\n--- banners ---\n' + (await page.textContent('#banners')).trim());
console.log('\n--- NU view (first 900 chars) ---\n' + (await page.textContent('#view-nu')).trim().slice(0, 900));

// 2. schema view
await page.click('#tab-schema');
console.log('\n--- SCHEMA view (first 700 chars) ---\n' + (await page.textContent('#view-schema')).trim().slice(0, 700));

// 3. weer view
await page.click('#tab-weer');
console.log('\n--- WEER view (first 500 chars) ---\n' + (await page.textContent('#view-weer')).trim().slice(0, 500));

await page.screenshot({ path: '/tmp/claude-0/-home-user-Festival-energy-tracker/b9ed3677-b541-5bfb-8bbb-7c0719287221/scratchpad/nu-view.png', fullPage: false });
await page.click('#tab-nu');
await page.waitForTimeout(200);
await page.screenshot({ path: '/tmp/claude-0/-home-user-Festival-energy-tracker/b9ed3677-b541-5bfb-8bbb-7c0719287221/scratchpad/nu-rain.png' });
await browser.close();
