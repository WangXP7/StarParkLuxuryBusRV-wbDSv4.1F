// Verify the interactive page: load, console errors, exterior / interior shots.
const { chromium } = require('playwright-core');
const EXE = 'C:/Users/USER/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe';
const URL = process.argv[2] || 'http://127.0.0.1:8137/index.html';
const OUT = process.argv[3] || 'tools/shots';

(async () => {
  const fs = require('fs');
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    executablePath: EXE, headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
           '--ignore-gpu-blocklist', '--enable-webgl', '--disable-dev-shm-usage']
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [], logs = [];
  page.on('console', m => { logs.push(m.type() + ': ' + m.text()); if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  page.on('requestfailed', r => errs.push('REQFAIL: ' + r.url() + ' ' + (r.failure() || {}).errorText));

  await page.goto(URL, { waitUntil: 'load', timeout: 60000 });

  // wait for the loading overlay to disappear (model parsed)
  try {
    await page.waitForFunction(() => !document.getElementById('boot'), null,
      { timeout: 90000, polling: 300 });
    console.log('MODEL: loaded');
  } catch (e) {
    console.log('MODEL: TIMEOUT — boot overlay still present');
  }
  await page.waitForTimeout(2500);
  await page.screenshot({ path: OUT + '/web_01_exterior.png' });
  console.log('shot exterior');

  // roof kit off
  await page.click('#btnRoof'); await page.waitForTimeout(900);
  await page.screenshot({ path: OUT + '/web_02_noroof.png' });
  await page.click('#btnRoof'); await page.waitForTimeout(600);

  // x-ray
  await page.click('#btnXray'); await page.waitForTimeout(1000);
  await page.screenshot({ path: OUT + '/web_03_xray.png' });
  await page.click('#btnXray'); await page.waitForTimeout(800);

  // interior via the dock
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('.dbtn')].find(e => e.textContent.includes('驾驶舱'));
    if (b) b.click();
  });
  await page.waitForTimeout(2200);
  await page.screenshot({ path: OUT + '/web_04_cockpit.png' });
  console.log('shot cockpit');

  await page.evaluate(() => {
    const b = [...document.querySelectorAll('.dbtn')].find(e => e.textContent.includes('会客区'));
    if (b) b.click();
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: OUT + '/web_05_lounge.png' });
  console.log('shot lounge');

  await page.evaluate(() => {
    const b = [...document.querySelectorAll('.dbtn')].find(e => e.textContent.includes('卧铺'));
    if (b) b.click();
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: OUT + '/web_06_bedroom.png' });
  console.log('shot bedroom');

  console.log('--- console errors (' + errs.length + ') ---');
  errs.slice(0, 12).forEach(e => console.log('  ' + e));
  console.log('--- sample logs ---');
  logs.slice(0, 8).forEach(l => console.log('  ' + l));

  await browser.close();
})();
