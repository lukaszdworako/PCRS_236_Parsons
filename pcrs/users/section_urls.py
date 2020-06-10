from django.conf.urls import url
from pcrs.generic_views import GenericCourseStaffDeleteView

from users.section_views import *

urlpatterns = [
    url(r'^change$', ChangeSectionView.as_view(),
        name='section_change'),
    url(r'^list$', SectionListView.as_view(),
        name='section_list'),
    url(r'^create$', SectionCreateView.as_view(),
        name='section_create'),
    url(r'^(?P<pk>[\w-]+)$', SectionUpdateView.as_view(),
        name='section_update'),
    url(r'^(?P<pk>[\w-]+)/delete$',
        GenericCourseStaffDeleteView.as_view(model=Section),
        name='section_delete'),
    url(r'^(?P<pk>[\w-]+)/reports$', SectionReportsView.as_view(),
        name='section_reports'),
]
