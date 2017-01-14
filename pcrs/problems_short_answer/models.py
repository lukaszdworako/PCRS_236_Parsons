import logging
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localtime, utc

from pcrs.model_helpers import has_changed
from problems.models import AbstractProblem, AbstractSubmission
from problems_python.python_language import PythonSpecifics


class Problem(AbstractProblem):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    solution = models.TextField(help_text='The solution should be valid Python code. It may import libraries, such as <i>re</i>. The submission to be graded will be in a variable named <i>submission</i>, and the score to be assigned should be placed in a variable <i>score</i>. An optional error message to be displayed to the student can be placed in variable <i>message</i>.')

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        clear = 'Submissions must be cleared before changing the solution. (Please copy the new solution to your clipboard, as it will be lost when you clear submissions.)'
        if self.submission_set.all():
            if self.pk and has_changed(self, 'solution'):
                raise ValidationError({'solution': [clear]})

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

        python_runner = PythonSpecifics()
        code_lines = ["submission = {0}".format(repr(self.submission))]

        test_params = self.problem.solution.replace('\n', '').split('\r')
        script = ["import sys",
                  "import os",
                  "import resource",
                  "resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))",
                  "resource.setrlimit(resource.RLIMIT_CPU, (3, 3))",
                  "message = None"] +\
                 code_lines +\
                 test_params +\
                 ["print(score)",
                  "print(message)",
                  "exit()"]

        try:
            p = python_runner.run_subprocess(script)
            p.wait(timeout=2)

            stderr_output = p.stderr.readlines()
            stdout_output = p.stdout.readlines()
            if stderr_output:
                logger = logging.getLogger('activity.logging')
                logger.info("{0} | Error within short answer evaluation ({1}, submitted: {2})\nException:\n{3}".format(
                             localtime(datetime.datetime.utcnow().replace(tzinfo=utc)), self.problem.pk, repr(self.submission), stderr_output))
                result = 0
                message = ""
            else:
                result = int(stdout_output[-2])
                message = stdout_output[-1].decode("utf-8") 
        except TimeoutExpired as ex:
            result = 0
            message = ""
        except Exception as ex:     # Probably a value error.
            logger = logging.getLogger('activity.logging')
            logger.error("{0} | Exception while evaluating short answer ({1}, submitted: {2})\nException:\n{3}".format(
                         localtime(datetime.datetime.utcnow().replace(tzinfo=utc)), self.problem.pk, self.submission, ex))
            result = 0
            message = ""

        self.score = result
        self.message = message
        self.save()
        self.set_best_submission()

