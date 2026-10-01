// Make Slack show Apple emoji instead of Google emoji.
//
// The Slack web client loads emoji images from the CDN with URLs like
//   https://a.slack-edge.com/production-standard-emoji-assets/15.0/google-medium/1f44d.png
// The same files exist under apple-*, so we redirect the requests in the main
// process. This covers every session (workspaces, popups, huddles), including
// the persist:* partitions that Slack creates after startup.
"use strict";

const { app, session } = require("electron");

const filter = {
  urls: [
    "*://*.slack-edge.com/production-standard-emoji-assets/*",
    "*://*.slack-edge-gov.com/production-standard-emoji-assets/*",
  ],
};

const patched = new WeakSet();

function patch(s) {
  if (patched.has(s)) return;
  patched.add(s);
  s.webRequest.onBeforeRequest(filter, (details, callback) => {
    const url = details.url
      .replace(/\/google-([a-z0-9]+)\//, "/apple-$1/")
      .replace(/sheet_google_/, "sheet_apple_");
    callback(url === details.url ? {} : { redirectURL: url });
  });
}

app.on("session-created", patch);
app.whenReady().then(() => patch(session.defaultSession));
