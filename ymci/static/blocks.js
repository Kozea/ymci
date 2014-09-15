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
      var interval, _i, _len, _ref;
      _ref = this.intervals;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        interval = _ref[_i];
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
          return $percent.css('width', "" + percent + "%");
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
        var args, block, cc_block, ws;
        block = $(this).attr('data-block');
        args = $(this).attr('data-args') || '';
        blocks[block] = {};
        cc_block = block[0].toUpperCase() + block.slice(1);
        blocks[block].hook = (hooks["" + cc_block + "Hook"] != null) && new hooks["" + cc_block + "Hook"]();
        blocks[block].ws = ws = new WebSocket("ws://" + location.host + "/blocks/" + block + args);
        ws.onopen = function() {
          return console.log("" + block + " ws open");
        };
        ws.onclose = function() {
          return console.log("" + block + " ws closed", arguments);
        };
        ws.onerror = function() {
          return console.error("" + block + " ws error", arguments);
        };
        return ws.onmessage = (function(_this) {
          return function(e) {
            var $block, _ref, _ref1;
            $block = $(_this);
            if ((_ref = blocks[block].hook) != null) {
              if (typeof _ref.before === "function") {
                _ref.before($block);
              }
            }
            console.debug("Refreshing block " + block);
            $block.html(e.data);
            return (_ref1 = blocks[block].hook) != null ? typeof _ref1.after === "function" ? _ref1.after($block) : void 0 : void 0;
          };
        })(this);
      });
    };
  })(this));

}).call(this);

//# sourceMappingURL=blocks.js.map
