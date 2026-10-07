const CACHE_NAME = 'ekg-sim-v38';
const ASSETS = [
  './', 
  './index.html', 
  './monitor.html', 
  './observer.html', 
  './control.html', 
  './manifest.json',
  './ekg_sinus.png',
  './ekg_rbbb.png',
  './ekg_lbbb.png',
  './alarm.mp3',
  './stat.mp3',
  './beep.mp3',
  './blutdruck.mp3',
  './shock_charge.mp3',
  './shock_ready.mp3',
  './shock_admitted.mp3'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
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
            return caches.delete(key);
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