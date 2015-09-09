
$ ->
  $code = $('code.out')
  ansi = new Ansi()

  code = $code.get(0)
  if code.innerHTML
    code.innerHTML = ansi.feed code.innerHTML
  return unless $code.attr('data-id')

  ws = new WebSocket("ws#{location.protocol.replace('http', '')}//#{
    location.host}/log/#{
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
      $code.get(0).innerHTML += ansi.feed e.data
      if autoscroll
        $(window).scrollTop($('body').height() - window.innerHeight)
    , 10
