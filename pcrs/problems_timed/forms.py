from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div, Button
from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm, CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_timed.models import Problem, Page, Submission


class ProblemForm(forms.ModelForm, BaseProblemForm):
    
    class Meta:
        model = Problem
        fields = ('name', 'problem_description', 'submission_description', 'delay', 'attempts', 'author', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        self.save_and_add = Submit('submit', 'Save and Add Pages',
                               css_class='btn-success pull-right',
                               formaction='create_redirect')
        
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)
        
        if self.instance.pk:
            self.buttons = (Div(CrispyFormMixin.delete_button,
                                self.clear_button,
                                css_class='btn-group'),
                            Div(self.save_button,
                                css_class='btn-group pull-right'))
        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))

class PageForm(BaseRelatedObjectForm):
    class Meta:
        model = Page
        widgets = {'problem': forms.HiddenInput, 'term_list': forms.TextInput}
        fields = ('text', 'term_list', 'problem')

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='pages',
                                       **kwargs)

class SubmissionForm(BaseSubmissionForm):
    submission = forms.CharField(widget=forms.Textarea())
    
    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', 'submission'),
            ButtonHolder(self.submit_button, css_class='pull-right'))
