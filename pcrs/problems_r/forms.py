from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div
from django import forms
from pcrs.form_mixins import CrispyFormMixin
from problems_r.models import Script, Problem
from problems.forms import BaseProblemForm

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
        fields = ('name', 'script', 'description', 'starter_code',
                  'solution', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)