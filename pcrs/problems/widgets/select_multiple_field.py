# Taken from https://github.com/kelvinwong-ca/django-select-multiple-field

from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.html import escape

try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt

try:
    from django.utils.html import format_html
except ImportError:
    def format_html(format_string, *args, **kwargs):
        return format_string.format(*args, **kwargs)

from traceback import print_tb


HTML_ATTR_CLASS = 'select-multiple-field'


class SelectMultipleField(widgets.SelectMultiple):
    """Multiple select widget ready for jQuery multiselect.js"""

    allow_multiple_selected = True

    def render(self, name, value, attrs={}, choices=()):
        rendered_attrs = {'class': HTML_ATTR_CLASS}
        rendered_attrs.update(attrs)
        if value is None:
            value = []



        additional_attr = {'name': name}

        final_attrs = self.build_attrs(rendered_attrs, additional_attr)
        output = [format_html('<select multiple="multiple"{0}>',
                              flatatt(final_attrs))]

        # Hacky, re-work this later (not sure about options API, was changed in 1.11)
        for option in self.options(choices, value):
            for selected_option in value:
                if selected_option == option['value']:
                    output.append("<option selected='selected' value={}>{}</option>"
                        .format(escape(option['value']), escape(option['label'])))
                    break
            else:
                output.append("<option value={}>{}</option>"
                    .format(escape(option['value']), escape(option['label'])))

        output.append('</select>')
        return mark_safe('\n'.join(output))

    def value_from_datadict(self, data, files, name):
        """
        SelectMultipleField widget delegates processing of raw user data to
        Django's SelectMultiple widget

        Returns list or None
        """
        return super(SelectMultipleField, self).value_from_datadict(
            data, files, name)
