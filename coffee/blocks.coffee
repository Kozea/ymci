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

      that.intervals.push setInterval update_progress, 100


$ =>
  @blocks = blocks = {}
  $('.block').each ->
    block = $(@).attr 'data-block'
    args = $(@).attr('data-args') or ''
    blocks[block] = {}
    cc_block = block[0].toUpperCase() + block.slice(1)
    blocks[block].hook = (
      hooks["#{cc_block}Hook"]? and new hooks["#{cc_block}Hook"]())

    blocks[block].ws = ws = new WebSocket(
      "ws://#{location.host}/blocks/#{block}#{args}")
    ws.onopen = -> console.log("#{block} ws open")
    ws.onclose = -> console.log("#{block} ws closed", arguments)
    ws.onerror = -> console.error("#{block} ws error", arguments)

    ws.onmessage = (e) =>
      $block = $(@)
      blocks[block].hook?.before?($block)
      console.debug("Refreshing block #{block}")
      $block.html(e.data)
      blocks[block].hook?.after?($block)
