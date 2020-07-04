from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_parsons.models import Problem, Submission
from django.utils.translation import ugettext_lazy as _

import pdb

class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'invariant', 'starter_code', 'unit_tests', 'visible_unit', 'run_unit', 'author', 'visibility')
        help_texts = {
            'starter_code': _('To add a distractor line, simply place it anywhere and add #distractor afterwards'),
            'unit_tests': _('Please enter as: input:"", output:"" one per line'),
            'visible_unit': _('Do you want students to see the unit tests'),
            'run_unit': _('Do you want to run the unit tests you made'),
        }

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)

class SubmissionForm(BaseSubmissionForm):
    submission = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        
        super().__init__(*args, **kwargs)
        self.submit_button = Button('Submit', value='Submit', css_class='green-button pull-right', id='submit')

        self.helper.layout = Layout(
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))


