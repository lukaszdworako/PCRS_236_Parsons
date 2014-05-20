from django.conf.urls import patterns, url

from problems.views import (ProblemClearView, ProblemListView,
                            ProblemDeleteView, ProblemCreateView,
                            ProblemUpdateView)

from problems_multiple_choice.forms import ProblemForm
from problems_multiple_choice.models import Problem
from problems_multiple_choice.views import (OptionCreateView,
                                            OptionDeleteView, OptionUpdateView,
                                            ProblemCreateAndAddOptView,
                                            SubmissionView, OptionsCreateView)


urlpatterns = patterns('',
    url(r'^list$', ProblemListView.as_view(model=Problem),
        name='mc_problem_list'),
    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='mc_problem_create'),
    url(r'^clone$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='mc_problem_clone'),
    url(r'^clone$',
        ProblemCreateAndAddOptView.as_view(model=Problem, form_class=ProblemForm),
        name='mc_problem_create_and_add_option'),
    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_multiple_choice/problem_form.html'),
        name='mc_problem_update'),
    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='mc_problem_clear'),
    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='mc_problem_delete'),
    url(r'^(?P<problem>[0-9]+)/options$', OptionsCreateView.as_view(),
        name='mc_problem_add_options'),
    url(r'^(?P<problem>[0-9]+)/option$', OptionCreateView.as_view(),
        name='mc_problem_add_option'),
    url(r'^(?P<problem>[0-9]+)/option/(?P<pk>[0-9]+)/?$',
        OptionUpdateView.as_view(),
        name='mc_problem_update_option'),
    url(r'^(?P<problem>[0-9]+)/option/(?P<pk>[0-9]+)/delete$',
        OptionDeleteView.as_view(),
        name='mc_problem_delete_option'),
    url(r'^(?P<problem>[0-9]+)/submit$', SubmissionView.as_view(),
        name='mc_problem_submit'),
)