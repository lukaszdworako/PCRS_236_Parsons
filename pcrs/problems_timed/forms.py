from crispy_forms.layout import ButtonHolder, Submit, Layout, Fieldset, Div
from django import forms

from pcrs.form_mixins import BaseRelatedObjectForm, CrispyFormMixin
from problems.forms import BaseProblemForm, BaseSubmissionForm
from problems_timed.models import Problem, Term, Submission


class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        #widgets = {'tags': forms.HiddenInput()}
        fields = ('description', 'delay', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        
        self.save_and_add = Submit('submit', 'Save and add terms',
                                   css_class='btn-success pull-right',
                                   formaction='create_and_add_term')
        
        BaseProblemForm.__init__(self)
        self.buttons = (Div(CrispyFormMixin.delete_button,
                            self.clear_button,
                            css_class='btn-group'),
                        Div(self.save_button,
                            css_class='btn-group pull-right'))
        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))


class TermForm(BaseRelatedObjectForm):
    class Meta:
        model = Term
        widgets = {'problem': forms.HiddenInput()}
        fields = ('text', 'problem')

    def __init__(self, *args, **kwargs):
        BaseRelatedObjectForm.__init__(self, *args, formaction='terms',
                                       **kwargs)

class SubmissionForm(BaseSubmissionForm):
    submission = forms.CharField(widget=forms.Textarea())
    
    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset('', 'submission'),
            ButtonHolder(self.submit_button, css_class='pull-right'))