from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm
from problems_python.models import Problem, TestCase


class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'starter_code',
                  'solution', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)


class TestCaseForm(BaseRelatedObjectForm):
    class Meta:
        model = TestCase
        fields = ('description', 'test_input', 'expected_output', 'is_visible',
                  'problem')
        widgets = {'problem': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='testcases',
                                       **kwargs)
