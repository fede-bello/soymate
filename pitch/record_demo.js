// Record the demo video shown on the demo slide, from the live app.
//
//   node pitch/record_demo.js [app-url]        (default http://18.206.176.19)
//
// Needs Node and Playwright with Chromium (`npm install playwright && npx playwright install chromium`).
// Writes pitch/deck/assets/demo_raw.webm; pitch/EDITING.md ("Re-record the demo video") has the ffmpeg
// steps that turn it into demo.mp4, demo.webm and demo_poster.jpg.
//
// What it shows: the Ghana farmer-saved example (many seeds), then the single seed labelled insect hole.
// To show other examples, change the button names in the two `click` lines (they match the sample
// cards' titles in the app).

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const URL = process.argv[2] || 'http://18.206.176.19';
const OUT_DIR = path.join(__dirname, 'deck', 'assets');
const W = 1920, H = 1080;

(async () => {
  const browser = await chromium.launch();
  const tmp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'soymate-rec-'));
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, recordVideo: { dir: tmp, size: { width: W, height: H } } });
  const page = await ctx.newPage();
  const pause = ms => page.waitForTimeout(ms);
  const scrollTo = async y => { await page.evaluate(y => window.scrollTo({ top: y, behavior: 'smooth' }), y); await pause(900); };
  // Wait for an analysis to finish: the "Finding and checking every seed" banner appears, then goes.
  const done = async () => {
    await page.waitForSelector('text=Finding and checking every seed', { timeout: 10000 }).catch(() => {});
    await page.waitForSelector('text=Finding and checking every seed', { state: 'detached', timeout: 180000 });
    await pause(800);
  };

  await page.goto(URL, { waitUntil: 'networkidle' });
  await pause(1500);
  await scrollTo(700); await pause(600);
  await page.getByRole('button', { name: /Ghana farmer-saved lot/ }).click();   // example 1: many seeds
  await scrollTo(0); await done(); await pause(3500);
  await scrollTo(420); await pause(3500);                                        // show the hand-count check
  await scrollTo(1000); await pause(700);
  await page.getByRole('button', { name: /labelled insect hole/ }).click();      // example 2: one seed
  await done(); await scrollTo(0); await pause(4500);

  const video = page.video();
  await ctx.close();
  await browser.close();
  const out = path.join(OUT_DIR, 'demo_raw.webm');
  fs.copyFileSync(await video.path(), out);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`wrote ${path.relative(process.cwd(), out)}`);
})();
