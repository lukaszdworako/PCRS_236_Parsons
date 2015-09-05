from django import forms

from problems.forms import BaseProblemForm
from problems_rdb.forms import RDBTestCaseForm
from problems_sql.models import Problem, TestCase


class ProblemForm(forms.ModelForm, BaseProblemForm):
    """
    Form for creating an SQL problem.
    """
    solution = forms.CharField(required=True, widget=forms.Textarea())

    class Meta:
        model = Problem
        fields = ('visibility', 'schema', 'name', 'description', 'starter_code',
                  'solution', 'order_matters')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)


class TestCaseForm(RDBTestCaseForm):
    """
    Form for creating a SQL problem testcase.
    """
    class Meta:
        model = TestCase
        widgets = {'problem': forms.HiddenInput()}
        fields = ('problem', 'dataset', 'description', 'is_visible')