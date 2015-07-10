from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from editor.views import EditorView, EditorAsyncView
import problems_c.models as c_models
import problems_python.models as python_models

from editor import editor_requests

urlpatterns = patterns('',
    url(r'^c/submit$',
        EditorView.as_view(template_name='editor/editor.html', model=c_models.Submission, pType='c')),
    url(r'^new-visualizer-details-editor$', editor_requests.new_visualizer_details_editor, name='new_visualizer_details_editor'),

    url(r'^python/submit$',
        EditorView.as_view(template_name='editor/editor.html', model=python_models.Submission, pType='python')),
)
