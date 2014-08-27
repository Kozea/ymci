document.addEventListener 'DOMContentLoaded', ->
  code = document.querySelectorAll('code.out')[0]
  ws = new WebSocket("ws://#{location.host}/log/#{
    code.getAttribute('data-id')}/#{code.getAttribute('data-idx')}/pipe")
  ws.onopen = -> console.log('ws opened')
  ws.onclose = -> console.log('ws closed', arguments)
  ws.onerror = -> console.error('ws error', arguments)
  ws.onmessage = (e) ->
    setTimeout (->
      code.innerHTML += e.data), 100
