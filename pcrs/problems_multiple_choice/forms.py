from crispy_forms.layout import ButtonHolder, Div, Submit, Layout, Fieldset
from django import forms
from pcrs.form_mixins import CrispyFormMixin

from problems import forms as problem_forms
from problems_multiple_choice.models import Problem, Option


class ProblemForm(problem_forms.ProblemForm, forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('description', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)

        if not self.instance.pk:
            self.buttons = ButtonHolder(Submit('submit', 'Save and add option',
                                        css_class='btn-success pull-right',
                                        formaction='create_and_add_option'))

        self.helper.layout = Layout(
            Fieldset('', 'description', 'tags', 'visibility'),
            self.buttons
        )


class OptionForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Option
        widgets = {'problem': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        save_and_add = Submit('submit', 'Save and add another',
                              css_class='btn-success',
                              formaction='options')
        buttons = Div(save_and_add if not self.instance.pk else None,
                      self.save_and_back,
                      css_class='btn-group pull-right')
        self.helper.layout = Layout(
            Fieldset(
                '', 'answer_text', 'is_correct'
            ),
            ButtonHolder(self.delete_button if self.instance.pk else None,
                         buttons)
        )


class SubmissionForm(CrispyFormMixin, forms.Form):
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(), widget=forms.CheckboxSelectMultiple(),
        required=False)

    def __init__(self, *args, **kwargs):
        problem = kwargs.pop('problem', None)
        super().__init__(*args, **kwargs)
        self.fields['options'].queryset = Option.objects.filter(problem=problem)

        submit_button = Submit('submit', 'Submit',
                               css_class='btn-success pull-right')
        self.helper.layout = Layout(
            Fieldset('', 'options'), submit_button)