const CACHE_NAME = 'ekg-sim-v20';
const ASSETS = [
  './', 
  './index.html', 
  './monitor.html', 
  './observer.html', 
  './control.html', 
  './manifest.json',
  './ekg_sample.png'
];

self.addEventListener('install', (e) => {
  self.skipWaiting(); // Zwingt den neuen Service Worker sofort aktiv zu werden
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key); // Löscht alle alten Caches automatisch
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});