$ ->
  $code = $('code.out')
  ws = new WebSocket("ws://#{location.host}/log/#{
    $code.attr('data-id')}/#{$code.attr('data-idx')}/pipe")
  ws.onopen = -> console.log('ws opened')
  ws.onclose = -> console.log('ws closed', arguments)
  ws.onerror = -> console.error('ws error', arguments)
  autoscroll = true

  $(window).on 'wheel', (e) ->
    autoscroll = false
    true

  $(window).on 'keydown', (e) ->
    autoscroll = not autoscroll

  ws.onmessage = (e) ->
    setTimeout ->
      $code.get(0).innerHTML += e.data
      if autoscroll
        $('html').scrollTop($('body').height() - window.innerHeight)
    , 100
