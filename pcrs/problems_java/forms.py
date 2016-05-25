from django import forms
from crispy_forms.layout import HTML

from pcrs.form_mixins import BaseRelatedObjectForm
from problems.forms import BaseProblemForm
from .models import Problem


class ProblemForm(forms.ModelForm, BaseProblemForm):
    # Overridden from BaseProblemForm
    clear_button = HTML('<a class="red-button" role="button" '
        'onclick="showClearSubmissionsDialog()"/clear">'
        'Clear submissions</a>')

    class Meta:
        model = Problem
        fields = ('name', 'description', 'starter_code', 'solution',
                  'test_suite', 'tags', 'visibility')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        BaseProblemForm.__init__(self)

