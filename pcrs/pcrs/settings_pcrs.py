# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Don't touch this file, create/edit settings_local.py with what you need to change.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Select the types of problems visible in the UI.
# app_name : language name
INSTALLED_PROBLEM_APPS = {
    # 'problems_python': 'Python',
    # 'problems_c': 'C',
    # 'problems_java': 'Java',
    # 'problems_rdb': '',
    # 'problems_sql': 'SQL',
    # 'problems_ra': 'Relational Algebra',
    # 'problems_multiple_choice': '',
    # 'problems_timed': '',
    # 'problems_rating': '',
    # 'problems_short_answer': '',
}

USE_SAFEEXEC = False              # For C only, for now
SAFEEXEC_USERID = "1004"          # Use the id command to identify correct values for these.
SAFEEXEC_GROUPID = "1005"

PRODUCTION = False
DEBUG = not PRODUCTION
SQL_DEBUG = False                   # Suppresses logging of SQL queries
TEMPLATE_DEBUG = DEBUG

# controls if live-updated quests page should be used
# live page receives updates from socket.io to update when items are completed
QUESTS_LIVE = False

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

# URL to the root of the system that stores PCRS documents. Make sure there is
# no trailing slash.
DOC_URL = 'https://bitbucket.org/utmandrew/pcrs-c-content/src/master/webdocs'

PROBLEM_APPS = (
    'problems_python',
    'problems_c',
    'problems_java',
    'problems_sql',
    'problems_rdb',
    'problems_ra',
    'problems_multiple_choice',
    'problems_timed',
    'problems_rating',
    'problems_short_answer',
)
