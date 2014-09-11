$ ->
  $('select[name=build-select]').on 'change', ->
    url = $(@).val()
    location.href = url
