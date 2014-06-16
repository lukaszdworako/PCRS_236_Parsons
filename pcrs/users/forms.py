from crispy_forms.layout import Submit, Fieldset, Layout, HTML, Div, \
    ButtonHolder
from django import forms
from pcrs.form_mixins import CrispyFormMixin, BaseCrispyForm
from users.models import Section


class SectionSelectionForm(CrispyFormMixin, forms.Form):
    section = forms.ModelChoiceField(queryset=Section.objects.all(),
                                     empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', 'section'), self.save_button)


class SectionForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Section
        fields = ('section_id', 'lecture_time', 'location')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
        )
        manage_quests_href = '/content/quests/section/{{object.pk}}'
        if self.instance.pk:
            manage_quests = HTML('<a class="btn btn-success" role="button" '
                               'href="{}">Manage quests</a>'.format(
                manage_quests_href))
            self.helper.layout.append(
                Div(ButtonHolder(self.delete_button,
                    Div(manage_quests, self.save_button,
                        css_class='btn-group pull-right'))
                )
            )
        else:
            self.helper.layout.append(ButtonHolder(self.save_button))