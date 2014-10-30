time = -> (new Date()).getTime() / 1000
hooks = {}
class hooks.BuildHook
  constructor: ->
    @intervals = []

  before: ($block) ->
    for interval in @intervals
      clearInterval interval
    @intervals = []

  after: ($block) ->
    that = @
    $block.find('.build-progress').each ->
      $percent = $(@)
      base = +$percent.attr('data-now')
      end = +$percent.attr('data-end')
      start = time()

      update_progress = ->
        percent = 100 * (base + (time() - start)) / end
        if percent > 120
          percent = 100
          $percent.addClass 'progress-bar-danger'
          $percent.removeClass 'progress-bar-warning'
        else if percent > 100
          percent = 100
          $percent.addClass 'progress-bar-warning'
          $percent.removeClass 'progress-bar-danger'
        else
          $percent.removeClass 'progress-bar-danger'
          $percent.removeClass 'progress-bar-warning'
        $percent.css 'width', "#{percent}%"

      if not isNaN(base)
        that.intervals.push setInterval update_progress, 10


$ =>
  @blocks = blocks = {}
  $('.block').each ->
    $elt = $(@)
    block = $elt.attr 'data-block'
    args = $elt.attr('data-args') or ''
    blocks[block] = {}
    cc_block = block[0].toUpperCase() + block.slice(1)
    blocks[block].hook = (
      hooks["#{cc_block}Hook"]? and new hooks["#{cc_block}Hook"]())

    delay = 100

    reconnect = (block, $elt) ->
      console.log("#{block} ws connecting")
      blocks[block].ws = ws = new WebSocket(
        "ws#{location.protocol.replace('http', '')}//#{
          location.host}/blocks/#{block}#{args}")
      ws.onopen = ->
        delay = 100
        console.log("#{block} ws open")

      ws.onclose = ->
        console.log("#{block} ws closed. Reconnecting in #{delay}ms", arguments)
        setTimeout (-> reconnect(block, $elt)), delay


      ws.onerror = ->
        delay *= 2
        console.error("#{block} ws error", arguments)

      ws.onmessage = (e) ->
        console.debug("Refreshing block #{block}", e)
        $block = $elt
        blocks[block].hook?.before?($block)
        $block.html(e.data)
        blocks[block].hook?.after?($block)

    reconnect(block, $elt)
