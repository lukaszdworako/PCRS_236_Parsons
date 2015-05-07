from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^c$',
        TemplateView.as_view(template_name='editor/c_editor.html')),

    url(r'^python$',
        TemplateView.as_view(template_name='editor/python_editor.html')),
)
