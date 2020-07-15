from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_parsons.models import Problem, Submission, TestCase
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'invariant', 'starter_code', 'unit_tests', 'visible_unit', 'author', 'visibility', 'evaluation_type')
        help_texts = {
            'starter_code': _(escape('To add a distractor line, simply place it anywhere and add #distractor afterwards. To group lines, use the following form: line1<br>line2<br>...<br>lineN')),
            'unit_tests': _('Please enter as: input:"", output:"" one per line<br>'+
            'example: input:"[1,2,3]", output:"[3,2,1]"'),
            'visible_unit': _('Do you want students to see the unit tests'),
            'evaluation_type': _('How do you want to evaluate student submissions (default is line comparison). Please only select one')
        }

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)

class SubmissionForm(BaseSubmissionForm):
    submission = forms.CharField()

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        
        super().__init__(*args, **kwargs)
        self.submit_button = Button('Submit', value='Submit', css_class='green-button pull-right', id='submit')

        self.helper.layout = Layout(
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))

class TestCaseForm(BaseRelatedObjectForm):
    class Meta:
        model = TestCase
        fields = ('description', 'pre_code', 'test_input', 'expected_output', 'is_visible',
                  'problem')
        widgets = {'problem': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='testcases',
                                       **kwargs)