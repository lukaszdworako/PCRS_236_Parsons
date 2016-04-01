from django.conf.urls import patterns, url

from problems.views import *
from problems.st_async_requests import visualizer_details

from .forms import ProblemForm, TestCaseForm
from .models import Problem, TestCase, Submission

from editor.views import EditorAsyncView


urlpatterns = patterns('',
    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='coding_problem_list'),

    # Using C forms since they support the tag editor
    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm,
                                  template_name='problems_c/problem_form.html'),
        name='coding_problem_create'),
    url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm,
                                 template_name='problems_c/problem_form.html'),
        name='code_problem_clone'),
    url(r'^create_and_add_testcase$',
        ProblemCreateAndAddTCView.as_view(model=Problem, form_class=ProblemForm),
        name='coding_problem_create_and_add_testcase'),
    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
                                  template_name='problems_c/problem_form.html'),
        name='coding_problem_update'),
    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='coding_problem_clear'),
    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='coding_problem_delete'),
    url(r'^(?P<problem>[0-9]+)/testcases$',
        TestCaseCreateManyView.as_view(model=TestCase, form_class=TestCaseForm),
        name='coding_problem_add_testcases'),
    url(r'^(?P<problem>[0-9]+)/testcase$',
        TestCaseCreateView.as_view(model=TestCase, form_class=TestCaseForm),
        name='coding_problem_add_testcase'),
    url(r'^(?P<problem>[0-9]+)/testcase/(?P<pk>[0-9]+)/?$',
        TestCaseUpdateView.as_view(model=TestCase, form_class=TestCaseForm),
        name='coding_problem_update_testcase'),
    url(r'^(?P<problem>[0-9]+)/testcase/(?P<pk>[0-9]+)/delete$',
        TestCaseDeleteView.as_view(model=TestCase),
        name='coding_problem_delete_testcase'),
    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(model=Submission,
                               template_name='problems_java/submission.html'),
        name='coding_problem_submit'),
    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='coding_problem_async_submit'),
    #url(r'^editor/run$',
    #    EditorAsyncView.as_view(model=Submission, pType='java'),
    #    name='editor_problem_async_submit'),
    url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='coding_problem_async_history'),

    url(r'^visualizer-details$', visualizer_details, name='visualizer details'),

    # monitoring
    url(r'^(?P<pk>[0-9]+)/monitor$',
        MonitoringView.as_view(model=Problem),
        name='coding_problem_monitor'),
    url(r'^(?P<pk>[0-9]+)/monitor_data$',
        MonitoringAsyncView.as_view(model=Problem),
        name='coding_problem_get_monitor_data'),

    url(r'^(?P<pk>[0-9]+)/browse_submissions$',
        BrowseSubmissionsView.as_view(model=Problem),
        name='coding_problem_browse_submissions'),
)