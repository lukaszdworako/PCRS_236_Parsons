from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import login
from users.views import SectionChangeView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/', login.login_view, name='login'),
    url(r'^section/', SectionChangeView.as_view(), name='section_change'),
    url(r'^logout$', login.logout_view, name = 'logout_view'),

    url(r'^problems/', include('problems.urls')),
    url(r'^content/', include('content.urls')),
)