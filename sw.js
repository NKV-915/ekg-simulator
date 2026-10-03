self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('ekg-sim-v11').then((cache) => {
      return cache.addAll(['./', './index.html', './monitor.html', './observer.html', './control.html', './manifest.json']);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});