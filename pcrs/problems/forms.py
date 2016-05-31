from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit, HTML, ButtonHolder, Div, Layout, \
    Fieldset, Button, Row
from django import forms
from django.utils.timezone import now

from pcrs.form_mixins import CrispyFormMixin
from users.models import Section

from problems.widgets.select_multiple_field import SelectMultipleField


class BaseProblemForm(CrispyFormMixin):
    clear_button = HTML('<a class="red-button" role="button" '
        'onclick="showClearSubmissionsDialog()"/clear">'
        'Clear submissions</a>')
    save_button = Submit('submit', 'Save', css_class='green-button-right')
    attempt_button = Submit('attempt', 'Save & Attempt', css_class='green-button-right')

    save_and_add = Submit('submit', 'Save and add testcases',
                           css_class='green-button-right',
                           formaction='create_and_add_testcase')

    buttons = None

    def __init__(self, *args, **kwargs):
        if self.instance.pk:
            clone = Submit('clone', 'Clone', css_class='green-button',
                           formaction='{}/clone'.format(
                               self.instance.get_absolute_url()))

            self.buttons = (Div(CrispyFormMixin.delete_button,
                                self.clear_button,
                                css_class='button-group'),
                            Div(clone, self.save_button, self.attempt_button,
                                css_class='button-group-right'),
                            )

        elif self.instance:
            # cloning
            self.buttons = self.save_button,
        else:
            # creating a new one
            self.buttons = self.save_and_add,

        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))

        self.fields['tags'].help_text = None
        self.fields['tags'].widget = SelectMultipleField(
            choices=self.fields['tags'].choices
        )



class EditorForm(CrispyFormMixin, forms.Form):
    code_box = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        problem = kwargs.pop('problem', None)
        simpleui = kwargs.pop('simpleui', False)
        super().__init__(*args, **kwargs)

        self.trace_button = Submit('Trace', value='Trace', css_class='debugBtn pull-right')
        self.fields['code_box'].initial = ''
        layout_fields = (Fieldset('', 'code_box'), Div(self.trace_button, css_class="floatdiv"))
        self.helper.layout = Layout(*layout_fields)


class BaseSubmissionForm(CrispyFormMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        problem = kwargs.pop('problem', None)
        simpleui = kwargs.pop('simpleui', False)
        super().__init__(*args, **kwargs)
        self.helper.form_show_labels = False
        self.submit_button = Submit('Submit', value='Submit',
                                    css_class='green-button')
        if not (problem.name == 'blank' or problem.challenge == None or simpleui):
            history_css = 'reg-button'
        else:
            history_css = 'reg-button hidden'
        self.history_button = StrictButton('History', name='history',
                                           data_toggle="modal",
                                           data_target="#history_window_"+
                                           problem.get_problem_type_name()+
                                                   "-{}".format(problem.pk),
                                           css_class=history_css)


class ProgrammingSubmissionForm(BaseSubmissionForm):
    submission = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)

        # Remove hidden code from the student
        problem.starter_code = remove_tag('[hidden]', '[/hidden]', problem.starter_code)

        super().__init__(*args, **kwargs)
        self.fields['submission'].initial = problem.starter_code
        layout_fields = (Fieldset('', 'submission'), Div(self.history_button, self.submit_button))
        self.helper.layout = Layout(*layout_fields)


def remove_tag(tag_open, tag_close, source_code):
    source_code = source_code.split('\n')
    source_code_output = []
    tag_count = 0
    for line in source_code:
        if line.find(tag_open) > -1:
            tag_count += 1
            continue
        elif line.find(tag_close) > -1:
            tag_count -= 1
            continue
        if tag_count == 0:
            source_code_output.append(line)
    return "\n".join(source_code_output)


class MonitoringForm(CrispyFormMixin, forms.Form):
    time = forms.DateTimeField(initial=now(), label='Start time', help_text='Submissions before this time will not be shown.')
    section = forms.ModelChoiceField(queryset=Section.objects.all())
    final = forms.BooleanField(required=False, label='Static result', help_text='Leave unchecked if you want results updated live.')

    def __init__(self, *args, **kwargs):
        go = Button('Go', value='Go', css_class='green-button')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Fieldset('', 'time', 'section', 'final',
                                    ButtonHolder(go)))


class BrowseSubmissionsForm(CrispyFormMixin, forms.Form):
    starttime = forms.DateTimeField(label='Submissions after', required=False)
    stoptime = forms.DateTimeField(label='Submissions before', initial=now(),
                                   required=False)
    section = forms.ModelChoiceField(queryset=Section.get_lecture_sections(),
                                     required=True)

    def __init__(self, *args, **kwargs):
        self.submit_button = Submit('Browse', value='Browse',
                                    css_class='green-button')
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
