from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from editor.views import EditorView
import problems_c.models as c_models
import problems_python.models as python_models

urlpatterns = patterns('',
    url(r'^c$',
        EditorView.as_view(model=c_models.Submission, template_name='editor/editor.html', pType='c')),

    url(r'^python$',
        EditorView.as_view(model=python_models.Submission, template_name='editor/editor.html', pType='python')),
)