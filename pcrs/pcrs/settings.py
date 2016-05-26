import os

# Select the types of problems visible in the UI.
# app_name : language name
INSTALLED_PROBLEM_APPS = {
    #'problems_python': 'Python',
    #'problems_c': 'C',
    'problems_java': 'Java',
    # 'problems_rdb': '',
    # 'problems_sql': 'SQL',
    # 'problems_ra': 'Relational Algebra',
    'problems_multiple_choice': '',
    # 'problems_timed': '',
    # 'problems_rating': '',
    # 'problems_short_answer': '',
}

USE_SAFEEXEC = False              # For C only, for now
SAFEEXEC_USERID = "1004"          # Use the id command to identify correct values for these.
SAFEEXEC_GROUPID = "1005"

# Session information
PROTOCOL_TYPES = (('http', 'http'), ('https', 'https'), ('ssh', 'ssh'))
SESSION_COOKIE_AGE = 86400       # One day, in seconds

PRODUCTION = False
DEBUG = not PRODUCTION
SQL_DEBUG = False                   # Suppresses logging of SQL queries
TEMPLATE_DEBUG = DEBUG

# True if links to bug reporting emails should be generated
REPORT_BUGS = False

# controls if live-updated quests page should be used
# live page receives updates from socket.io to update when items are completed
QUESTS_LIVE = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pcrsdev',
        'USER': 'pcrsdev',
        'PASSWORD': 'apJIRu4',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                               # Set to empty string for default.
    }
}


# RDB problems database information
RDB_DATABASE = 'crs_data'
RDB_DATABASE_test = 'crs_data_test'

# Site prefix
SITE_PREFIX = ''
if PRODUCTION:
    SITE_PREFIX = '/pcrs_108'
FORCE_SCRIPT_NAME = SITE_PREFIX

# Login details
LOGIN_URL = SITE_PREFIX + '/login'
if PRODUCTION:
    LOGIN_URL = SITE_PREFIX + "/login"
AUTH_USER_MODEL = 'users.PCRSUser'
AUTHENTICATION_BACKENDS = ('pcrs_authentication.ModelBackend',)
AUTH_TYPE = 'none'       # 'shibboleth', 'pwauth', 'pass', or 'none'
AUTOENROLL = False

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Toronto'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Enables sites and sets default to the site with ID 1. Ensure that the
# database has a correct "site 1".
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the location of the project
# Example: "/var/www/example.com/media/"
PROJECT_ROOT = str(os.getcwd())

# URL to the root of the system that stores PCRS documents. Make sure there is
# no trailing slash.
DOC_URL = 'https://bitbucket.org/utmandrew/pcrs-c-content/src/master/webdocs'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

#Indicates to django_compress that you want the files to be compressed
COMPRESS_ENABLED = "True"

# Additional locations of static files
STATICFILES_DIRS = (
    (PROJECT_ROOT + os.sep + 'resources'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
#finder for django_compress
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '36!^rq34a%q0stzTNy2:34%328[setv8pwWtLLglihs4r1JOZ&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "pcrs.context_processors.site_settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pcrs.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pcrs.wsgi.application'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)

PROBLEM_APPS = (
    'problems_python',
    'problems_c',
    'problems_sql',
    'problems_rdb',
    'problems_ra',
    'problems_multiple_choice',
    'problems_timed',
    'problems_rating',
    'problems_short_answer',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'crispy_forms',
    'helpers',
    'content',
    'problems',
    'editor',
    'compressor',
    'users',
) + PROBLEM_APPS

CRISPY_TEMPLATE_PACK = 'bootstrap3'

if DEBUG and not SQL_DEBUG:
    # These lines must be positioned *after* the definition of the not so secret SECRET_KEY
    import django.db.backends
    import django.db.backends.util
    django.db.backends.BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: django.db.backends.util.CursorWrapper(cursor, self)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        # Handler for logging student activity which is save to a file
        # filename contains the path to a file where you want to store the log
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'activity.log'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'activity.logging': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}
