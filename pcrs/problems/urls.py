from django.conf.urls import patterns, include, url
from pcrs.settings import INSTALLED_PROBLEM_APPS

pattern_options = {'problems_code': (r'^code/', 'problems_code.urls'),
    'problems_multiple_choice': (r'^multiple_choice/', 'problems_multiple_choice.urls'),
    'problems_rdb': (r'^rdb/', 'problems_rdb.urls'),
    'problems_sql': (r'^sql/', 'problems_sql.urls'),
    'problems_ra': (r'^ra/', 'problems_ra.urls'),
    'problems_timed': (r'^timed/', 'problems_timed.urls'),
}

pattern_list = [''] + [url(pattern_options[mod][0], include(pattern_options[mod][1])) for mod in INSTALLED_PROBLEM_APPS]

urlpatterns = patterns(*pattern_list)

