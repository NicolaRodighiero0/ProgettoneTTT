// service-worker.js

const STATIC_CACHE  = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';
const OFFLINE_PAGE  = '/offline.html';

const STATIC_ASSETS = [
  '/',                // index.html
  OFFLINE_PAGE,
  '/css/home.css',
  '/js/home.js',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  // aggiungi qui tutte le tue risorse statiche...
];

self.addEventListener('install', evt => {
  // metti in cache tutte le risorse statiche
  evt.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', evt => {
  // pulisci le cache vecchie
  evt.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys
        .filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
        .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', evt => {
  const req = evt.request;
  const url = new URL(req.url);

  // 1) Static assets: cache-first
  if (url.origin === location.origin && req.destination !== 'document') {
    evt.respondWith(cacheFirst(req));
    return;
  }

  // 2) API calls: network-and-cache
  if (req.url.includes('/api/')) {
    evt.respondWith(networkAndCache(req));
    return;
  }

  // 3) HTML pages: network-first, poi cache della stessa pagina, poi offline.html
  if (req.headers.get('accept')?.includes('text/html')) {
    evt.respondWith(networkFirst(req));
    return;
  }

  // tutte le altre richieste (es. font), lasciale andare normalmente
});

async function cacheFirst(req) {
  const cached = await caches.match(req);
  return cached || fetch(req);
}

async function networkAndCache(req) {
  const cache = await caches.open(DYNAMIC_CACHE);
  try {
    const res = await fetch(req);
    cache.put(req, res.clone());
    return res;
  } catch {
    return cache.match(req);
  }
}

async function networkFirst(req) {
  const cache = await caches.open(DYNAMIC_CACHE);
  try {
    const fresh = await fetch(req);
    cache.put(req, fresh.clone());
    return fresh;
  } catch (err) {
    // se offline, prova a prendere la stessa pagina dalla cache
    const cached = await cache.match(req, {ignoreSearch: true});
    if (cached) return cached;
    // altrimenti mostra la pagina offline generica
    return caches.match(OFFLINE_PAGE);
  }
}
