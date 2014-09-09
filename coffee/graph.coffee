$ ->
  $('.pygal').on 'click', ->
    $popup = $('<embed type="image/svg+xml"/>')
    width = $(window).width()
    height = $(window).height()
    base_url = $(this).attr('src').split('.')[0]
    $popup.attr 'src', "#{base_url}_#{width}_#{height}.svg"
    $popup.popup(
      autoopen: true
      detach: true
    )
