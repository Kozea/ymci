(function() {
  $(function() {
    return $('select[name=build-select]').on('change', function() {
      var url;
      url = $(this).val();
      return location.href = url;
    });
  });

}).call(this);

//# sourceMappingURL=browse.js.map
