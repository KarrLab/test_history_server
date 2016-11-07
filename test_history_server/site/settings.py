"""
Django (1.10.2) settings

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2016-11-01
:Copyright: 2016, Karr Lab
:License: MIT
"""

import os

BASE_DOMAIN = 'tests.karrlab.org'
BASE_URL = 'http://' + BASE_DOMAIN

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY_FILENAME = os.path.join(BASE_DIR, 'site', 'SECRET_KEY')
if os.path.isfile(SECRET_KEY_FILENAME):
    with open(SECRET_KEY_FILENAME, 'r') as file:
        SECRET_KEY = file.read().rstrip()
else:
    import random, string
    SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [BASE_DOMAIN]


# Application definition

INSTALLED_APPS = [
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.messages',
    #'django.contrib.staticfiles',
    'test_history_server.cli',
    'test_history_server.core',
    'test_history_server.html',
    'test_history_server.rest',
]

MIDDLEWARE = [
    #'django.middleware.security.SecurityMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'test_history_server.site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'html', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'test_history_server.site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASE_PASSWORD_FILENAME = os.path.join(BASE_DIR, 'site', 'DATABASE_DEFAULT_PASSWORD')
if os.path.isfile(DATABASE_PASSWORD_FILENAME):
    with open(DATABASE_PASSWORD_FILENAME, 'r') as file:
        DB_PASSWORD = file.read().rstrip()
else:
    DB_PASSWORD = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test_history_server',        # Or path to database file if using sqlite3.
        'USER': 'karrlab_tests',              # Not used with sqlite3.
        'PASSWORD': DB_PASSWORD,               # Not used with sqlite3.
        'HOST': 'mysql.karrlab.org',          # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                           # Set to empty string for default. Not used with sqlite3.
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

''' Logging '''

LOG_DIR = os.path.join(BASE_DIR, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'error.log')

if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)
if not os.path.isfile(LOG_FILE):
    with open(LOG_FILE, 'w'):
        os.utime(LOG_FILE, None)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'formatter': 'verbose',
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

''' App settings '''
XML_REPORTS_DIR = os.path.join(BASE_DIR, 'core', 'xml_reports')
#:obj:`str`: path to directory to save XML reports

REST_API_TOKEN_FILENAME = os.path.join(BASE_DIR, 'rest', 'REST_API_TOKEN')
#:obj:`str`: path to file with REST API token

if os.path.isfile(REST_API_TOKEN_FILENAME):
    with open(REST_API_TOKEN_FILENAME, 'r') as file:
        REST_API_TOKEN = file.read().rstrip()
        #:obj:`str`: REST API token; used to authenticate with server for submitting test reports
else:
    REST_API_TOKEN = None
