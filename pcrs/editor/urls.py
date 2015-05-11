from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from editor.views import EditorView, EditorAsyncView
import problems_c.models as c_models
import problems_python.models as python_models

urlpatterns = patterns('',
    url(r'^c/submit$',
        EditorView.as_view(template_name='editor/editor.html', pType='c')),

    url(r'^python/submit$',
        EditorView.as_view(template_name='editor/editor.html', pType='python')),

    url('/problems/c/editor/run',
        EditorAsyncView.as_view(model=c_models.Submission),
        name='c_editor_async_submit'),
)