(function() {
  var hooks, time;

  time = function() {
    return (new Date()).getTime() / 1000;
  };

  hooks = {};

  hooks.BuildHook = (function() {
    function BuildHook() {
      this.intervals = [];
    }

    BuildHook.prototype.before = function($block) {
      var i, interval, len, ref;
      ref = this.intervals;
      for (i = 0, len = ref.length; i < len; i++) {
        interval = ref[i];
        clearInterval(interval);
      }
      return this.intervals = [];
    };

    BuildHook.prototype.after = function($block) {
      var that;
      that = this;
      return $block.find('.build-progress').each(function() {
        var $percent, base, end, start, update_progress;
        $percent = $(this);
        base = +$percent.attr('data-now');
        end = +$percent.attr('data-end');
        start = time();
        update_progress = function() {
          var percent;
          percent = 100 * (base + (time() - start)) / end;
          if (percent > 120) {
            percent = 100;
            $percent.addClass('progress-bar-danger');
            $percent.removeClass('progress-bar-warning');
          } else if (percent > 100) {
            percent = 100;
            $percent.addClass('progress-bar-warning');
            $percent.removeClass('progress-bar-danger');
          } else {
            $percent.removeClass('progress-bar-danger');
            $percent.removeClass('progress-bar-warning');
          }
          return $percent.css('width', percent + "%");
        };
        if (!isNaN(base)) {
          return that.intervals.push(setInterval(update_progress, 10));
        }
      });
    };

    return BuildHook;

  })();

  $((function(_this) {
    return function() {
      var blocks;
      _this.blocks = blocks = {};
      return $('.block').each(function() {
        var $elt, args, block, cc_block, delay, reconnect;
        $elt = $(this);
        block = $elt.attr('data-block');
        args = $elt.attr('data-args') || '';
        blocks[block] = {};
        cc_block = block[0].toUpperCase() + block.slice(1);
        blocks[block].hook = (hooks[cc_block + "Hook"] != null) && new hooks[cc_block + "Hook"]();
        delay = 100;
        reconnect = function(block, $elt) {
          var ws;
          console.log(block + " ws connecting");
          blocks[block].ws = ws = new WebSocket("ws" + (location.protocol.replace('http', '')) + "//" + location.host + "/blocks/" + block + args);
          ws.onopen = function() {
            delay = 100;
            return console.log(block + " ws open");
          };
          ws.onclose = function() {
            console.log(block + " ws closed. Reconnecting in " + delay + "ms", arguments);
            return setTimeout((function() {
              return reconnect(block, $elt);
            }), delay);
          };
          ws.onerror = function() {
            delay *= 2;
            return console.error(block + " ws error", arguments);
          };
          return ws.onmessage = function(e) {
            var $block, ref, ref1;
            console.debug("Refreshing block " + block, e);
            $block = $elt;
            if ((ref = blocks[block].hook) != null) {
              if (typeof ref.before === "function") {
                ref.before($block);
              }
            }
            $block.html(e.data);
            return (ref1 = blocks[block].hook) != null ? typeof ref1.after === "function" ? ref1.after($block) : void 0 : void 0;
          };
        };
        return reconnect(block, $elt);
      });
    };
  })(this));

}).call(this);
