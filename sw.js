self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('ekg-sim-v3').then((cache) => {
      return cache.addAll(['./', './index.html', './monitor.html', './control.html', './manifest.json']);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});