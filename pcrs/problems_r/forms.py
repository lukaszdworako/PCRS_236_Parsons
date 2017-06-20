from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML
from django import forms
from pcrs.form_mixins import CrispyFormMixin
from problems_r.models import Script, Problem, FileSubmissionManager
from problems.forms import BaseProblemForm, ProgrammingSubmissionForm
from problems.helper import remove_tag

class ScriptForm(CrispyFormMixin, forms.ModelForm):
	"""
	Form for R Script details
	"""
	save_and_run = Submit("submit", "Save and run",
						  css_class="green-button-right",
						  formaction="create_and_run")
	class Meta:
		model = Script
		fields = ("name", "code")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper.layout = Layout(
			Fieldset('', *self.Meta.fields),
			ButtonHolder(self.save_and_run, css_class="pull-right")
			)

class ProblemForm(forms.ModelForm, BaseProblemForm):
    class Meta:
        model = Problem
        fields = ('name', 'script', 'description', 'starter_code', 'solution',
				  'tags', 'visibility', 'output_visibility', 'allow_data_set')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)

class FileSubmissionForm(ProgrammingSubmissionForm):

    def __init__(self, *args, **kwargs):
        problem = kwargs.get('problem', None)
        shouldLoadSolution = kwargs.pop('loadSolution', False)
        isInstructor = kwargs.pop('isInstructor', False)
        user = kwargs.pop('user', None)

        # Only instuctors should be able to auto-load the solution
        code = problem.solution if shouldLoadSolution else problem.starter_code
        code = remove_tag('[hidden]', '[/hidden]', code)

        super().__init__(*args, **kwargs)
        self.fields['submission'].initial = code
        buttonDiv = self._generateButtonDiv(problem, isInstructor)

        if problem.allow_data_set:
            try:
                fsm = FileSubmissionManager.objects.get(user=user, problem=problem)
                if fsm:
                    # Retrieve file info
                    name = fsm.file_upload.name
                    substring = fsm.file_upload.get_str_data()[:150]

                    layout_fields = (HTML('<br><div id="file_existance" class="alert well"> \
						<p><input type="button" id="delete_file" class="btn btn-danger pull-right" \
						value="Delete Data Set"></input>File Name: {} <br>First 150 Characters: \
						<br>{}</p></div>'.format(name, substring.replace('\n', '<br>'))),
						Fieldset('', 'submission'), buttonDiv)
            except:
                layout_fields = (Fieldset('', 'submission'), buttonDiv)
        else:
            layout_fields = (Fieldset('', 'submission'), buttonDiv)
        self.helper.layout = Layout(*layout_fields)
