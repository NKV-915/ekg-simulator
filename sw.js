const CACHE_NAME = 'ekg-sim-v52';
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
  './ekg_perikardtamponade.png',
  './ekg_perikarditis.png',
  './ekg_wpw.png',
  './ekg_s1_q3_t3.png',
  './ekg_stemi_rechts.png',
  './ekg_stemi_haupt.png',
  './ekg_long_qt.png',
  './ekg_hyperkaliaemie.png',
  './ekg_dewinter.png',
  './ekg_wellens.png',
  './ekg_stemi_hinten.png',
  './ekg_sinus_tachy.png',
  './ekg_sinus_brady.png',
  './ekg_vhf.png',
  './ekg_av_lll.png',
  './ekg_av_ll_mobitz.png',
  './ekg_av_ll_wenckebach.png',
  './ekg_av_l.png',
  './ekg_vt.png',
  './ekg_svt.png',
  './alarm.mp3',
  './stat.mp3',
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