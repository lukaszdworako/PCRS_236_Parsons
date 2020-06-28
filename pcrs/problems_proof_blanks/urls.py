from django.conf.urls import url

from problems.views import (ProblemCreateView, ProblemListView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from problems_proof_blanks.models import Problem, Submission
from problems_proof_blanks.forms import ProblemForm
from problems_proof_blanks.views import (SubmissionView, SubmissionAsyncView,
                                         ProblemCreateRedirectView, ProblemCloneView,
                                         SubmissionHistoryAsyncView)

urlpatterns = [

    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='proof_blanks_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_proof_blanks/problem_form.html'),
        name='proof_blanks_create'),

    url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm),
        name='proof_blanks_problem_clone'),

    url(r'^create_redirect$',
        ProblemCreateRedirectView.as_view(model=Problem, form_class=ProblemForm),
        name='proof_blanks_create_redirect'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_proof_blanks/problem_form.html'),
        name='proof_blanks_update'),

    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='proof_blanks_clear'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='proof_blanks_delete'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='proof_blanks_submit'),

    url(r'^embed/(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='embedded_proof_blanks_submit'),

    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='proof_blanks_async_submit'),

    url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='proof_blanks_async_history'),
]
