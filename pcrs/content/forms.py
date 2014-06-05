from crispy_forms.layout import Fieldset, Layout, ButtonHolder, Div, HTML
from django import forms

from content.models import Challenge, Video
from content.tags import Tag
from pcrs.form_mixins import CrispyFormMixin


class TagForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
            ButtonHolder(self.delete_button if self.instance.pk else None,
                         self.save_button)
        )


class VideoForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Video
        fields = ('name', 'description', 'link', 'tags')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
            ButtonHolder(self.delete_button if self.instance.pk else None,
                         self.save_button)
        )


class ChallengeForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ('visibility', 'name', 'description', 'is_graded', 'quest')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('', *self.Meta.fields),
        )
        if self.instance.pk:
            add_objects = HTML('<a class="btn btn-success" role="button" '
                               'href="{{ object.get_absolute_url }}/objects">'
                               'Manage content</a>')
            self.helper.layout.append(
                Div(ButtonHolder(self.delete_button,
                    Div(add_objects, self.save_button,
                        css_class='btn-group pull-right'))
                )
            )
        else:
            self.helper.layout.append(ButtonHolder(self.save_button))

            # class ProblemSetForm(CrispyFormMixin, forms.ModelForm):
            #     """
            #     A form for creating a ProblemSet.
            #     """
            #
            #     class Meta:
            #         # model = ProblemSet
            #         fields = ('visibility', 'name', 'description')
            #
            #     def __init__(self, *args, **kwargs):
            #         super().__init__(*args, **kwargs)
            #
            #         problem_ctypes = ContentType.objects.filter(Q(model='problem'))
            #         for problem_ctype in problem_ctypes:
            #             field = forms.ModelMultipleChoiceField(
            #                 queryset=problem_ctype.model_class().objects.all(),
            #                 widget=forms.CheckboxSelectMultiple(),
            #                 required=False, label='')
            #             self.fields[problem_ctype.app_label] = field
            #
            #         self.helper.layout = Layout(
            #             Fieldset('', *self.Meta.fields),
            #             TabHolder(
            #                 *[Tab(
            #                     ctype.model_class().get_problem_type_name().replace('_',
            #                         ' '),
            #                     ctype.app_label)
            #                   for ctype in problem_ctypes]
            #             ),
            #             ButtonHolder(self.save_button)
            #         )