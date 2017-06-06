from django.conf.urls import url

from problems.views import (ProblemCreateView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from problems_timed.models import Problem
from problems_timed.forms import ProblemForm
from problems_timed.views import (ProblemCreateRedirectView,
                                  PageCreateView, PagesCreateView,
                                  PageUpdateView, PageDeleteView,
                                  SubmissionView, ProblemListView)
from problems_timed.async_requests import AsyncAttempt, AsyncDownload

urlpatterns = [

    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='timed_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='timed_create'),

    url(r'^create_redirect$',
        ProblemCreateRedirectView.as_view(model=Problem, form_class=ProblemForm),
        name='timed_create_redirect'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_timed/problem_form.html'),
        name='timed_update'),

    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='timed_clear'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='timed_delete'),

    url(r'^(?P<problem>[0-9]+)/page$',
        PageCreateView.as_view(),
        name='timed_add_page'),

    url(r'^(?P<problem>[0-9]+)/pages$',
        PagesCreateView.as_view(),
        name='timed_add_pages'),

    url(r'^(?P<problem>[0-9]+)/page/(?P<pk>[0-9]+)/?$',
        PageUpdateView.as_view(),
        name='timed_update_page'),

    url(r'^(?P<problem>[0-9]+)/page/(?P<pk>[0-9]+)/delete$',
        PageDeleteView.as_view(),
        name='timed_delete_page'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='timed_submit'),

    url(r'^(?P<problem_pk>[0-9]+)/attempt$',
        AsyncAttempt.problem_attempt,
        name='attempt'),

    url(r'^(?P<problem_pk>[0-9]+)/download$',
        AsyncDownload.download_submissions,
        name='download'),

]
