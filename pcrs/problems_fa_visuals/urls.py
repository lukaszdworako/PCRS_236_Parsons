from django.conf.urls import url

from problems.views import (ProblemCreateView, ProblemListView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from problems_fa_visuals.models import Problem, Submission
from problems_fa_visuals.forms import ProblemForm
from problems_fa_visuals.views import (SubmissionView, SubmissionAsyncView,
                                         ProblemCreateRedirectView, ProblemCloneView,
                                         SubmissionHistoryAsyncView)

urlpatterns = [

    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='fa_visuals_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='fa_visuals_create'),

    url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm),
        name='fa_visuals_problem_clone'),

    url(r'^create_redirect$',
        ProblemCreateRedirectView.as_view(model=Problem, form_class=ProblemForm),
        name='fa_visuals_create_redirect'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_fa_visuals/problem_form.html'),
        name='fa_visuals_update'),

    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='fa_visuals_clear'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='fa_visuals_delete'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='fa_visuals_submit'),

    url(r'^embed/(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='embedded_fa_visuals_submit'),

    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='fa_visuals_async_submit'),

    url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='fa_visuals_async_history'),
]
