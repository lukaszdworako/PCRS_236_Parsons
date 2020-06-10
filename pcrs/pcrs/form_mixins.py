from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Div, Submit, HTML, Layout, ButtonHolder,
                                 Fieldset)
from django import forms


class CrispyFormMixin:
    save_button = Submit('submit', 'Save',
                              css_class='green-button-right')

    delete_button = HTML('<a class="red-button" role="button" '
                                  'href="{{object.get_absolute_url}}/delete">'
                                  'Delete</a>')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.render_hidden_fields = True


class BaseCrispyForm(CrispyFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
            ButtonHolder(self.delete_button if self.instance.pk else None,
                         self.save_button)
        )


class BaseRelatedObjectForm(CrispyFormMixin, forms.ModelForm):
    save_and_back = Submit('submit', 'Save and go back',
                               css_class='btn-success')

    def __init__(self, *args, **kwargs):
        formaction = kwargs.pop('formaction')
        super().__init__(*args, **kwargs)
        self.save_and_add = Submit('submit', 'Save and add another',
                                   css_class='btn-success',
                                   formaction=formaction)
        if self.instance.pk:
            self.buttons = Div(self.delete_button, Div(self.save_and_back,
                                css_class='button-group-right'))
        else:
            self.buttons = Div(Div(self.save_and_add, self.save_and_back,
                                   css_class='button-group-right'))

        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))