from django.conf.urls import patterns, url
from problems_r.models import Problem, Submission
from problems_r.views import *
from problems_r.forms import ProblemForm
from problems.views import *
from editor.views import EditorAsyncView

urlpatterns = patterns('',
	url(r"^script/create$", ScriptCreateView.as_view(),
		name="script_create"),
	url(r"^script/create_and_run$", ScriptCreateAndRunView.as_view(),
		name="script_create_and_run"),
	url(r"^script/(?P<pk>[0-9]+)/delete$", ScriptDeleteView.as_view(),
		name="script_delete"),
	url(r"^script/(?P<pk>[0-9]+)$", ScriptDetailView.as_view(),
		name="script_view"),
	url(r"^script/list$", ScriptListView.as_view(),
		name="script_list"),
	url(r"^list$", ProblemListView.as_view(model=Problem),
		name="coding_problem_list"),
	url(r"^create$", ProblemCreateView.as_view(model=Problem,
		form_class=ProblemForm, template_name="problems_r/problem_form.html"),
		name="code_problem_create"),
	url(r'^(?P<pk>[0-9]+)/?$', ProblemUpdateView.as_view(
		model=Problem, form_class=ProblemForm,
        template_name='problems_r/problem_form.html'),
		name="coding_problem_update"),
	url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='coding_problem_delete'),
	url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(model=Submission,
        template_name='problems_r/submission.html'),
        name='coding_problem_submit'),
	url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='coding_problem_async_submit'),
	url(r'^editor/run$',
        EditorAsyncView.as_view(model=Submission, pType='r'),
        name='editor_problem_async_submit'),
	url(r'^(?P<problem>[0-9]+)/history$',
        SubmissionHistoryAsyncView.as_view(model=Submission),
        name='coding_problem_async_history'),
	url(r'^(?P<pk>[0-9]+)/monitor$',
        MonitoringView.as_view(model=Problem),
        name='coding_problem_monitor'),
	url(r'^(?P<pk>[0-9]+)/monitor_data$',
        MonitoringAsyncView.as_view(model=Problem),
        name='coding_problem_get_monitor_data'),
	url(r'^(?P<pk>[0-9]+)/browse_submissions$',
        BrowseSubmissionsView.as_view(model=Problem),
        name='coding_problem_browse_submissions'),
	url(r'^graph/(?P<image>[a-zA-Z0-9]+)$',
        render_graph,
        name='render_graph'),
	url(r'^embed/(?P<problem>[0-9]+)/submit$', SubmissionView.as_view(model=Submission,
								template_name='problems_r/submission.html'),
								name='embedded_coding_problem_submit'),
	url(r"^embed/script/(?P<pk>[0-9]+)$", ScriptDetailView.as_view(),
		name="embedded_script_view"),
	)
