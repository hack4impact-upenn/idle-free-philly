from flask.ext.assets import Bundle

app_css = Bundle(
    'app.scss',
    filters='scss',
    output='styles/app.css'
)

app_js = Bundle(
    'app.js',
    filters='jsmin',
    output='scripts/app.js'
)

vendor_css = Bundle(
    'vendor/semantic.min.css',
    output='styles/vendor.css'
)

vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    filters='jsmin',
    output='scripts/vendor.js'
)

iThing_css = Bundle(
    'iThing.css',
    output='styles/iThing.css'
)

jqueryui_js = Bundle(
    'jquery-ui.js',
    output='scripts/jquery-ui.js'
)

jQDateRangeSlidermin_js = Bundle(
    'jQDateRangeSlider-min.js',
    output='scripts/jQDateRangeSlider-min.js'
)
