style = Cookies.get('style') or 'lumen.css'

$style = $('#style')
styles = $('body').attr('data-styles').split(',')
index = styles.indexOf(style)
base = $style.attr('data-href')

change_style = ->
  $style.attr('href', base.replace('_style_', styles[index % styles.length]))

change_style()

$('.theme-switcher').click ->
  index++
  change_style()
  Cookies.set 'style', styles[index % styles.length], path: '/'
  false
