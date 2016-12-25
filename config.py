import os
import urlparse
from raygun4py.middleware import flask as flask_raygun

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_NAME = 'IdleFreePhilly'
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'SjefBOa$1FgGco0SkfPO392qqH9%a492'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMIN_EMAIL = 'flask-base-admin@example.com'
    EMAIL_SUBJECT_PREFIX = '[{}]'.format(APP_NAME)
    EMAIL_SENDER = '{app_name} Admin <{email}>'.format(app_name=APP_NAME,
                                                       email=MAIL_USERNAME)
    # Default viewport is bounding box for Philadelphia, PA
    VIEWPORT = '39.861204,-75.310357|40.138932,-74.928582'

    OPEN_WEATHER_MAP_API_KEY = os.environ.get('OPEN_WEATHER_MAP_API_KEY') or \
        'SjefBOa$1FgGco0SkfPO392qqH9'
    IMGUR_CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID')
    IMGUR_CLIENT_SECRET = os.environ.get('IMGUR_CLIENT_SECRET')

    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

    REDIS_URL = os.getenv('REDISTOGO_URL') or 'http://localhost:6379'

    RAYGUN_APIKEY = os.environ.get('RAYGUN_APIKEY')

    GOOGLE_GEOCODE_KEY = os.environ.get('GOOGLE_GEOCODE_KEY')

    # Parse the REDIS_URL to set RQ config variables
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(REDIS_URL)

    RQ_DEFAULT_HOST = url.hostname
    RQ_DEFAULT_PORT = url.port
    RQ_DEFAULT_PASSWORD = url.password
    RQ_DEFAULT_DB = 0

    # Used for external url_for. This is a hack, see
    # https://julo.ch/blog/why-flask-can-suck/#urlfor-and-servername for why
    # this is necessary.
    DOMAIN = os.environ.get('DOMAIN')

    # Used for displaying dates in local format. Must be a string recognized
    # by pytz.
    TIMEZONE = os.environ.get('TIMEZONE') or 'US/Eastern'

    # Send all incident report emails to this address.
    SEND_ALL_REPORTS_TO = os.environ.get('SEND_ALL_REPORTS_TO')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    # TODO: add to flask-base
    SSL_DISABLE = (os.environ.get('SSL_DISABLE') or 'True') == 'True'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        if app.config['RAYGUN_APIKEY'] is not None:
            flask_raygun.Provider(app, app.config['RAYGUN_APIKEY']).attach()


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class ProductionWithDebug(ProductionConfig):
    DEBUG = True
    ASSETS_DEBUG = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'production_debug': ProductionWithDebug,
    'default': DevelopmentConfig
}
