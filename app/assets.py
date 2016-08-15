from flask.ext.assets import Bundle

app_css = Bundle(
    'app.scss',
    'map.scss',
    filters='scss',
    output='styles/app.css'
)

app_js = Bundle(
    'app.js',
    'map.js',
    filters='jsmin',
    output='scripts/app.js'
)

vendor_css = Bundle(
    'vendor/semantic.min.css',
    'vendor/iThing.css',
    output='styles/vendor.css'
)

vendor_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/semantic.min.js',
    'vendor/tablesort.min.js',
    'vendor/jquery-ui.js',
    'vendor/jQDateRangeSlider-min.js',
    'vendor/oms.min.js',
    'vendor/markerclusterer.js',
    filters='jsmin',
    output='scripts/vendor.js'
)
