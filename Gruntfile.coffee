module.exports = (grunt) ->

  jsdeps = [
    'jquery/dist/jquery'
    'js-cookie/src/js.cookie'
    'jquery-popup-overlay/jquery.popupoverlay'
  ].map (js) -> "#{['bower_components', js].join '/'}.js"

  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')

    fileExists:
      js: jsdeps

    uglify:
      options:
        banner: '/*! <%= pkg.name %>
           <%= grunt.template.today("yyyy-mm-dd") %> */\n'

      ymci:
        files:
          'ymci/static/main.min.js': 'ymci/static/main.js'

      deps:
        files:
          'ymci/static/deps.min.js': jsdeps

    sass:
      options:
        includePaths: [
          'bower_components/bootstrap-sass/assets/stylesheets/'
        ]

      ymci:
        expand: true
        cwd: 'sass'
        src: '*.sass'
        dest: 'ymci/static/'
        ext: '.css'

    autoprefixer:
      hydra:
        expand: true
        cwd: 'ymci/static/'
        src: '*.css'
        dest: 'ymci/static/'

    coffee:
      ymci:
        expand: true
        cwd: 'coffee'
        src: '*.coffee'
        dest: 'ymci/static/'
        ext: '.js'

    coffeelint:
      ymci:
        'coffee/*.coffee'

    watch:
      options:
        livereload: true
      coffee:
        files: [
          'coffee/*.coffee'
          'Gruntfile.coffee'
        ]
        tasks: ['coffeelint', 'coffee']

      sass:
        files: [
          'sass/*.sass'
        ]
        tasks: ['sass']

  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-cssmin'
  grunt.loadNpmTasks 'grunt-file-exists'
  grunt.loadNpmTasks 'grunt-autoprefixer'
  grunt.loadNpmTasks 'grunt-coffeelint'
  grunt.loadNpmTasks 'grunt-sass'

  grunt.registerTask 'dev', [
    'coffeelint', 'coffee', 'sass', 'watch']
  grunt.registerTask 'css', ['sass']
  grunt.registerTask 'default', [
    'fileExists', 'coffeelint', 'coffee', 'sass', 'autoprefixer', 'uglify']
