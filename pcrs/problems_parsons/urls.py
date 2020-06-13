from django.conf.urls import url

from problems.views import (ProblemCreateView, ProblemListView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from .models import Problem, Submission
from .forms import ProblemForm
from .views import (SubmissionView, SubmissionAsyncView,
                                         ProblemCreateRedirectView, ProblemCloneView,
                                         SubmissionHistoryAsyncView)

urlpatterns = [

    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='short_answer_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='short_answer_create'),

    url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm),
        name='short_answer_problem_clone'),

    url(r'^create_redirect$',
        ProblemCreateRedirectView.as_view(model=Problem, form_class=ProblemForm),
        name='short_answer_create_redirect'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_parson/problem_form.html'),
        name='short_answer_update'),

    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='short_answer_clear'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='short_answer_delete'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='short_answer_submit'),

    url(r'^embed/(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='embedded_short_answer_submit'),

    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='short_answer_async_submit'),

    url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='short_answer_async_history'),
]
