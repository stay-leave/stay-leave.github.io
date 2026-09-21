(function () {
  function sendBusuanzi() {
    var origin = location.origin;
    var targetUrl = location.href;
    if (origin.indexOf('localhost') !== -1 || origin.indexOf('127.0.0.1') !== -1) {
      targetUrl = 'https://stay-leave.github.io' + location.pathname + location.search;
    }

    var u = new URL('https://cdn.busuanzi.cc/');
    fetch(u.protocol + '//' + u.host + '/api.php', {
      method: 'POST',
      body: JSON.stringify({ url: targetUrl, referrer: document.referrer })
    })
      .then(function (r) { return r.json(); })
      .then(function (r) {
        for (var k in r) {
          document.querySelectorAll('#' + k).forEach(function (e) {
            e.innerText = r[k];
          });
          var legacyKey = k.replace(/^busuanzi_/, 'busuanzi_value_');
          document.querySelectorAll('#' + legacyKey).forEach(function (e) {
            e.innerText = r[k];
          });
          var containerKey = k.replace(/^busuanzi_/, 'busuanzi_container_');
          document.querySelectorAll('#' + containerKey).forEach(function (e) {
            e.style.display = 'inline';
          });
        }
      })
      .catch(function (e) {
        console.error('Busuanzi fetch error:', e);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendBusuanzi, { once: true });
  } else {
    sendBusuanzi();
  }

  document.addEventListener('pjax:complete', sendBusuanzi);
})();
