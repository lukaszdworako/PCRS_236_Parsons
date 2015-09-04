from django import forms

from problems.forms import BaseProblemForm
from problems_ra.models import Problem, TestCase
from problems_rdb.forms import RDBTestCaseForm


class ProblemForm(forms.ModelForm, BaseProblemForm):
    """
    Form for creating an RA problem.
    """
    solution = forms.CharField(required=True, widget=forms.Textarea())
    grammar = forms.ChoiceField(choices=Problem.GRAMMARS)
    semantics = forms.ChoiceField(choices=Problem.SEMANTICS)

    class Meta:
        model = Problem
        fields = ('visibility', 'schema', 'name', 'description', 'starter_code',
                  'solution', 'grammar', 'semantics')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)


class TestCaseForm(RDBTestCaseForm):
    """
    Form for creating an RA problem testcase.
    """
    class Meta:
        model = TestCase
        widgets = {'problem': forms.HiddenInput()}
        fields = ('problem', 'dataset', 'description', 'is_visible')