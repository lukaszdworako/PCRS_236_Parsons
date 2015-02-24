from crispy_forms.layout import Submit, Fieldset, Layout, HTML, Div, \
    ButtonHolder
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from content.models import Quest
from pcrs.form_mixins import CrispyFormMixin, BaseCrispyForm
from users.models import Section, PCRSUser


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
        manage_quests_href = settings.SITE_PREFIX + '/content/quests/section/{{object.pk}}'
        if self.instance.pk:
            manage_quests = HTML('<a class="green-button" role="button" '
                               'href="{}">Manage quests</a>'.format(
                manage_quests_href))
            self.helper.layout.append(
                Div(ButtonHolder(self.delete_button,
                    Div(manage_quests, self.save_button,
                        css_class='button-group-right'))
                )
            )
        else:
            self.helper.layout.append(ButtonHolder(self.save_button))


class QuestGradeForm(CrispyFormMixin, forms.Form):  
    
    OPTIONS = (('fc','For credit'),
               ('nfc','Not for credit'))
    
    section = forms.ModelChoiceField(Section.objects.all(),
                                     widget=forms.HiddenInput())
    quest = forms.ModelChoiceField(Quest.objects.all())
    active = forms.BooleanField(required=False,
                                label='Include only active users')
    for_credit = forms.MultipleChoiceField(required=True,
                                   label='For Credit',
                                   choices=OPTIONS)
    class Meta:
        fields = ('section', 'quest', 'active', 'for_credit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        export_button = Submit('submit', 'Export grade file',
                               css_class='btn-success pull-right')
        self.helper.layout = Layout(
            Fieldset('Get grade report for this section', 'quest', 'section', 'for_credit'),
            ButtonHolder(export_button)
        )


class SettingsForm(CrispyFormMixin, forms.Form):
    colour_scheme = forms.ChoiceField(choices=PCRSUser.code_style_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', 'colour_scheme'), self.save_button)


class UserForm(CrispyFormMixin, forms.Form):
    username = forms.CharField(required=False, help_text='Enter the username, or leave blank to clear')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        button = Submit('submit', 'View as user',
                         css_class='btn-success pull-right')
        self.helper.layout = Layout(
            Fieldset('', 'username'), button)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        if username:
            try:
                user = PCRSUser.objects.get(username=username)
                cleaned_data['user'] = user
            except PCRSUser.DoesNotExist:
                raise ValidationError({'username': 'Enter a valid username.'})
        else:
            cleaned_data['user'] = None
        return cleaned_data
