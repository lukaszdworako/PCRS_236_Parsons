from django.conf.urls import patterns, include, url
from pcrs.settings import INSTALLED_PROBLEM_APPS

pattern_options = {'problems_code': url(r'^code/', include('problems_code.urls')),
    'problems_multiple_choice': url(r'^multiple_choice/', include('problems_multiple_choice.urls')),
    'problems_rdb': url(r'^rdb/', include('problems_rdb.urls')),
    'problems_sql': url(r'^sql/', include('problems_sql.urls')),
    'problems_ra': url(r'^ra/', include('problems_ra.urls')),
}

pattern_list = [''] + [pattern_options[mod] for mod in INSTALLED_PROBLEM_APPS]

urlpatterns = patterns(*pattern_list)

