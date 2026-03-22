const CACHE = "oref-nerya-v3.1";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  // נתוני alerts — תמיד מהרשת (לא מהקאש)
  if (e.request.url.includes("raw.githubusercontent.com")) {
    e.respondWith(fetch(e.request).catch(() => new Response("{}", { headers: { "Content-Type": "application/json" } })));
    return;
  }
  // שאר הקבצים — קאש ראשון
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
