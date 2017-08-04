from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete

from problems.pcrs_languages import GenericLanguage
from pcrs.model_helpers import has_changed
from problems.models import (AbstractProgrammingProblem, AbstractSubmission,
    SubmissionPreprocessorMixin, AbstractTestCaseWithDescription,
    AbstractTestRun,
    testcase_delete, problem_delete)


class Problem(AbstractProgrammingProblem):
    """
    A coding problem.

    A coding problem has all the properties of a problem, and
    a language and starter code
    """

    language = models.CharField(max_length=50,
                                choices=(('python', 'Python 3.4'),),
                                default='python')


class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
    """
    A coding problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def run_testcases(self, request, save=True):
        """
        Run all testcases for the submission and create testrun objects.
        Return the list of testrun results.
        """
        results = []
        error = None

        submittedFiles = self.preprocessTags()
        # We don't support multiple files yet
        submittedCode = submittedFiles[0]['code']

        for testcase in self.problem.testcase_set.all():
            run = testcase.run(submittedCode)

            try:
                passed = run['passed_test']
            except KeyError:
                passed = False
                if 'exception' in run:
                    error = run['exception']
                else:
                    error = "The testcase could not be run"
            if save:
                TestRun.objects.create(submission=self, testcase=testcase,
                                       test_passed=passed)

            run['test_desc'] = testcase.description
            run['debug'] = False
            if testcase.is_visible:
                run['test_input'] = testcase.test_input.replace('\n','<br />')
                run['debug'] = True
            else:
                run['test_input'] = None
            results.append(run)

        return results, error


class TestCase(AbstractTestCaseWithDescription):
    """
    A coding problem testcase.

    A testcase has an input and expected output and an optional description.
    The test input and expected output may or may not be visible to students.
    This is controlled by is_visible flag.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
    pre_code = models.TextField(default="", blank=True)
    test_input = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        testcase = '{input} -> {output}'.format(input=self.test_input,
                                                output=self.expected_output)
        if self.description:
            return self.description + ' : ' + testcase
        else:
            return testcase

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
        return runner.run_test(code, self.test_input, self.expected_output, self.pre_code)


class TestRun(AbstractTestRun):
    """
    A coding problem testrun, created for each testcase on each submission.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)

    def get_history(self):
        return {
            'visible': self.testcase.is_visible,
            'input': self.testcase.test_input,
            'output': self.testcase.expected_output,
            'passed': self.test_passed,
            'description': self.testcase.description
        }


# Signal handlers

# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)

post_delete.connect(problem_delete, sender=Problem)
