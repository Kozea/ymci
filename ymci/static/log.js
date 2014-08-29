(function() {
  $(function() {
    var $code, ws;
    $code = $('code.out');
    ws = new WebSocket("ws://" + location.host + "/log/" + ($code.attr('data-id')) + "/" + ($code.attr('data-idx')) + "/pipe");
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
        return $code.get(0).innerHTML += e.data;
      }), 100);
    };
  });

}).call(this);

//# sourceMappingURL=log.js.map
