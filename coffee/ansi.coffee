class @Ansi
  COLORS: [
    '#2e3436',
    '#cc0000',
    '#4e9a06',
    '#c4a000',
    '#3465a4',
    '#75507b',
    '#06989a',
    '#d3d7cf',
    '#555753',
    '#ef2929',
    '#8ae234',
    '#fce94f',
    '#729fcf',
    '#ad7fa8',
    '#34e2e2',
    '#eeeeec'
  ]

  constructor: ->
    @state = 'normal'
    @opts = []
    @param = 0
    @color = @default_color()

  default_color: ->
    bg: null
    fg: null
    bold: false
    underline: false

  span: ->
    style = ''
    if @color.bg isnt null
      bg = Ansi::COLORS[@color.bg]
      style += 'background-color: ' + bg + ';'
    if @color.fg isnt null
      fg = @color.fg
      if @color.bold and fg < 8
        fg += 8
      fg = Ansi::COLORS[fg]
      style += 'color: ' + fg + ';'
    if @color.bold
      style += 'font-weight: bold;'
    if @color.underline
      style += 'text-decoration: underline;'
    if style
      style = " style=\"#{ style }\""

    "<span#{style}>"


  feed: (data) ->
    if data.indexOf('\x1b') < 0
      return @span() + data + '</span>'

    out = @span()
    i = -1

    while i < data.length - 1
      c = data.charAt ++i
      switch @state
        when 'normal'
          if c is '\x1b'
            @state = 'escaped'
            break
          out += c

        when 'escaped'
          if c is '['
            @opts = []
            @param = 0
            @state = 'csi'
            break

          if c is ']'
            @opts = []
            @param = 0
            @state = 'osc'
            break
          @state = 'normal'

        when 'csi'
          if ['?', '>', '!', '$', '"', ' ', "'"].indexOf(c) >= 0
            break
          if '0' <= c <= '9'
            @param = @param * 10 + c.charCodeAt(0) - 48
            break
          @opts.push @param
          @param = 0

          break if c is ';'

          @state = 'normal'

          break if c isnt 'm'

          for opt in @opts
            if opt is 0
              @color = @default_color()
            else if opt is 1
              @color.bold = true
            else if opt is 4
              @color.underline = true
            else if opt is 22
              @color.bold = false
            else if opt is 24
              @color.underline = false
            else if 30 <= opt <= 37
              @color.fg = opt - 30
            else if opt is 39
              @color.fg = null
            else if 40 <= opt <= 47
              @color.bg = opt - 40
            else if opt is 49
              @color.bg = null
            else if opt is 100
              @color.fg = null
              @color.bg = null

          out += '</span>'
          out += @span()
          @opts = []

    return out + '</span>'
