from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms

from pcrs.form_mixins import CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_short_answer.models import Problem, Submission


class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'max_score', 'solution', 'max_chars', 'author', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.save_and_add = Submit('submit', 'Save',
                               css_class='green-button-right',
                               formaction='create_redirect')
        BaseProblemForm.__init__(self)


class SubmissionForm(BaseSubmissionForm):
    submission = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', Field('submission', maxlength=problem.max_chars)),
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))
