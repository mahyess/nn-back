importScripts("https://www.gstatic.com/firebasejs/6.0.4/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/6.0.4/firebase-messaging.js");

firebase.initializeApp({
  messagingSenderId: "689375755300"
});
const messaging = firebase.messaging();
