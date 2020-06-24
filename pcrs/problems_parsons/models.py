import logging
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc
from django.contrib.postgres.fields import HStoreField

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics




class Problem(AbstractProblem):
    name = models.CharField(max_length=50, default="")
    description = models.TextField(blank=True)
    starter_code = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    invariant = models.TextField(blank=True)
    unit_tests = models.TextField(blank=True)
    run_unit = models.BooleanField(default=False)
    visible_unit = models.BooleanField(default=False)
    static = models.TextField(blank=True)
    groups = models.TextField(blank=True)
    inter = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    


class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
