from django.conf.urls import url

from users.views import UserViewView

urlpatterns = [
    url(r'^view_as$', UserViewView.as_view(),
        name='view_as_user'),
]
