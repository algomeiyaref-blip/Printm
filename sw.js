const CACHE='prinm0-v2'; const ASSETS=['./','./index.html','./style.css','./app.js','./manifest.json'];
self.addEventListener('install',event=>{ event.waitUntil( caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()) ); });
self.addEventListener('activate',event=>{ event.waitUntil( caches.keys().then(keys=>Promise.all( keys.filter(key=>key.startsWith('prinm0-') && key!==CACHE).map(key=>caches.delete(key)) )).then(()=>self.clients.claim()) ); });
self.addEventListener('fetch',event=>{ event.respondWith( fetch(event.request).then(response=>{ const copy=response.clone(); caches.open(CACHE).then(cache=>cache.put(event.request,copy)).catch(()=>{}); return response; }).catch(()=>caches.match(event.request)) ); })));
