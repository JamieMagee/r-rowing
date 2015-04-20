'use strict';

module.exports = function (grunt) {
    // Show elapsed time after tasks run
    require('time-grunt')(grunt);
    // Load all Grunt tasks
    require('jit-grunt')(grunt);

    grunt.initConfig({
        app: {
            source: 'src',
            dist: 'dist'
        },
        watch: {
            css: {
                files: '<%= app.source %>/theme.css',
                tasks: [
                    'copy:css',
                    'autoprefixer',
                    'cssmin'
                ]
            },
            images: {
                files: '<%= app.source %>/img/*.{gif,jpg,jpeg,png,svg,webp}',
                tasks: [
                    'copy:images',
                    'imagemin'
                ]
            }
        },
        clean: {
            dist: {
                files: [{
                    dot: true,
                    src: [
                        '<%= app.dist %>/*',
                        '!<%= app.dist %>/.git*'
                    ]
                }]
            }
        },
        autoprefixer: {
            options: {
                browsers: ['last 3 versions']
            },
            dist: {
                files: [{
                    expand: true,
                    cwd: '<%= app.dist %>',
                    src: 'theme.css',
                    dest: '<%= app.dist %>'
                }]
            }
        },
        cssmin: {
            dist: {
                options: {
                    keepSpecialComments: 0,
                    aggressiveMerging: true,
                    advanced: true
                },
                files: [{
                    expand: true,
                    cwd: '<%= app.dist %>',
                    src: 'theme.css',
                    dest: '<%= app.dist %>'
                }]
            }
        },
        imagemin: {
            options: {
                progressive: true,
                optimizationLevel: 7
            },
            dist: {
                files: [{
                    expand: true,
                    cwd: '<%= app.dist %>/img/',
                    src: '*.{jpg,jpeg,png,gif}',
                    dest: '<%= app.dist %>/img/'
                }]
            }
        },
        copy: {
            images: {
                files: [{
                    flatten: true,
                    expand: true,
                    src: '<%= app.source %>/img/*',
                    dest: '<%= app.dist %>/img'
                }]
            },
            css: {
                files : [{
                    src: '<%= app.source %>/theme.css',
                    dest: '<%= app.dist %>/theme.css'
                }]
            }
        }
    });

    // Define Tasks
    grunt.registerTask('build', [
        'clean',
        'copy',
        'imagemin',
        'autoprefixer',
        'cssmin',
        'watch'
    ]);

    grunt.registerTask('default', [
        'build'
    ]);
};