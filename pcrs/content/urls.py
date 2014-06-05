from django.conf.urls import patterns, url

from content.challenge_content_views import TextCreateView, PageCreateView, \
    ChallengeObjectsView, ItemDeleteView, ChallengePagesObjectsView
from content.views import *
from content.tag_views import *
from content.video_views import *
from pcrs.generic_views import GenericCourseStaffDeleteView



urlpatterns = patterns('',
    url(r'^tags/list$', TagListView.as_view(),
        name='tag_list'),
    url(r'^tags/create$', TagCreateView.as_view(),
        name='tag_create'),
    url(r'^tags/(?P<pk>[0-9]+)$', TagUpdateView.as_view(),
        name='tag_update'),
    url(r'^tags/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Tag),
        name='tag_delete'),

    url(r'^quests$', ContainerListView.as_view(),
        name='quests'),
    
    url(r'^videos/create$', VideoCreateView.as_view(),
        name='video_create'),
    url(r'^videos/(?P<pk>[0-9]+)$', VideoUpdateView.as_view(),
        name='video_update'),
    url(r'^videos/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Video),
        name='video_delete'),
    url(r'^videos/list$', VideoListView.as_view(),
        name='video_list'),


    url(r'^challenges/create$', ChallengeCreateView.as_view(),
        name='challenge_create'),
    url(r'^challenges/(?P<pk>[0-9]+)$', ChallengeUpdateView.as_view(),
        name='challenge_update'),
    url(r'^challenges/list$', ChallengeListView.as_view(),
        name='challenge_list'),
    url(r'^challenges/(?P<challenge>[0-9]+)/(?P<page>[0-9]+)$',
        ContentPageView.as_view(),
        name='challenge_page'),
    url(r'^challenges/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Challenge),
        name='challenge_delete'),

    url(r'^challenges/(?P<pk>[0-9]+)/go$', ChallengeStartView.as_view(),
        name=''),

    # content object manipulation within challenge
    url(r'^challenges/(?P<pk>[0-9]+)/objects$', ChallengeObjectsView.as_view()),
    url(r'^challenges/(?P<pk>[0-9]+)/objects/pages$',
        ChallengePagesObjectsView.as_view()),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/page/create$',
        PageCreateView.as_view()),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/page-(?P<pk>[0-9]+)/delete',
        ItemDeleteView.as_view(model=ContentPage)),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/page-(?P<page>[0-9]+)/text/create$',
        TextCreateView.as_view()),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/textblock-(?P<pk>[0-9]+)/delete',
        ItemDeleteView.as_view(model=TextBlock))
)