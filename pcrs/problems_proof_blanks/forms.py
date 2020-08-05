from crispy_forms.layout import HTML, ButtonHolder, Submit, Layout, Fieldset, Div, Button, Field
from django import forms
from django.contrib.postgres.forms.jsonb import JSONField

from pcrs.form_mixins import CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_proof_blanks.models import Problem, Feedback, Submission

from django.utils.translation import ugettext_lazy as _



class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        no_correct_response = forms.BooleanField(label="<b>Survey purposes only</b>",
                                           help_text="Click here if this problem will have no correct answer.",
                                           required=False)
        fields = ('name', 'proof_statement', 'incomplete_proof', 'answer_keys', 'no_correct_response', 'notes', 'author', 'tags', 'visibility', 'scaling_factor')
        help_texts = {'answer_keys': _('Answer keys follow the format: <br> \
            { <br> \
                "1": "Strong Induction", <br>\
                "Blank 2": "(a * 2) ** 2 + 1", <br>\
                "Third Blank": "3" <br>\
            }')}


    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.save_and_add_button = Submit('submit', 'Save and add testcases',
            css_class='green-button-right',
            formaction='create_and_add_testcase')
        BaseProblemForm.__init__(self)
    

    def _createButtons(self):
        '''Generate the buttons for the problem form.

        Returns:
            A tuple of button elements
        '''
        absUrl = self.instance.get_absolute_url()
        cloneUrl = '{}/clone'.format(absUrl)
        clearUrl = '{}/clear'.format(absUrl)

        self.clear_button = HTML('<a class="red-button" role="button" '
            'onclick="showClearSubmissionsDialog(\'' + clearUrl + '\')">'
            'Clear submissions</a>')
        clone_button = Submit('clone', 'Clone',
            css_class='green-button', formaction=cloneUrl)
        save_button = Submit('submit', 'Save',
            css_class='green-button-right')
        attempt_button = Submit('attempt', 'Save & Attempt',
            css_class='green-button-right')

        # if existing feedback, redirect to edit page
        if hasattr(self.instance, 'feedback'):
            add_button = Submit('submit', 'Save and edit feedback',
                css_class='green-button-right',
                formaction='{0}/feedback/{0}'.format(self.instance.pk))
        else:
            add_button = Submit('submit', 'Save and add feedback',
                css_class='green-button-right',
                formaction='{}/feedback'.format(self.instance.pk))

        # Existing problem
        if self.instance.pk:
            return (
                Div(CrispyFormMixin.delete_button, self.clear_button,
                    css_class='button-group'),
                Div(clone_button, save_button, add_button, attempt_button,
                    css_class='button-group-right'),
            )
        # Cloning a problem
        elif self.instance:
            return save_button,
        # Creating a new problem
        else:
            return self.save_and_add_button,



class FeedbackForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('feedback_keys', 'hint_keys', 'problem')
        widgets = {'problem': forms.HiddenInput()}
        help_texts = {
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
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
        self.save_button = Submit('submit', 'Save',
                                   css_class='green-button-right')
        if self.instance.pk:
            self.buttons = Div(self.delete_button, Div(self.save_button, 
                                   css_class='button-group-right'))
        else:
            self.buttons = Div(Div(self.save_button, 
                                   css_class='button-group-right'))
        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))


class SubmissionForm(BaseSubmissionForm):
    # TODO -- turn submission into a json fields
    submission = forms.CharField(widget=forms.Textarea())
    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
        fieldsets = []
        for question in problem.answer_keys:
            self.fields["submission_{}".format(question)] = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':1, 'size': '5'}), required=False, label=question, max_length=20)
            fieldsets.append(HTML('<span> <label> {}'.format(question)))
            fieldsets.append((Fieldset('', Field("submission_{}".format(question), maxlength=20))))
            fieldsets.append(HTML('''<div id="proof_blanks-hints-{0}"> 
                                     <button type="button" onClick="hintHandler('{0}', '{1}')">Hint</button>
                                     </div>
                                     </label> </span>'''.format(question, problem.feedback.hint_keys[question])))
            
        self.helper.layout = Layout(
            *fieldsets,
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right'))