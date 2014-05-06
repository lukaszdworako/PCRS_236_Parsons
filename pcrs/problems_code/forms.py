from crispy_forms.layout import ButtonHolder, Layout, Fieldset, Submit, Div
from django import forms
from pcrs.form_mixins import CrispyFormMixin

from problems import forms as problem_forms
from problems_code.models import Problem, Submission, TestCase


class ProblemForm(problem_forms.ProblemForm, forms.ModelForm):
    class Meta:
        model = Problem

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.buttons = ButtonHolder(Submit('submit', 'Save and add testcases',
                                          css_class='btn-success pull-right',
                                          formaction='create_and_add_testcase'))

        self.helper.layout = Layout(
            Fieldset(
                '', 'language', 'name', 'description', 'starter_code',
                'solution', 'tags', 'visibility'),
            self.buttons
        )


class TestCaseForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = TestCase
        widgets = {'problem': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        save_and_add = Submit('submit', 'Save and add another',
                              css_class='btn-success',
                              formaction='testcases')

        buttons = Div(save_and_add if not self.instance.pk else None,
                      self.save_and_back,
                      css_class='btn-group pull-right')
        self.helper.layout = Layout(
            Fieldset(
                '', 'description', 'test_input', 'expected_output', 'is_visible'
            ),
            ButtonHolder(self.delete_button if self.instance.pk else None,
                         buttons)
        )


class SubmissionForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('student', 'problem', 'submission', 'section')
        widgets = {
            'student': forms.HiddenInput(),
            'problem': forms.HiddenInput(),
            'section': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_show_labels = False
        submit_button = Submit('submit', 'Submit',
                               css_class='btn-success pull-right')
        self.helper.layout = Layout(
            Fieldset('', 'submission'), submit_button)