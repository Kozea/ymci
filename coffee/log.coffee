$ ->
  $code = $('code.out')
  ws = new WebSocket("ws://#{location.host}/log/#{
    $code.attr('data-id')}/#{$code.attr('data-idx')}/pipe")
  ws.onopen = -> console.log('ws opened')
  ws.onclose = -> console.log('ws closed', arguments)
  ws.onerror = -> console.error('ws error', arguments)
  ws.onmessage = (e) ->
    setTimeout (->
      $code.get(0).innerHTML += e.data), 100
