const CACHE_NAME = 'agrogest-cache-v6';

// Only cache files that definitely exist
const CORE_FILES = [
  '/',
  '/static/manifest.json',
  '/static/js/dashboard.js',
  '/static/css/styles.css',
  '/static/js/main.js'
];

// Install event - cache core files
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching core files');
        return Promise.all(
          CORE_FILES.map(url =>
            fetch(url, { cache: 'no-store' })
              .then(response => {
                if (!response.ok) {
                  console.warn(`[Service Worker] Failed to cache ${url}: ${response.status}`);
                  return null;
                }
                return cache.put(url, response);
              })
              .catch(error => {
                console.warn(`[Service Worker] Error caching ${url}:`, error);
                return null;
              })
          )
        );
      })
      .catch(error => {
        console.error('[Service Worker] Cache failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, falling back to network
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || !event.request.url.startsWith('http')) {
    return;
  }

  const requestUrl = new URL(event.request.url);

  // Skip cross-origin requests
  if (!requestUrl.origin.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }

        return fetch(event.request)
          .then(networkResponse => {
            // Only cache successful responses (status 200)
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, networkResponse.clone()));
            }
            return networkResponse;
          })
          .catch(() => {
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/');
            }
            return new Response('', { status: 503 });
          });
      })
  );
});