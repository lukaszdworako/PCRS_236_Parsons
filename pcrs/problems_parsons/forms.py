from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_parsons.models import Problem, Submission
from django.utils.translation import ugettext_lazy as _

class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'starter_code', 'author', 'visibility')
        help_texts = {}

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
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


