from django.conf.urls import patterns, url

from problems.views import (ProblemListView, ProblemCreateView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from problems_timed.models import Problem
from problems_timed.forms import ProblemForm
from problems_timed.views import (TermCreateView, TermsCreateView,
                                  TermUpdateView, TermDeleteView,
                                  SubmissionView)

urlpatterns = patterns('',
                       
    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='timed_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='timed_create'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
        template_name='problems_timed/problem_form.html'),
        name='timed_update'),
    
    # add problem clone view
    
    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='timed_clear'),
    
    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='timed_delete'),

    url(r'^(?P<problem>[0-9]+)/term$',
        TermCreateView.as_view(),
        name='timed_add_term'),

    url(r'^(?P<problem>[0-9]+)/terms$',
        TermsCreateView.as_view(),
        name='timed_add_terms'),

    url(r'^(?P<problem>[0-9]+)/term/(?P<pk>[0-9]+)/?$',
        TermUpdateView.as_view(),
        name='timed_update_term'),

    url(r'^(?P<problem>[0-9]+)/term/(?P<pk>[0-9]+)/delete$',
        TermDeleteView.as_view(),
        name='timed_delete_term'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='timed_submit'),
    
    # add monitor view
    
)