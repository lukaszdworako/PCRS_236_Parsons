from django.conf.urls import url

from problems.views import (ProblemCreateView, ProblemListView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from problems_parsons.models import Problem, Submission
from problems_parsons.forms import ProblemForm
from problems_parsons.views import (SubmissionView, SubmissionAsyncView,
                                         ProblemCreateRedirectView, ProblemCloneView,
                                         SubmissionHistoryAsyncView)

urlpatterns = [

    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='parsons_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm,template_name='problems_parsons/problem_form.html'),
        name='parsons_create'),

    url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm),
        name='parsons_problem_clone'),

    url(r'^create_redirect$',
        ProblemCreateRedirectView.as_view(model=Problem, form_class=ProblemForm),
        name='parsons_create_redirect'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_parsons/problem_form.html'),
        name='parsons_update'),

    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='parsons_clear'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='parsons_delete'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(
        template_name='problems_parsons/submission.html'),
        name='parsons_submit'),

    url(r'^embed/(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='embedded_parsons_submit'),

    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='parsons_async_submit'),

    url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='parsons_async_history'),
]
