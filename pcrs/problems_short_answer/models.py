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
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    max_chars = models.PositiveIntegerField(default=200)
    keys = HStoreField(default=None)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        clear = 'Submissions must be cleared before changing the solution. (Please copy the new solution to your clipboard, as it will be lost when you clear submissions.)'
        if self.submission_set.all():
            if self.pk and has_changed(self, 'keys'):
                raise ValidationError({'keys': [clear]})

    def __str__(self):
        return self.name

    def prepareJSON(self):
        """
        Returns serializatin of short answer problem in JSON format.
        """
        content = [self]
        return content

Problem._meta.get_field('max_score').default = 1
Problem._meta.get_field('max_score').blank = False


class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def set_score(self, submission):
        self.submission = submission
        result = 0
        message = ""

        answer_dict = {}
        answer_keys = []
        answer_values = []
        checked_indices = []
        index = 0

        for key in self.problem.keys:
            key_array = []
            for ele in key.split(","):
                key_array.append(ele.lower())
                answer_dict[ele.strip()] = index
            answer_keys.append(key_array)
            answer_values.append(self.problem.keys[key])
            checked_indices.append(False)
            index += 1

        if self.submission.strip() == "":
            self.score = 0

        words = self.submission.split(" ")
        for word in words:
            if word in answer_dict and checked_indices[answer_dict[word]] != True:
                result += 1
                checked_indices[answer_dict[word]] = True

        for i in range(index):
            if checked_indices[i] == False:
                message += answer_values[i] + "\n"

        self.score = result
        self.message = message
        self.save()
        self.set_best_submission()
