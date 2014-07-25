from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit, HTML, ButtonHolder, Div, Layout, \
    Fieldset, Button
from django import forms
from django.utils.timezone import now

from pcrs.form_mixins import CrispyFormMixin
from users.models import Section


class BaseProblemForm(CrispyFormMixin):
    clear_button = HTML('<a class="btn btn-danger" role="button" '
                        'href="{{ object.get_absolute_url }}/clear">'
                        'Clear submissions</a>')
    save_button = Submit('submit', 'Save', css_class='btn-success pull-right')

    save_and_add = Submit('submit', 'Save and add testcases',
                           css_class='btn-success pull-right',
                           formaction='create_and_add_testcase')

    buttons = None

    def __init__(self, *args, **kwargs):
        if self.instance.pk:
            clone = Submit('clone', 'Clone', css_class='btn-success',
                           formaction='{}/clone'.format(
                               self.instance.get_absolute_url()))
            self.buttons = (Div(CrispyFormMixin.delete_button,
                                self.clear_button,
                                css_class='btn-group'),
                            Div(clone, self.save_button,
                                css_class='btn-group pull-right'))
        elif self.instance:
            # cloning
            self.buttons = self.save_and_add,
        else:
            # creating a new one
            self.buttons = self.save_and_add,
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))


class BaseSubmissionForm(CrispyFormMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        problem = kwargs.pop('problem', None)
        super().__init__(*args, **kwargs)
        self.helper.form_show_labels = False
        self.submit_button = Submit('Submit', value='Submit',
                                    css_class='btn-success')
        self.history_button = StrictButton('History', name='history',
                                           data_toggle="modal",
                                           data_target="#history_window_"+
                                            problem.get_problem_type_name()+
                                                       "-{}".format(problem.pk),
                                           css_class='btn-default')



class ProgrammingSubmissionForm(BaseSubmissionForm):
    submission = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        super().__init__(*args, **kwargs)
        self.fields['submission'].initial = problem.starter_code
        self.helper.layout = Layout(
            Fieldset('', 'submission'),
            self.history_button,
            ButtonHolder(self.submit_button, css_class='pull-right')
        )


class MonitoringForm(CrispyFormMixin, forms.Form):
    time = forms.DateTimeField(initial=now())
    section = forms.ModelChoiceField(queryset=Section.objects.all())
    final = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        go = Button('Go', value='Go', css_class='btn-success')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Fieldset('', 'time', 'section', 'final',
                                    ButtonHolder(go)))


class BrowseSubmissionsForm(CrispyFormMixin, forms.Form):
    starttime = forms.DateTimeField(label='Submissions after')
    stoptime = forms.DateTimeField(label='Submissions before', initial=now())
    section = forms.ModelChoiceField(queryset=Section.objects.all())

    def __init__(self, *args, **kwargs):
        self.submit_button = Submit('Browse', value='Browse',
                                    css_class='btn-success')
        problem = kwargs.pop('problem')
        super().__init__(*args, **kwargs)

        for testcase in problem.testcase_set.all():
            self.fields['testcase-'+str(testcase.pk)] = \
                forms.ChoiceField(
                    label=testcase.display(), widget=forms.RadioSelect(),
                    choices=[('pass', 'pass'), ('fail', 'fail'), ('any', 'any')],
                    initial='any')

        self.helper.layout = Layout(Fieldset('', *self.fields.keys()),
                                    ButtonHolder(self.submit_button))
