from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms

from pcrs.form_mixins import CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_parsons.models import Problem, Submission

from django.utils.translation import ugettext_lazy as _

class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'description', 'max_score', 'keys', 'max_chars', 'min_chars', 'author', 'tags', 'visibility')
        help_texts = {
            'keys': _('Keys follow the format: <br> \
            { <br> \
                "key1, key2, ...": "hint", <br>\
                "key1, key2, ...": "hint" <br>\
            }'),
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
            Fieldset('', Field('submission', maxlength=problem.max_chars)),
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))
