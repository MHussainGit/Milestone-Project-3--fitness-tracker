{% load static %}
/*global self, caches, fetch*/
const CACHE = "fittrack-v1";
const STATIC_ASSETS = [
    "{% static 'css/styles.css' %}",
    "{% static 'assets/dumbbell.png' %}",
    "/offline/"
];

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE).then(function (cache) {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys.filter(function (k) {
                    return k !== CACHE;
                }).map(function (k) {
                    return caches.delete(k);
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener("fetch", function (event) {
    const request = event.request;
    const url = new URL(request.url);

    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            caches.match(request).then(function (cached) {
                return cached || fetch(request).then(function (res) {
                    const clone = res.clone();
                    caches.open(CACHE).then(function (cache) {
                        cache.put(request, clone);
                    });
                    return res;
                });
            })
        );
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(function () {
                return caches.match("/offline/");
            })
        );
    }
});
