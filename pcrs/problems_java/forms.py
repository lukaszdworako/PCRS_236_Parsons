from django import forms
from crispy_forms.layout import HTML

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm
from .models import Problem


class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'starter_code', 'solution',
                  'test_suite', 'visualizer_code', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)

        self.fields['starter_code'].initial = '[file NewFile.java]\n\n[/file]'

