from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import login
from users.views import UserSettingsView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', login.login_view, name='login'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/', login.login_view, name='login'),
    url(r'^logout$', login.logout_view, name = 'logout_view'),
    url(r'^settings$', UserSettingsView.as_view(), name = 'user_settings_view'),

    url(r'^sections/', (include('users.section_urls'))),
    url(r'^users/', (include('users.user_urls'))),
    url(r'^problems/', include('problems.urls')),
    url(r'^content/', include('content.urls')),
)
