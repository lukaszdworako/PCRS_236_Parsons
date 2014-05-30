from django.conf.urls import patterns, url

from content.models import ProblemSet
from content.problemset_views import (ProblemSetCreateView, ProblemSetUpdateView,
                                      ProblemSetDetailView, ProblemSetListView)
from content.views import *
from pcrs.generic_views import GenericCourseStaffDeleteView

from content import views #video



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
        GenericCourseStaffDeleteView.as_view(model=Challenge),
        name='challenge_delete'),

    url(r'^challenge/(?P<pk>[0-9]+)/go$', ChallengeStartView.as_view(),
        name=''),

    url(r'^quests$', ContainerListView.as_view(),
        name='quests'),

    # PROBLEM SETS
    url(r'^problem_set/list$',
        ProblemSetListView.as_view(),
        name='problem_set_list'),
    url(r'^problem_set/create$',
        ProblemSetCreateView.as_view(template_name='pcrs/crispy_form.html'),
        name='problem_set_create'),
    url(r'^problem_set/(?P<pk>[0-9]+)$', ProblemSetUpdateView.as_view(),
        name='problem_set_update'),
    url(r'^problem_set/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=ProblemSet)),
    url(r'^problem_set/(?P<problemset>[0-9]+)/list$',
        ProblemSetDetailView.as_view(template_name='content/problem_set.html')),

    # video
    url(r'^youtube', views.youtube, name = 'youtube'),
)