from crispy_forms.layout import Submit, Fieldset, Layout
from django import forms
from pcrs.form_mixins import CrispyFormMixin
from users.models import Section


class SectionSelectionForm(CrispyFormMixin, forms.Form):
    section = forms.ModelChoiceField(queryset=Section.objects.all(),
                                     empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', 'section'), self.save_button)