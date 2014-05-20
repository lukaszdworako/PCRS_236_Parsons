from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^code/', include('problems_code.urls')),
    url(r'^multiple_choice/', include('problems_multiple_choice.urls')),
    url(r'^rdb/', include('problems_rdb.urls')),
    url(r'^sql/', include('problems_sql.urls')),
    url(r'^ra/', include('problems_ra.urls')),
)