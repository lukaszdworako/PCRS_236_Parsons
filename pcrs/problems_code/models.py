from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete

from .pcrs_languages import GenericLanguage
from pcrs.model_helpers import has_changed
from pcrs.settings import LANGUAGE_CHOICES
from problems.models import (AbstractNamedProblem, AbstractSubmission,
                             AbstractTestCase, AbstractTestRun,
                             testcase_delete)


class Problem(AbstractNamedProblem):
    """
    A coding problem.

    A coding problem has all the properties of a problem, and
    a language and starter code
    """

    type_name = 'coding'

    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES,
                                default='python')
    starter_code = models.TextField(blank=True)


class Submission(AbstractSubmission):
    """
    A coding problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def run_testcases(self):
        """
        Run all testcases for the submission and create testrun objects.
        """
        for testcase in self.problem.testcase_set.all():
            run = testcase.run(self.submission)
            TestRun.objects.create(submission=self, testcase=testcase,
                                   test_passed=run['passed_test'])

    def set_score(self):
        """
        Set the score of this submission to the number of testcases that
        the submission passed.
        """
        self.score = self.testrun_set.filter(test_passed=True).count()
        self.save(update_fields=['score'])

    @classmethod
    def get_problem_class(cls):
        return Problem


class TestCase(AbstractTestCase):
    """
    A coding problem testcase.

    A testcase has an input and expected output and an optional description.
    The test input and expected output may or may not be visible to students.
    This is controlled by is_visible flag.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    test_input = models.TextField()
    expected_output = models.TextField()
    is_visible = models.BooleanField(null=False, default=False,
        verbose_name='Test input and output visible to students')

    @classmethod
    def get_problem_class(cls):
        return Problem

    def __str__(self):
        testcase = '{input} -> {output}'.format(input=self.test_input,
                                                output=self.expected_output)
        if self.description:
            return self.description + ' : ' + testcase
        else:
            return testcase

    def clean(self):
        super().clean()
        if not self.pk and self.problem.submission_set.all():
            raise ValidationError(
                'Submissions must be cleared before adding a testcase.')

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        if self.pk:
            if has_changed(self, 'problem_id'):
                raise ValidationError({
                    'problem': ['Reassigning a problem is not allowed.']
                })
            if self.problem.submission_set.all():
                clear = 'Submissions must be cleared before editing a testcase.'
                if has_changed(self, 'test_input'):
                    raise ValidationError({'test_input': [clear]})
                if has_changed(self, 'expected_output'):
                    raise ValidationError({'expected_output': [clear]})

    def run(self, code):
        runner = GenericLanguage(self.problem.language)
        return runner.run_test(code, self.test_input, self.expected_output)


class TestRun(AbstractTestRun):
    """
    A coding problem testrun, created for each testcase on each submission.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)


# Signal handlers

# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)