from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm
from .models import Problem, TestCase


class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'starter_code', 'solution',
                  'test_suite', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)


class TestCaseForm(BaseRelatedObjectForm):
    class Meta:
        model = TestCase
        fields = ('description', 'test_name', 'is_visible',
                  'problem')
        widgets = {'problem': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='testcases',
                                       **kwargs)

