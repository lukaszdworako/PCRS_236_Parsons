from django.conf.urls import patterns, url

from problems.views import *
from problems_rdb.views import RDBTestCaseCreateView, RDBTestCaseCreateManyView
from problems_sql.models import Problem, TestCase, Submission
from problems_sql.forms import ProblemForm, TestCaseForm

urlpatterns = patterns('',
    url(r'^list$', ProblemListView.as_view(model=Problem),
        name='sql_problem_list'),
    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='sql_problem_create'),
   url(r'^(?P<pk>[0-9]+)/clone$',
        ProblemCloneView.as_view(model=Problem, form_class=ProblemForm),
        name='sql_problem_clone'),
    url(r'^create_and_add_testcase$',
        ProblemCreateAndAddTCView.as_view(model=Problem, form_class=ProblemForm),
        name='sql_problem_create_and_add_testcase'),
    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='sql_problem_clear'),
    url(r'^(?P<pk>[0-9]+)$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemForm,
                    template_name='problems_rdb/rdb_problem_form.html'),
        name='sql_problem_update'),
    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='sql_problem_delete'),
    url(r'^(?P<problem>[0-9]+)/testcases$',
        RDBTestCaseCreateManyView.as_view(model=TestCase,
                                          form_class=TestCaseForm),
        name='sql_problem_add_testcases'),
    url(r'^(?P<problem>[0-9]+)/testcase$',
        RDBTestCaseCreateView.as_view(model=TestCase, form_class=TestCaseForm),
        name='sql_problem_add_testcase'),
    url(r'^(?P<problem>[0-9]+)/testcase/(?P<pk>[0-9]+)/delete$',
        TestCaseDeleteView.as_view(model=TestCase),
        name='sql_problem_delete_testcase'),
    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(model=Submission,
                               template_name='problems_rdb/submission.html'),
        name='sql_problem_submit'),

    # monitoring
    url(r'^(?P<pk>[0-9]+)/monitor$',
        MonitoringView.as_view(model=Problem,
                               template_name='problems_rdb/monitor.html'),
        name='sql_problem_monitor'),
    url(r'^(?P<pk>[0-9]+)/monitor_data$',
        MonitoringAsyncView.as_view(model=Problem),
        name='sql_problem_get_monitor_data'),
    )