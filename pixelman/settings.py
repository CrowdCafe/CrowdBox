import djcelery
djcelery.setup_loader()

"""
Django settings for clientapp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from settings_secret import *


ADMINS = (
    ('Pavel', 'pavel@crowdcafe.io'),
    ('Stefano', 'stefano@crowdcafe.io'),
)

MANAGERS = ADMINS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."),
)

MARBLE_3D_ERROR_THREASHOLD = {
    'center':0.15,
    'perimetr':0.15,
    'area':0.15
}
MARBLE_3D_ENLARGE_POLYGON = 100
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['crowdcrop.crowdcafe.io','80.240.134.163','localhost']

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_ROOT, 'components')

BOWER_INSTALLED_APPS = (
    'bootstrap',
    'fontawesome',
    'jquery',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3' 
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',
    'djangobower',
    'crispy_forms',
    'social_auth',
    'website',
    'dropbox',
    'djcelery',
    'djrill',
    #'paypal.standard.ipn',
    #'djkombu',
    'kombu.transport.django',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_auth.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'pixelman.urls'

WSGI_APPLICATION = 'pixelman.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'logfile': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': "/var/log/django/pixelman.log",
                'maxBytes': 50000,
                'backupCount': 3,
                'formatter': 'standard'
        },
        'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
    },
    'loggers': {
        'django': {
            'handlers': ['console','logfile'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console','logfile'],
            'level': 'WARNING',
            'propagate': False,
        },
        'background_tasks': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'client_dropbox': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'client_crowdcafe': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'crowd_io': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'crowd_task': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console','logfile'],
            'level': 'DEBUG',
            'propagate': True
        }

    }
}
APP_URL = "http://rockpearl.crowdcafe.io/"
# PayPal account on which requestors send money
# ---------------------------------------------------------------
PAYPAL_RECEIVER_EMAIL = "pavel@crowdcafe.io"
PAYPAL_TEST = False
# ---------------------------------------------------------------

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.contrib.dropbox.DropboxBackend',
    #'social_auth.backends.twitter.TwitterBackend',
    #'social_auth.backends.facebook.FacebookBackend',
#    'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
#    'social_auth.backends.google.GoogleBackend',
#    'social_auth.backends.yahoo.YahooBackend',
#    'social_auth.backends.browserid.BrowserIDBackend',
#    'social_auth.backends.contrib.linkedin.LinkedinBackend',
#    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
#    'social_auth.backends.contrib.orkut.OrkutBackend',
#    'social_auth.backends.contrib.foursquare.FoursquareBackend',
    #'social_auth.backends.contrib.github.GithubBackend',
#    'social_auth.backends.contrib.vkontakte.VKontakteBackend',
#    'social_auth.backends.contrib.live.LiveBackend',
#    'social_auth.backends.contrib.skyrock.SkyrockBackend',
#    'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
#    'social_auth.backends.OpenIDBackend',
    #'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('dropbox')

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.social.load_extra_data',
)

LOGIN_ERROR_URL =APP_URL# '/'
LOGIN_URL=APP_URL#'/'
LOGIN_REDIRECT_URL =APP_URL# 'http://rockpearl.crowdcafe/'

MEDIA_ROOT = '/var/django/media/'
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static1-files/

STATIC_URL = '/static/'
#STATIC_URL = 'https://s3-eu-west-1.amazonaws.com/' + AWS_STORAGE_BUCKET_NAME + '/'
STATIC_ROOT = '/var/www/pixelman.io/static/'

# List of finder classes that know how to find static1 files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# -----------------------------------------------------------------------------
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_URL = 'django://'
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
#BROKER_URL = 'django://'
