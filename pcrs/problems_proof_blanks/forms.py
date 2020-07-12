from crispy_forms.layout import HTML, ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms
from django.contrib.postgres.forms.jsonb import JSONField

from pcrs.form_mixins import CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_proof_blanks.models import Problem, Submission

from django.utils.translation import ugettext_lazy as _



class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        no_correct_response = forms.BooleanField(label="<b>Survey purposes only</b>",
                                           help_text="Click here if this problem will have no correct answer.",
                                           required=False)
        fields = ('name', 'proof_statement', 'incomplete_proof', 'no_correct_response', 'answer_keys',
                  'feedback_keys', 'hint_keys','notes', 'author', 'tags', 'visibility', 'scaling_factor')
        help_texts = {
            'answer_keys': _('Answer keys follow the format: <br> \
            { <br> \
                "1": "Strong Induction", <br>\
                "Blank 2": "(a * 2) ** 2 + 1", <br>\
                "Third Blank": "3" <br>\
            }'),
            'hint_keys': _('Hint keys follow the format: <br> \
            { <br> \
                "1": "Think of the induction type where you assume for everything before a certain value", <br>\
                "Blank 2": "A mathematical expression" <br>\
            }'),
            'feedback_keys': _('Hint keys follow the format: <br> \
            { <br> \
                "1": {"type": "string", "Weak Induction": "Think of something stronger"}, <br>\
                "Blank 2": {"type": "mathexpr"}, <br>\
                "third": {"type": "int", "lambda ans: ans > 3"}, <br>\
            }'),
        }

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.save_and_add = Submit('submit', 'Save',
                               css_class='green-button-right',
                               formaction='create_redirect')
        BaseProblemForm.__init__(self)


class SubmissionForm(BaseSubmissionForm):
    # TODO -- turn submission into a json fields
    submission = forms.CharField(widget=forms.Textarea())
    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        description = HTML('<p>{}:</p>'.format(problem.proof_statement))
        incomplete_proof = HTML('<p>{}</p> <br>'.format(problem.incomplete_proof))
        super().__init__(*args, **kwargs)
        fieldsets = []
        for question in problem.answer_keys:
            self.fields["submission_{}".format(question)] = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':1, 'size': '5'}), required=False, label=question, max_length=20)
            fieldsets.append(HTML('<span> <label> {}'.format(question)))
            fieldsets.append((Fieldset('', Field("submission_{}".format(question), maxlength=20))))
            fieldsets.append(HTML('<button type="button">Hint</button></label> </span>'))
            
        self.helper.layout = Layout(
            description,
            incomplete_proof,
            *fieldsets,
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))