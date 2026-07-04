// Minimal service worker: app shell always loads offline.
// Same-origin: network-first (freshest tool after a push), cache fallback.
// Cross-origin (Open-Meteo) passes through untouched — the app has its own
// localStorage cache + stale indicator for weather.
const CACHE = "tml-energy-v1";
const ASSETS = ["./", "./index.html", "./manifest.json", "./icon-180.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return res;
      })
      // ignoreSearch: ?now=/?rain= simulator URLs also resolve offline
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
