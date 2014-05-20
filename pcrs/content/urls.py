from django.conf.urls import patterns, url
from django.views.generic import TemplateView, FormView
from content.forms import ProblemSetForm
from users.views import GenericCourseStaffDeleteView

from .views import *


urlpatterns = patterns('',
    url(r'^challenge/create$', ChallengeCreateView.as_view(),
        name='challenge_create'),
    url(r'^challenge/(?P<pk>[0-9]+)$', ChallengeUpdateView.as_view(),
        name='challenge_update'),
    url(r'^challenge/list$', ChallengeListView.as_view(),
        name='challenge_list'),
    url(r'^challenge/(?P<challenge>[0-9]+)/(?P<page>[0-9]+)$',
        ContentPageView.as_view(),
        name='challenge_page'),
    url(r'^challenge/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Challenge,
                                             template_name='pcrs/check_delete.html'),
        name='challenge_delete'),

    url(r'^challenge/(?P<pk>[0-9]+)/go$', ChallengeStartView.as_view(),
        name=''),

    url(r'^quests$', ContainerListView.as_view(),
        name='quests'),

    url(r'^problem_set/create$',
        ProblemSetCreateView.as_view(template_name='pcrs/crispy_form.html')),
    url(r'^problem_set/(?P<problemset>[0-9]+)$',
        ProblemSetDetailView.as_view(template_name='content/problem_set.html'))
)