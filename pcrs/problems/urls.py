from django.conf.urls import include, url
from pcrs.settings import INSTALLED_PROBLEM_APPS


pattern_options = {'problems_python': (r'^python/', 'problems_python.urls'),
                   'problems_c': (r'^c/', 'problems_c.urls'),
                   'problems_java': (r'^java/', 'problems_java.urls'),
                   'problems_multiple_choice': (r'^multiple_choice/', 'problems_multiple_choice.urls'),
                   'problems_rdb': (r'^rdb/', 'problems_rdb.urls'),
                   'problems_sql': (r'^sql/', 'problems_sql.urls'),
                   'problems_ra': (r'^ra/', 'problems_ra.urls'),
                   'problems_timed': (r'^timed/', 'problems_timed.urls'),
                   'problems_rating': (r'^rating/', 'problems_rating.urls'),
                   'problems_short_answer': (r'^short_answer/', 'problems_short_answer.urls'),
}

# pattern_list = [''] + [url(pattern_options[pt][0], include(pattern_options[pt][1])) for pt in INSTALLED_PROBLEM_APPS.keys()]
pattern_list = [url(pattern_options[pt][0], include(pattern_options[pt][1])) for pt in INSTALLED_PROBLEM_APPS.keys()]

urlpatterns = [*pattern_list]
