import logging
import datetime

from django.db import models
from django.utils.timezone import localtime, utc

from problems.models import AbstractProblem, AbstractSubmission
from problems_python.pcrs_languages import PythonSpecifics


class Problem(AbstractProblem):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    solution = models.TextField()

    def __str__(self):
        return self.name
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
                  "resource.setrlimit(resource.RLIMIT_CPU, (3, 3))"] +\
                 code_lines +\
                 test_params +\
                 ["print(score)",
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
            else:
                result = int(stdout_output[-1])
        except TimeoutExpired as ex:
            result = 0
        except Exception as ex:     # Probably a value error.
            logger = logging.getLogger('activity.logging')
            logger.error("{0} | Exception while evaluating short answer ({1}, submitted: {2})\nException:\n{3}".format(
                         localtime(datetime.datetime.utcnow().replace(tzinfo=utc)), self.problem.pk, self.submission, ex))
            result = 0

        self.score = result
        self.save()
        self.set_best_submission()

