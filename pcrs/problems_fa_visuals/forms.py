from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms

from pcrs.form_mixins import CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_fa_visuals.models import Problem, Submission

from django.utils.translation import ugettext_lazy as _

class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'regex', 'author', 'tags', 'visibility')
        help_texts = {
            'regex': _('Regular expressions follow the format: <br>' 
            # ε is the empty string <br> \
            +'() for grouping <br> \
            * for Kleene star <br> '
            # Put a space between expressions for concatenation <br> \
             +
            ' + for alternation <br>' +
            'e.g. (a|b)+cd is valid <br>' 
            ),
        }

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
            Fieldset('', Field('submission')),
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))
