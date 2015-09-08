(function() {
  $(function() {
    return $('.pygal').on('click', function() {
      var $popup, base_url, height, width;
      $popup = $('<embed type="image/svg+xml"/>');
      width = $(window).width();
      height = $(window).height();
      base_url = $(this).attr('src').split('.')[0];
      $popup.attr('src', base_url + "_" + width + "_" + height + ".svg");
      return $popup.popup({
        autoopen: true,
        detach: true
      });
    });
  });

}).call(this);
