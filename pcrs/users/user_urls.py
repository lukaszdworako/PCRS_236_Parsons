from django.conf.urls import patterns, url

from users.views import UserViewView

urlpatterns = patterns('',
    url(r'^view_as$', UserViewView.as_view(),
        name='view_as_user'),
)