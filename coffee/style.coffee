style = Cookies.get('style') or 'lumen.css'

$style = $('#style')
styles = $('body').attr('data-styles').split(',')
index = styles.indexOf(style)

change_style = ->
  $style.attr('href', '/static/' + styles[index % styles.length])

change_style()

$('.theme-switcher').click ->
  index++
  change_style()
  Cookies.set 'style', styles[index % styles.length], path: '/'
  false
