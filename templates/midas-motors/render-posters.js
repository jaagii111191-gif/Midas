// Renders one 1080×1350 PNG per entry in a JSON file of Midas Motors posters.
// Usage:  node templates/midas-motors/render-posters.js [data/midas-cars.json] [--out <dir>] [--scale 2]
//         (or the friendlier `npm run poster -- help`, see bin/midas-poster.js)
// Needs:  npm install   (or set CHROMIUM_PATH to an existing Chromium binary)
// Entry "template": "t1" (one photo, default) | "multi" (one car, several photos) | "lineup" (several cars)
// Output: reports/midas-posters/<id>.png unless --out is given
// Behind an intercepting HTTPS proxy, set IGNORE_HTTPS_ERRORS=1 so remote photos (https://…) load.
const { chromium } = require('playwright');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const root = path.resolve(__dirname, '..', '..');
const DEFAULT_OUT = path.join(root, 'reports', 'midas-posters');
const TEMPLATES = { t1: 'poster-t1.html', multi: 'poster-multi.html', lineup: 'poster-lineup.html' };
const CACHE_DIR = path.join(root, '.cache', 'photos');

function launchBrowser() {
  return chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
}
function newContext(browser, extra = {}) {
  return browser.newContext({
    ignoreHTTPSErrors: process.env.IGNORE_HTTPS_ERRORS === '1', // only for networks behind an intercepting proxy
    ...extra,
  });
}

// Local photo paths are relative to the repo root; downloaded URLs point at their cached copy.
function photoUrl(p, cache) {
  if (!p) return p;
  if (typeof p === 'object') return { ...p, src: photoUrl(p.src, cache) };
  if (cache && cache.has(p)) return cache.get(p);
  if (/^(https?:|data:|file:)/.test(p)) return p;
  return pathToFileURL(path.resolve(root, p)).href;
}
function resolvePhotos(entry, cache) {
  const e = { ...entry };
  if (e.photo) e.photo = photoUrl(e.photo, cache);
  if (Array.isArray(e.photos)) e.photos = e.photos.map(p => photoUrl(p, cache));
  if (Array.isArray(e.cars)) e.cars = e.cars.map(c => resolvePhotos(c, cache));
  return e;
}

function remoteUrls(entry, set = new Set()) {
  const add = p => { const src = p && (typeof p === 'object' ? p.src : p); if (src && /^https?:/.test(src)) set.add(src); };
  add(entry.photo);
  (entry.photos || []).forEach(add);
  (entry.cars || []).forEach(c => remoteUrls(c, set));
  return set;
}

// Downloads remote photos one at a time, with retries, into .cache/photos so a flaky network
// cannot leave holes in a poster. Returns a map of URL → file:// URL of the cached copy.
async function cacheRemotePhotos(context, urls) {
  const cache = new Map();
  if (!urls.size) return cache;
  fs.mkdirSync(CACHE_DIR, { recursive: true });
  const page = await context.newPage();
  for (const url of urls) {
    const ext = (path.extname(new URL(url).pathname) || '.jpg').toLowerCase();
    const file = path.join(CACHE_DIR, crypto.createHash('sha1').update(url).digest('hex').slice(0, 16) + ext);
    for (let attempt = 1; attempt <= 6 && !fs.existsSync(file); attempt++) {
      try {
        const resp = await page.goto(url, { waitUntil: 'commit', timeout: 45000 });
        if (resp && resp.ok()) fs.writeFileSync(file, await resp.body());
      } catch (e) { /* retried below */ }
      if (!fs.existsSync(file) && attempt < 6) await new Promise(r => setTimeout(r, 1000 * attempt));
    }
    if (fs.existsSync(file)) cache.set(url, pathToFileURL(file).href);
    else console.error('  ! photo could not be downloaded: ' + url);
  }
  await page.close();
  return cache;
}

// Renders each entry to <out>/<id>.png and returns the written paths.
async function renderEntries(entries, { out = DEFAULT_OUT, scale = 1, log = console.log } = {}) {
  fs.mkdirSync(out, { recursive: true });
  const browser = await launchBrowser();
  const written = [];
  try {
    const context = await newContext(browser, { viewport: { width: 1080, height: 1350 }, deviceScaleFactor: scale });
    const cache = await cacheRemotePhotos(context, entries.reduce((set, e) => remoteUrls(e, set), new Set()));
    const page = await context.newPage();
    page.on('console', m => { if (m.type() === 'error') console.error('  ! ' + m.text()); });
    await page.addInitScript(() => { window.__external = true; });
    for (const entry of entries) {
      const file = TEMPLATES[entry.template || 't1'];
      if (!file) { console.error(`✗ ${entry.id}: unknown template "${entry.template}"`); continue; }
      // Retry when a remote photo fails to load (flaky networks); local files fail fast and keep failing.
      let errors = 0;
      for (let attempt = 1; attempt <= 3; attempt++) {
        await page.goto(pathToFileURL(path.join(__dirname, file)).href, { waitUntil: 'load' });
        await page.evaluate(d => window.renderPoster(d), resolvePhotos(entry, cache));
        await page.waitForFunction(() => window.posterReady === true, null, { timeout: 60000 });
        errors = await page.evaluate(() => window.posterErrors || 0);
        if (!errors) break;
      }
      if (errors) console.error(`  ! ${entry.id}: ${errors} photo(s) still missing`);
      const target = path.join(out, `${entry.id}.png`);
      await (await page.$('#poster')).screenshot({ path: target });
      log('✓ ' + path.relative(process.cwd(), target));
      written.push(target);
    }
  } finally {
    await browser.close();
  }
  return written;
}

function readEntries(file) {
  return JSON.parse(fs.readFileSync(path.resolve(root, file), 'utf8')).cars;
}

module.exports = { root, DEFAULT_OUT, TEMPLATES, launchBrowser, newContext, renderEntries, readEntries };

if (require.main === module) {
  const opts = { data: 'data/midas-cars.json', out: DEFAULT_OUT, scale: 1 };
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--out') opts.out = path.resolve(argv[++i]);
    else if (argv[i] === '--scale') opts.scale = Number(argv[++i]) || 1;
    else opts.data = argv[i];
  }
  renderEntries(readEntries(opts.data), opts).catch(e => { console.error(e); process.exit(1); });
}
