// Poke Tracker service worker - written by pokemon_pipeline.py on every run;
// edit it there (SERVICE_WORKER), not here.
//  - The page and app files: fetched fresh whenever there's internet (so a
//    new build shows the next time the app opens), with the saved copy used
//    when offline or if the network takes longer than 4 seconds.
//  - Sprites: saved the first time they're shown, then loaded from the phone.
const VERSION = '14e9774e6df7';
const PAGE_CACHE = 'page-' + VERSION;
const SPRITE_CACHE = 'sprites-v1';
const SPRITE_MAX = 1500;
const SPRITE_HOSTS = ['raw.githubusercontent.com', 'play.pokemonshowdown.com'];
const APP_FILES = ['./pokemon_ui.html', './manifest.json',
  './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(PAGE_CACHE).then(c => c.addAll(APP_FILES.map(u => new Request(u, {cache: 'reload'}))))
    .then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('page-') && k !== PAGE_CACHE).map(k => caches.delete(k))))
    .then(trimSprites).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  const url = new URL(req.url);
  if(url.origin === location.origin) e.respondWith(networkFirst(req));
  else if(SPRITE_HOSTS.includes(url.hostname)) e.respondWith(spriteFirst(req));
});

async function networkFirst(req){
  const cache = await caches.open(PAGE_CACHE);
  const fresh = fetch(req, {cache: 'no-cache'}).then(res => {
    if(res.ok) cache.put(req, res.clone());
    return res;
  });
  const timeout = new Promise(res => setTimeout(res, 4000));
  try{
    const res = await Promise.race([fresh, timeout]);
    if(res) return res;
  }catch(err){ /* offline: use the saved copy */ }
  const saved = await cache.match(req, {ignoreSearch: true})
    || (req.mode === 'navigate' && await cache.match('./pokemon_ui.html'));
  return saved || fresh;
}

let puts = 0;
async function spriteFirst(req){
  const cache = await caches.open(SPRITE_CACHE);
  const saved = await cache.match(req.url);
  if(saved) return saved;
  try{
    // a CORS copy can be saved at its real size (and read by the page's canvas)
    const res = await fetch(req.url, {mode: 'cors', credentials: 'omit'});
    if(res.ok){
      await cache.put(req.url, res.clone());
      if(++puts % 50 === 0) trimSprites();
    }
    return res;
  }catch(err){
    return fetch(req);   // the host refused CORS: load it as normal, unsaved
  }
}

async function trimSprites(){
  const cache = await caches.open(SPRITE_CACHE);
  const keys = await cache.keys();
  await Promise.all(keys.slice(0, Math.max(0, keys.length - SPRITE_MAX)).map(k => cache.delete(k)));
}
