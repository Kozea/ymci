(function() {
  var $style, change_style, index, style, styles;

  style = Cookies.get('style') || 'lumen.css';

  $style = $('#style');

  styles = $('body').attr('data-styles').split(',');

  index = styles.indexOf(style);

  change_style = function() {
    return $style.attr('href', '/static/' + styles[index % styles.length]);
  };

  change_style();

  $('.theme-switcher').click(function() {
    index++;
    change_style();
    Cookies.set('style', styles[index % styles.length], {
      path: '/'
    });
    return false;
  });

}).call(this);
