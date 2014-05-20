from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.layout import Fieldset, Layout, ButtonHolder, Field, Div
from django import forms

from content.models import Challenge, ProblemSet
from pcrs.form_mixins import CrispyFormMixin
from problems_code.models import Problem as CodeProblem
from problems_multiple_choice.models import Problem as MCProblem


class ChallengeForm(CrispyFormMixin, forms.ModelForm):
    problems_code = forms.ModelMultipleChoiceField(queryset=CodeProblem.objects.all(),
                                          widget=forms.CheckboxSelectMultiple(),
                                          required=False)
    problems_multiple_choice = forms.ModelMultipleChoiceField(
        queryset=MCProblem.objects.all(),
        widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = Challenge

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', 'name', 'description', 'visibility'),
            Div(Div(TabHolder(Tab('Code', 'problems_code'),
                      Tab('MC', 'problems_multiple_choice'),
                ), css_class='col-lg-4'),
            Div(Field('markup', rows=42), css_class='col-lg-8 pull-right'),
                css_class='row'),
            Div(ButtonHolder(self.delete_button if self.instance.pk else None,
                         self.save_button))
        )


class ProblemSetForm(CrispyFormMixin, forms.ModelForm):
    """
    A form for creating a ProblemSet.
    """


    name = forms.CharField(required=True)
    description = forms.CharField(required=True)
    problems_code = forms.ModelMultipleChoiceField(
        queryset=CodeProblem.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False)
    problems_multiple_choice = forms.ModelMultipleChoiceField(
        queryset=MCProblem.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False)

    class Meta:
        model = ProblemSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'name', 'description',
            TabHolder(Tab('Code', 'problems_code'),
                      Tab('MC', 'problems_multiple_choice')
            ),
            ButtonHolder(self.save_button)
        )