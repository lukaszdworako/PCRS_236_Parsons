from crispy_forms.layout import Submit, HTML, ButtonHolder, Div
from django import forms

from pcrs.form_mixins import CrispyFormMixin
from problems.models import ProblemTag, AbstractProblem


class ProblemForm(CrispyFormMixin):
    tags = forms.ModelMultipleChoiceField(queryset=ProblemTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(), required=False)
    visibility = forms.ChoiceField(choices=AbstractProblem.visibility_levels)

    clear_button = HTML('<a class="btn btn-danger" role="button" '
                 'href="{{ object.get_absolute_url }}/clear">'
                 'Clear submissions</a>')
    save_button = Submit('submit', 'Save', css_class='btn-success pull-right')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = ButtonHolder(
                Div(self.delete_button,
                    self.clear_button,
                    css_class='btn-group'),
                self.save_button
        )