const CACHE_NAME = "karuta-v7";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
  "./audio/a.mp3",
  "./audio/i.mp3",
  "./audio/u.mp3",
  "./audio/e.mp3",
  "./audio/o.mp3",
  "./audio/ka.mp3",
  "./audio/ki.mp3",
  "./audio/ku.mp3",
  "./audio/ke.mp3",
  "./audio/ko.mp3",
  "./audio/sa.mp3",
  "./audio/shi.mp3",
  "./audio/su.mp3",
  "./audio/se.mp3",
  "./audio/so.mp3",
  "./audio/ta.mp3",
  "./audio/chi.mp3",
  "./audio/tsu.mp3",
  "./audio/te.mp3",
  "./audio/to.mp3",
  "./audio/na.mp3",
  "./audio/ni.mp3",
  "./audio/nu.mp3",
  "./audio/ne.mp3",
  "./audio/no.mp3",
  "./audio/ha.mp3",
  "./audio/hi.mp3",
  "./audio/fu.mp3",
  "./audio/he.mp3",
  "./audio/ho.mp3",
  "./audio/ma.mp3",
  "./audio/mi.mp3",
  "./audio/mu.mp3",
  "./audio/me.mp3",
  "./audio/mo.mp3",
  "./audio/ya.mp3",
  "./audio/yu.mp3",
  "./audio/yo.mp3",
  "./audio/ra.mp3",
  "./audio/ri.mp3",
  "./audio/ru.mp3",
  "./audio/re.mp3",
  "./audio/ro.mp3",
  "./audio/wa.mp3",
  "./audio/wo.mp3",
  "./audio/n.mp3"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      for (const asset of ASSETS) {
        try {
          await cache.add(asset);
        } catch (error) {
          console.error("SW skip missing asset:", asset, error?.message || error);
        }
      }
    }),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key)),
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  // Network-first for index.html so edits show up immediately
  if (url.pathname.endsWith("/") || url.pathname.endsWith("/index.html")) {
    event.respondWith(
      fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return networkResponse;
      }).catch(() => caches.match(event.request))
    );
    return;
  }
  // Cache-first for everything else (audio, icons, etc.)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || event.request.method !== "GET") {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseToCache));
        return networkResponse;
      });
    }),
  );
});
