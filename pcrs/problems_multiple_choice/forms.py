from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset
from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_multiple_choice.models import Problem, Option


class ProblemForm(forms.ModelForm, BaseProblemForm):
    no_correct_response = forms.BooleanField(label="<b>Survey purposes only</b>", help_text="Click here if this problem will have no correct answer.", required=False)
    class Meta:
        model = Problem
        fields = ('name', 'description', 'tags', 'visibility', 'no_correct_response')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.save_and_add = Submit('submit', 'Save and add options',
                                   css_class='green-button-right',
                                   formaction='create_and_add_option')
        BaseProblemForm.__init__(self)


class OptionForm(BaseRelatedObjectForm):
    class Meta:
        model = Option
        widgets = {'problem': forms.HiddenInput()}
        fields = ('answer_text', 'is_correct', 'problem')

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='options',
                                       **kwargs)


class SubmissionForm(BaseSubmissionForm):
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(), widget=forms.CheckboxSelectMultiple(),
        required=False)

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
        self.fields['options'].queryset = Option.objects.filter(problem=problem)
        self.helper.layout = Layout(
            Fieldset('', 'options'),
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right')
        )
