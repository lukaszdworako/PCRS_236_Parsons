from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML


class CrispyFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.render_hidden_fields = True

        self.save_button = Submit('submit', 'Save',
                                  css_class='btn-success pull-right')

        self.save_and_back = Submit('submit', 'Save and go back',
                               css_class='btn-success')

        self.delete_button = HTML('<a class="btn btn-danger" role="button" '
                                  'href="{{object.get_absolute_url}}/delete">'
                                  'Delete</a>')

        self.delete_confirm_button = Submit('submit', 'Delete',
                                  css_class='btn-danger')