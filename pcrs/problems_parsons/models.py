import logging
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics
from multiselectfield import MultiSelectField



class Problem(AbstractProblem):
    name = models.CharField(max_length=50, default="")
    description = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)
    invariant = models.TextField(blank=True)
    unit_tests = models.TextField(blank=True)
    visible_unit = models.BooleanField(default=False)
    evaluation_choices = ((0, 'Evaluate using all methods'), (1, 'Evaluate using line comparison (simple)'), (2, 'Evaluate using unit tests method'))
    evaluation_type = MultiSelectField(choices=evaluation_choices, max_choices=1, max_length=1, default=1)
    


class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
