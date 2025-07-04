const CACHE_NAME = 'club-blanca-v1';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/logo.png',
  '/static/favicon.ico',
  '/manifest.json',
  // Puedes agregar aquí otras rutas como:
  // '/static/fondo.jpg',
  // '/quienes-somos',
  // '/mision',
  // '/vision',
];

// Instalación del SW
self.addEventListener('install', event => {
  console.log('✅ Service Worker instalado');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .catch(err => console.error("❌ Error al cachear archivos: ", err))
  );
  self.skipWaiting();
});

// Activación del SW
self.addEventListener('activate', event => {
  console.log('✅ Service Worker activado');
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log(`🗑️ Borrando caché antigua: ${key}`);
            return caches.delete(key);
          }
        })
      )
    )
  );
  return self.clients.claim();
});

// Intercepción de peticiones
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          // console.log('📦 Usando desde caché:', event.request.url);
          return response;
        }
        // console.log('🌐 Requiriendo desde red:', event.request.url);
        return fetch(event.request);
      })
      .catch(() => new Response('⚠️ Sin conexión y recurso no en caché', {
        headers: { 'Content-Type': 'text/plain' }
      }))
  );
});