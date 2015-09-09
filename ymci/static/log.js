(function() {
  $(function() {
    var $code, ansi, autoscroll, code, ws;
    $code = $('code.out');
    ansi = new Ansi();
    code = $code.get(0);
    if (code.innerHTML) {
      code.innerHTML = ansi.feed(code.innerHTML);
    }
    if (!$code.attr('data-id')) {
      return;
    }
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
        $code.get(0).innerHTML += ansi.feed(e.data);
        if (autoscroll) {
          return $(window).scrollTop($('body').height() - window.innerHeight);
        }
      }, 10);
    };
  });

}).call(this);
