(function() {
  $(function() {
    var $code, autoscroll, ws;
    $code = $('code.out');
    ws = new WebSocket("ws" + (location.protocol.replace('http', '')) + "//" + location.host + "/log/" + ($code.attr('data-id')) + "/" + ($code.attr('data-idx')) + "/pipe");
    ws.onopen = function() {
      return console.log('ws opened');
    };
    ws.onclose = function() {
      return console.log('ws closed', arguments);
    };
    ws.onerror = function() {
      return console.error('ws error', arguments);
    };
    autoscroll = true;
    $(window).on('wheel', function(e) {
      autoscroll = false;
      return true;
    });
    $(window).on('keydown', function(e) {
      return autoscroll = !autoscroll;
    });
    return ws.onmessage = function(e) {
      return setTimeout(function() {
        $code.get(0).innerHTML += e.data;
        if (autoscroll) {
          return $(window).scrollTop($('body').height() - window.innerHeight);
        }
      }, 100);
    };
  });

}).call(this);

//# sourceMappingURL=log.js.map
