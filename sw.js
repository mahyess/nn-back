const cacheName = "namastenepal-static-v20";
const dynamicCache = "namastenepal-pages-v20";

const assets = [
  "/",
  "/static/js/reactify-django.ui.js",
  "/static/css/reactify-django.ui.css",
  "https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic&subset=latin",
  "/static/media/logo_2.f92bf144.png",
  "/static/img/icons/favicon.ico",
  "/static/media/brand-icons.13db00b7.eot",
  "/static/media/brand-icons.a046592b.woff",
  "/static/media/brand-icons.a1a749e8.svg",
  "/static/media/brand-icons.c5ebe0b3.ttf",
  "/static/media/brand-icons.e8c322de.woff2",
  "/static/media/chalfal.294b5fcc.png",
  "/static/media/chautari.c1b65e5a.png",
  "/static/media/flags.9c74e172.png",
  "/static/media/icons.0ab54153.woff2",
  "/static/media/icons.8e3c7f55.eot",
  "/static/media/icons.962a1bf3.svg",
  "/static/media/icons.b87b9ba5.ttf",
  "/static/media/icons.faff9214.woff",
  "/static/media/kurakani.7bc9e0ea.png",

  "/static/media/livechat-animation.e31b7528.gif",

  "/static/media/login.d237a690.png",

  "/static/media/mero_sathi.9c63f7dd.png",

  "/static/media/message.03563536.png",
  "/static/media/namaste.e5054380.png",

  "/static/media/nn_loading2.bbff240a.gif",

  "/static/media/outline-icons.701ae6ab.eot",

  "/static/media/outline-icons.82f60bd0.svg",

  "/static/media/outline-icons.ad97afd3.ttf",

  "/static/media/outline-icons.cd6c777f.woff2",

  "/static/media/outline-icons.ef60a4f6.woff",
  "/static/media/samaj.5186144b.png",
  "/static/media/signup.92a968a4.png",
  "/static/media/tags.79f540f8.png"
];
// limit size
const limitCacheSize = (name, size) => {
  caches.open(name).then(cache => {
    cache.keys().then(keys => {
      if (keys.length > size) {
        cache.delete(keys[0]).then(limitCacheSize(name, size));
      }
    });
  });
};

// install a serviceworker
self.addEventListener("install", evt => {
  // console.log('service worker installed');
  evt.waitUntil(
    caches.open(cacheName).then(cache => {
      console.log("caching assets");

      cache.addAll(assets);
    })
  );
});

self.addEventListener("activate", evt => {
  //   console.log("service worker activated");
  evt.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys
          .filter(key => key !== cacheName && key !== dynamicCache)
          .map(key => caches.delete(key))
      );
    })
  );
});

self.addEventListener("fetch", evt => {
  evt.respondWith(
    caches.match(evt.request).then(cacheRes => {
      return (
        cacheRes ||
        fetch(evt.request).then(fetchRes => {
          return caches.open(dynamicCache).then(cache => {
            cache.put(evt.request.url, fetchRes.clone());
            limitCacheSize(dynamicCache, 15);
            return fetchRes;
          });
        })
      );
    })
    // .catch(() => {
    //   // if (evt.request.url.indexOf(".html") > -1) {
    //   return caches.match("/offline/");
    //   // }
    // })
  );
});
