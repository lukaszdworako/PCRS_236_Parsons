from crispy_forms.layout import (ButtonHolder, Submit, Layout,
                                 Fieldset, Div, Button, HTML)
from django import forms

from pcrs.form_mixins import CrispyFormMixin
from problems.forms import BaseSubmissionForm
from problems_rating.models import Problem


class ProblemForm(forms.ModelForm, CrispyFormMixin):
    save_and_continue = Submit('submit', 'Save and Continue',
                          css_class='btn-success pull-right')

    class Meta:
        model = Problem
        widgets = {'max_score': forms.HiddenInput()}
        fields = ('name', 'description', 'scale_type', 'tags', 'visibility',
                         'max_score', 'author')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        CrispyFormMixin.__init__(self)

        # fields = self.Meta.create_fields
        self.buttons = (self.save_and_continue,)
        self.helper.layout = Layout(Fieldset('', *fields),
                                    ButtonHolder(*self.buttons))

class ProblemUpdateForm(forms.ModelForm, CrispyFormMixin):
    clear_button = HTML('<a class="btn btn-danger" role="button" '
                        'href="{{ object.get_absolute_url }}/clear">'
                        'Clear submissions</a>')
    save_button = Submit('submit', 'Save', css_class='btn-success pull-right')

    class Meta:
        model = Problem
        exclude = ()
        likert_fields = ('options', 'name', 'description', 'tags', 'visibility')
        slider_fields = ('minimum', 'maximum', 'increment', 'extra', 'name', 'description',
                         'tags', 'visibility')
        star_fields = ('maximum', 'increment', 'extra', 'options', 'name', 'description',
                       'tags', 'visibility')
        widgets = {'max_score': forms.HiddenInput(), 'scale_type': forms.HiddenInput(),
                   'extra': forms.CheckboxInput()}

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        CrispyFormMixin.__init__(self)

        if self.instance.scale_type == 'LIK':
            fields = self.Meta.likert_fields
            self.fields['options'].label = "Options*"
            self.fields['options'].help_text = "Enter each option on a separate line."
        elif self.instance.scale_type == 'SLI':
            fields = self.Meta.slider_fields
            self.fields['minimum'].label = "Minimum*"
            self.fields['maximum'].label = "Maximum*"
            self.fields['extra'].label = "<i><b>Use shorter slider?</b></i>"
            self.fields['increment'].label = "Increment*"
        elif self.instance.scale_type == 'STA':
            fields = self.Meta.star_fields
            self.fields['maximum'].label = "Number of stars*"
            self.fields['increment'].label = "Increment*"
            self.fields['options'].label = "Labels"
            self.fields['options'].help_text = """Enter each label on a separate line.
            A label appears when you hover over its star. Leave this field empty
            to have no labels, or enter an empty line to not have a label for that
            particular star."""
            self.fields['extra'].label = "<i><b>Use larger star icons?</b></i>"

        self.buttons = (Div(CrispyFormMixin.delete_button,
                            self.clear_button,
                            css_class='btn-group'),
                        Div(self.save_button,
                            css_class='btn-group pull-right'))

        self.helper.layout = Layout(Fieldset('', *fields),
                                    ButtonHolder(*self.buttons))


class SubmissionForm(BaseSubmissionForm):
    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
