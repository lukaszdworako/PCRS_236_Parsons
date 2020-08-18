PRODUCTION = False
DEBUG = not PRODUCTION

ADMINS = (
	('Akira', 'akira.takaki@mail.utoronto.ca'),
    # ('Your Name', 'your_email@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pcrsadmin',
        'USER': 'pcrsadmin',
        'PASSWORD': 'pcrsadmin',
        'HOST': '127.0.0.1', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',          # Set to empty string for default.
    }
}


# Make this unique, and don't share it with anybody.
SECRET_KEY = '69420'

INSTALLED_PROBLEM_APPS = {
    'problems_python': 'Python',
    # 'problems_c': 'C',
    # 'problems_java': 'Java',
    # 'problems_rdb': '',
    # 'problems_sql': 'SQL',
    # 'problems_ra': 'Relational Algebra',
    # 'problems_r': 'R',
    'problems_multiple_choice': '',
    # 'problems_timed': '',
    # 'problems_rating': '',
    'problems_short_answer': '',
	'problems_fa_visuals': '',
}


AUTH_TYPE = 'none'       # 'shibboleth', 'pwauth', 'pass', or 'none'