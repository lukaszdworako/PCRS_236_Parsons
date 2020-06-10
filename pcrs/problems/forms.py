from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Submit, HTML, ButtonHolder, Div, Layout, \
    Fieldset, Button, Row
from django import forms
from django.utils.timezone import now

from pcrs.form_mixins import CrispyFormMixin
from users.models import Section

from problems.widgets.select_multiple_field import SelectMultipleField

from problems.helper import remove_tag

class BaseProblemForm(CrispyFormMixin):

    def __init__(self, *args, **kwargs):
        self.buttons = self._createButtons()

        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Fieldset('', *self.Meta.fields),
                                    ButtonHolder(*self.buttons))

        # Not all problems have the tags field.
        if 'tags' in self.fields:
            self.fields['tags'].help_text = None
            self.fields['tags'].widget = SelectMultipleField(
                choices=self.fields['tags'].choices
            )

    def _createButtons(self):
        '''Generate the buttons for the problem form.

        Returns:
            A tuple of button elements
        '''
        absUrl = self.instance.get_absolute_url()
        cloneUrl = '{}/clone'.format(absUrl)
        clearUrl = '{}/clear'.format(absUrl)

        self.clear_button = HTML('<a class="red-button" role="button" '
            'onclick="showClearSubmissionsDialog(\'' + clearUrl + '\')">'
            'Clear submissions</a>')
        clone_button = Submit('clone', 'Clone',
            css_class='green-button', formaction=cloneUrl)
        save_button = Submit('submit', 'Save',
            css_class='green-button-right')
        attempt_button = Submit('attempt', 'Save & Attempt',
            css_class='green-button-right')
        save_and_add_button = Submit('submit', 'Save and add testcases',
            css_class='green-button-right',
            formaction='create_and_add_testcase')

        # Existing problem
        if self.instance.pk:
            return (
                Div(CrispyFormMixin.delete_button, self.clear_button,
                    css_class='button-group'),
                Div(clone_button, save_button, attempt_button,
                    css_class='button-group-right'),
            )
        # Cloning a problem
        elif self.instance:
            return save_button,
        # Creating a new problem
        else:
            return self.save_and_add_button,


class EditorForm(CrispyFormMixin, forms.Form):
    code_box = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        problem = kwargs.pop('problem', None)
        simpleui = kwargs.pop('simpleui', False)
        initial_code = kwargs.pop('initial_code', '')
        super().__init__(*args, **kwargs)

        self.trace_button = Submit('Trace', value='Trace', css_class='debugBtn pull-right')
        self.fields['code_box'].initial = initial_code
        layout_fields = (Fieldset('', 'code_box'), Div(self.trace_button, css_class="floatdiv"))
        self.helper.layout = Layout(*layout_fields)


class BaseSubmissionForm(CrispyFormMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        problem = kwargs.pop('problem', None)
        simpleui = kwargs.pop('simpleui', False)
        super().__init__(*args, **kwargs)
        self.helper.form_show_labels = False
        self.submit_button = Submit('Submit', value='Submit',
                                    css_class='green-button pull-right')
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

        shouldLoadSolution = kwargs.pop('loadSolution', False)
        isInstructor = kwargs.pop('isInstructor', False)

        # Only instuctors should be able to auto-load the solution
        code = problem.solution if shouldLoadSolution else problem.starter_code
        code = remove_tag('[hidden]', '[/hidden]', code)

        super().__init__(*args, **kwargs)
        self.fields['submission'].initial = code

        buttonDiv = self._generateButtonDiv(problem, isInstructor)
        layout_fields = (Fieldset('', 'submission'), buttonDiv)
        self.helper.layout = Layout(*layout_fields)

    def _generateButtonDiv(self, problem, isInstructor):
        if not isInstructor:
            return Div(self.history_button, self.submit_button)

        # If it is an instructor, add a link to auto-load the solution
        url = problem.get_absolute_url() + '/submit?loadSolution'
        loadSolutionButton = StrictButton('Load Solution',
            name='load_solution',
            onclick='window.location.href = "' + url + '"',
            css_class='btn reg-button')
        return Div(self.history_button,
            loadSolutionButton, self.submit_button)


class MonitoringForm(CrispyFormMixin, forms.Form):
    time = forms.DateTimeField(initial=now(), label='Start time', help_text='Submissions before this time will not be shown.')
    section = forms.ModelChoiceField(queryset=Section.objects.all())
    final = forms.BooleanField(required=False, label='Static result', help_text='Leave unchecked if you want results updated live.')
    firstSubmissionsOnly = forms.BooleanField(required=False, label='Count first submissions only',\
                                              help_text='Check to see only results of all first submissions per student after start time')

    def __init__(self, *args, **kwargs):
        go = Button('Go', value='Go', css_class='green-button')
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Fieldset('', 'time', 'section', 'final','firstSubmissionsOnly',\
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
