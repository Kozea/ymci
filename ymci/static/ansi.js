(function() {
  this.Ansi = (function() {
    Ansi.prototype.COLORS = ['#2e3436', '#cc0000', '#4e9a06', '#c4a000', '#3465a4', '#75507b', '#06989a', '#d3d7cf', '#555753', '#ef2929', '#8ae234', '#fce94f', '#729fcf', '#ad7fa8', '#34e2e2', '#eeeeec'];

    function Ansi() {
      this.state = 'normal';
      this.opts = [];
      this.param = 0;
      this.color = this.default_color();
    }

    Ansi.prototype.default_color = function() {
      return {
        bg: null,
        fg: null,
        bold: false,
        underline: false
      };
    };

    Ansi.prototype.span = function() {
      var bg, fg, style;
      style = '';
      if (this.color.bg !== null) {
        bg = Ansi.prototype.COLORS[this.color.bg];
        style += 'background-color: ' + bg + ';';
      }
      if (this.color.fg !== null) {
        fg = this.color.fg;
        if (this.color.bold && fg < 8) {
          fg += 8;
        }
        fg = Ansi.prototype.COLORS[fg];
        style += 'color: ' + fg + ';';
      }
      if (this.color.bold) {
        style += 'font-weight: bold;';
      }
      if (this.color.underline) {
        style += 'text-decoration: underline;';
      }
      if (style) {
        style = " style=\"" + style + "\"";
      }
      return "<span" + style + ">";
    };

    Ansi.prototype.feed = function(data) {
      var c, i, j, len, opt, out, ref;
      if (data.indexOf('\x1b') < 0) {
        return this.span() + data + '</span>';
      }
      out = this.span();
      i = -1;
      while (i < data.length - 1) {
        c = data.charAt(++i);
        switch (this.state) {
          case 'normal':
            if (c === '\x1b') {
              this.state = 'escaped';
              break;
            }
            out += c;
            break;
          case 'escaped':
            if (c === '[') {
              this.opts = [];
              this.param = 0;
              this.state = 'csi';
              break;
            }
            if (c === ']') {
              this.opts = [];
              this.param = 0;
              this.state = 'osc';
              break;
            }
            this.state = 'normal';
            break;
          case 'csi':
            if (['?', '>', '!', '$', '"', ' ', "'"].indexOf(c) >= 0) {
              break;
            }
            if (('0' <= c && c <= '9')) {
              this.param = this.param * 10 + c.charCodeAt(0) - 48;
              break;
            }
            this.opts.push(this.param);
            this.param = 0;
            if (c === ';') {
              break;
            }
            this.state = 'normal';
            if (c !== 'm') {
              break;
            }
            ref = this.opts;
            for (j = 0, len = ref.length; j < len; j++) {
              opt = ref[j];
              if (opt === 0) {
                this.color = this.default_color();
              } else if (opt === 1) {
                this.color.bold = true;
              } else if (opt === 4) {
                this.color.underline = true;
              } else if (opt === 22) {
                this.color.bold = false;
              } else if (opt === 24) {
                this.color.underline = false;
              } else if ((30 <= opt && opt <= 37)) {
                this.color.fg = opt - 30;
              } else if (opt === 39) {
                this.color.fg = null;
              } else if ((40 <= opt && opt <= 47)) {
                this.color.bg = opt - 40;
              } else if (opt === 49) {
                this.color.bg = null;
              } else if (opt === 100) {
                this.color.fg = null;
                this.color.bg = null;
              }
            }
            out += '</span>';
            out += this.span();
            this.opts = [];
        }
      }
      return out + '</span>';
    };

    return Ansi;

  })();

}).call(this);
