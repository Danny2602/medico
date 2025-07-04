self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('medico-cache').then((cache) => {
      return cache.addAll([
        '/',
        '/static/manifest.json',
        '/static/icons/icon-192x192.png',
        '/static/icons/icon-512x512.png',
        '/static/css/styles.css', // Agrega tus archivos CSS
        '/static/js/scripts.js', // Agrega tus archivos JS
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});