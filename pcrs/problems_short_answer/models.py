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
    min_chars = models.PositiveIntegerField(default=50)
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

        if len(self.submission) < self.problem.min_chars:
            self.message = 'Your answer is less than minimum character requirement of ' \
                            + str(self.problem.min_chars) + '.'
        else:
            messages = []

            # Check each key in submission
            for key in self.problem.keys:
                # Build dict from array of keys for fast lookup
                key_dict = {}
                for ele in key.split(","):
                    key_dict[ele.strip()] = 1

                for word in key_dict:
                    if word in submission:
                        result += 1
                        break
                else:
                    messages.append(self.problem.keys[key])

            separator = '\n'
            message = separator.join(messages)
            self.message = message

        self.score = result
        self.save()
        self.set_best_submission()
