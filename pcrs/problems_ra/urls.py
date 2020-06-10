from django.conf.urls import url

from problems.views import *
from problems_ra.forms import ProblemForm, TestCaseForm
from problems_ra.models import Problem, TestCase, Submission
from problems_ra.views import RASyntaxReferenceView
from problems_rdb.views import (RDBTestCaseCreateView,
    RDBTestCaseCreateManyView, RDBTestCaseEditRedirectView)

from editor.views import EditorAsyncView


urlpatterns = [
    url(r'^ra_syntax$', RASyntaxReferenceView.as_view(),
        name='ra_syntax'),
    url(r'^list$', ProblemListView.as_view(model=Problem),
        name='ra_problem_list'),
    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm,
            template_name='problems_ra/problem_form.html'),
        name='ra_problem_create'),
    url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm,
            template_name='problems_ra/problem_form.html'),
        name='ra_problem_clone'),
    url(r'^create_and_add_testcase$',
        ProblemCreateAndAddTCView.as_view(model=Problem, form_class=ProblemForm),
        name='ra_problem_create_and_add_testcase'),
    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='ra_problem_clear'),
    url(r'^(?P<pk>[0-9]+)$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
            template_name='problems_ra/problem_form.html'),
        name='ra_problem_update'),
    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='ra_problem_delete'),
    url(r'^(?P<problem>[0-9]+)/testcases$',
        RDBTestCaseCreateManyView.as_view(model=TestCase,
                                          form_class=TestCaseForm),
        name='ra_problem_add_testcases'),
    url(r'^(?P<problem>[0-9]+)/testcase$',
        RDBTestCaseCreateView.as_view(model=TestCase, form_class=TestCaseForm),
        name='ra_problem_add_testcase'),
    url(r'^(?P<problem>[0-9]+)/testcase/(?P<pk>[0-9]+)/delete$',
        TestCaseDeleteView.as_view(model=TestCase),
        name='ra_problem_delete_testcase'),
    url(r'^(?P<problem>[0-9]+)/testcase/(?P<pk>[0-9]+)$',
        RDBTestCaseEditRedirectView.as_view(model=TestCase),
        name='sql_problem_edit_redirect'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(model=Submission,
                               template_name='problems_ra/submission.html'),
        name='ra_problem_submit'),
    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='ra_problem_async_submit'),
    url(r'^editor/run$',
        EditorAsyncView.as_view(model=Submission, pType='ra'),
        name='editor_problem_async_submit'),

    url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='ra_problem_async_history'),

    # monitoring
    url(r'^(?P<pk>[0-9]+)/monitor$',
        MonitoringView.as_view(model=Problem,
                               template_name='problems_rdb/monitor.html'),
        name='ra_problem_monitor'),
    url(r'^(?P<pk>[0-9]+)/monitor_data$',
        MonitoringAsyncView.as_view(model=Problem),
        name='ra_problem_get_monitor_data'),
    url(r'^(?P<pk>[0-9]+)/browse_submissions$',
        BrowseSubmissionsView.as_view(model=Problem),
        name='ra_problem_browse_submissions'),
]
