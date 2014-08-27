(function() {
  document.addEventListener('DOMContentLoaded', function() {
    var code, ws;
    code = document.querySelectorAll('code.out')[0];
    ws = new WebSocket("ws://" + location.host + "/log/" + (code.getAttribute('data-id')) + "/" + (code.getAttribute('data-idx')) + "/pipe");
    ws.onopen = function() {
      return console.log('ws opened');
    };
    ws.onclose = function() {
      return console.log('ws closed', arguments);
    };
    ws.onerror = function() {
      return console.error('ws error', arguments);
    };
    return ws.onmessage = function(e) {
      return setTimeout((function() {
        return code.innerHTML += e.data;
      }), 10);
    };
  });

}).call(this);

//# sourceMappingURL=log.js.map
