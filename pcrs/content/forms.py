from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, ButtonHolder, Div, HTML, \
    Submit, Button
from django import forms

from content.models import Challenge, Video, Quest, SectionQuest
from content.tags import Tag
from pcrs.form_mixins import CrispyFormMixin, BaseCrispyForm

class QuestImportForm(CrispyFormMixin, forms.Form):
    json_file = forms.FileField(label="",
                help_text="<br/>Must be a .json file exported from PCRS instance<br/>")

    class Meta:
        fields = ('json_file',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import_url = '/content/import'
        import_button = Submit('import', 'Import', css_class='green-button',
                               formaction=import_url)
        self.fields['json_file'].label = "JSON file"
        self.helper.layout = Layout('json_file',
                                    ButtonHolder(import_button)
                                    )
    
    
class TagForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', )


class VideoForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = Video
        fields = ('name', 'description', 'resources', 'link', 'thumbnail', 'download', 'tags')


class ChallengeForm(CrispyFormMixin, forms.ModelForm):
    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Challenge.objects.order_by('name'),
        required=False)

    class Meta:
        model = Challenge
        fields = ('visibility', 'name', 'description', 'is_graded',
                  'prerequisites')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
        )
        if self.instance.pk:
            absUrl = self.instance.get_absolute_url()
            self.fields['prerequisites'].queryset = \
                Challenge.objects.exclude(pk=self.instance.pk).order_by('name')
            add_objects = HTML('<a class="green-button" role="button" '
                               'href="{{ object.get_absolute_url }}/objects">'
                               'Manage content</a>')
            exportUrl = '{}/export'.format(absUrl)
            export_button = Submit('export', 'Export', css_class='green-button',
                               formaction=exportUrl)
            self.helper.layout.append(
                Div(ButtonHolder(self.delete_button,
                    Div(add_objects, export_button, self.save_button,
                        css_class='button-group-right'))
                )
            )
        else:
            self.helper.layout.append(ButtonHolder(self.save_button))


class QuestForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = Quest
        fields = ('name', 'description', 'mode')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            absUrl = self.instance.get_absolute_url()
            exportUrl = '{}/export'.format(absUrl)
            export_button = Submit('export', 'Export', css_class='green-button-right',
                                   formaction=exportUrl)
            self.helper.layout.append(export_button)


class QuestSectionForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = SectionQuest
        fields = ('visibility', 'open_on', 'due_on', 'quest')
        widgets = {'quest': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_tag = False
