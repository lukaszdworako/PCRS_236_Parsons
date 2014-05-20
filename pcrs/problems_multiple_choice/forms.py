from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset
from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_multiple_choice.models import Problem, Option


class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('description', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.save_and_add = Submit('submit', 'Save and add options',
                                   css_class='btn-success pull-right',
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