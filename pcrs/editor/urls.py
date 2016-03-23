from django.conf.urls import patterns, url
from editor.views import EditorView

import problems_c.models as c_models
import problems_python.models as python_models
import problems_ra.models as ra_models

from editor import editor_requests


urlpatterns = patterns('',
    url(r'^c/submit$',
        EditorView.as_view(template_name='editor/editor.html', model=c_models.Submission, pType='c')),
    url(r'^python/submit$',
        EditorView.as_view(template_name='editor/editor.html', model=python_models.Submission, pType='python')),
    url(r'^ra/submit$',
        EditorView.as_view(template_name='editor/editor.html', model=ra_models.Submission, pType='ra')),
)
