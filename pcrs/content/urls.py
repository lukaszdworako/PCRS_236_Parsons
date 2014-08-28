from django.conf import settings
from django.conf.urls import patterns, url
from content.api import InclassProblems, InclassProblemsView

from content.challenge_content_views import (TextCreateView, PageCreateView,
                                             ChallengeObjectsView,
                                             ItemDeleteView,
                                             ChallengePagesObjectsView,
                                             ChangeProblemVisibilityView,
                                             PageDeleteView)
from content.challenge_views import *
from content.quest_views import (QuestCreateView, QuestUpdateView, QuestListView,
                                 QuestSaveChallengesView, QuestSectionListView,
                                 QuestsView, ReactiveQuestsView,
                                 ReactiveQuestsDataView)
from content.tag_views import *
from content.video_views import *
from pcrs.generic_views import GenericCourseStaffDeleteView


challenge_page_view = ContentPageView
quests_page_view = QuestsView

if settings.REACT:
    challenge_page_view = ReactiveContentPageView

if settings.QUESTS_LIVE:
    quests_page_view = ReactiveQuestsView

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
    
    url(r'^videos/create$', VideoCreateView.as_view(),
        name='video_create'),
    url(r'^videos/(?P<pk>[0-9]+)$', VideoUpdateView.as_view(),
        name='video_update'),
    url(r'^videos/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Video),
        name='video_delete'),
    url(r'^videos/list$', VideoListView.as_view(),
        name='video_list'),
    url(r'^videos/(?P<pk>[0-9]+)/watched$', VideoRecordWatchView.as_view(),
        name='video_record_watch'),

    url(r'^challenges/create$', ChallengeCreateView.as_view(),
        name='challenge_create'),
    url(r'^challenges/(?P<pk>[0-9]+)$', ChallengeUpdateView.as_view(),
        name='challenge_update'),
    url(r'^challenges/list$', ChallengeListView.as_view(),
        name='challenge_list'),
    url(r'^challenges/(?P<challenge>[0-9]+)/(?P<page>[0-9]+)$',
        challenge_page_view.as_view(),
        name='challenge_page'),

    url(r'^challenges/(?P<challenge>[0-9]+)/(?P<page>[0-9]+)/get_page_data$',
        ReactiveContentPageData.as_view(),
        name='challenge_page_data'),


    url(r'^challenges/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Challenge),
        name='challenge_delete'),
    url(r'^challenges/(?P<pk>[0-9]+)/stats$',
        ChallengeStatsView.as_view(),
        name='challenge_stats'),
    url(r'^challenges/(?P<pk>[0-9]+)/stats/data$',
        ChallengeStatsGetData.as_view(),
        name='challenge_stats_data'),

    # prerequisites graph
    url(r'^challenges/prereq_graph$', ChallengeGraphView.as_view()),
    url(r'^challenges/prereq_graph/generate_horizontal$', ChallengeGraphGenViewHorizontal.as_view()),
    url(r'^challenges/prereq_graph/generate_vertical$', ChallengeGraphGenViewVertical.as_view()),
    url(r'^challenges/prereq_graph/for_user$',
        ChallengeCompletionForUserView.as_view(),
        name='challenge_prerequisite_data_for_user'),

    # content object manipulation within challenge
    url(r'^challenges/(?P<pk>[0-9]+)/objects$', ChallengeObjectsView.as_view()),
    url(r'^challenges/(?P<pk>[0-9]+)/objects/pages$',
        ChallengePagesObjectsView.as_view(), name='page_manage_objects'),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/page/create$',
        PageCreateView.as_view(), name='page_create'),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/page-(?P<pk>[0-9]+)/delete',
        PageDeleteView.as_view(model=ContentPage), name='page_delete'),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/page-(?P<page>[0-9]+)/text/create$',
        TextCreateView.as_view()),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/textblock-(?P<pk>[0-9]+)/delete',
        ItemDeleteView.as_view(model=TextBlock)),
    url(r'^challenges/(?P<challenge>[0-9]+)/objects/change_status',
        ChangeProblemVisibilityView.as_view(model=TextBlock)),

    url(r'^quests$', quests_page_view.as_view(), name='quests'),

    url(r'^quests/list$', QuestListView.as_view(),
        name='quest_list'),
    url(r'^quests/list/save_challenges$', QuestSaveChallengesView.as_view(),
        name='quest_list_save_challenges'),
    url(r'^quests/create$', QuestCreateView.as_view(),
        name='quest_create'),
    url(r'^quests/(?P<pk>[0-9]+)$', QuestUpdateView.as_view(),
        name='quest_update'),
    url(r'^quests/(?P<pk>[0-9]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Quest),
        name='quest_delete'),

    url(r'^quests/section/(?P<section>[\w-]+)$', QuestSectionListView.as_view(),
        name='section_quests_setup'),


    url(r'^inclass$', InclassProblemsView.as_view(),
        name='inclass_problems_page'),

    url(r'^inclass/list$', InclassProblems.as_view(),
        name='inclass_problems'),

    url(r'^get_quest_list$', ReactiveQuestsDataView.as_view(),
        name='live_quest_list'),


)