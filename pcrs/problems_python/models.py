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
from pcrs.models import AbstractSelfAwareModel
from pcrs.settings import PROJECT_ROOT

import python_ta
import io, re, os, tempfile
from contextlib import redirect_stdout




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
    #Record PyTA output
    pyta = models.TextField(blank=True, null=True)

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

        tags = [tag.name for tag in self.problem.tags.all()]

        for testcase in self.problem.testcase_set.all():
            if "PyTA" in tags and testcase.description == "PyTA":
                continue

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

    def run_pyta(self):
        """
        Run PyTA with the submitted code as input.
        Return the output of PyTA.
        """
        submittedFiles = self.preprocessTags()
        # We don't support multiple files yet
        submittedCode = submittedFiles[0]['code']

        pytaResult = {}
        pytaResult['test_desc'] = 'PyTA'
        #Identify the result as PyTA output
        pytaResult['PyTA'] = True
        
        try:
            tempfileDir= os.path.join(PROJECT_ROOT,'languages','python','execution','temporary')
            submittedCodeFile = tempfile.NamedTemporaryFile(delete=False, dir=tempfileDir, suffix='.py')
            submittedCodeFile.write(submittedCode.encode())
            submittedCodeFile.close()
            with io.StringIO() as buf, redirect_stdout(buf):
                python_ta.check_all('.'.join(('languages','python','execution','temporary',submittedCodeFile.name.split(os.sep)[-1])))
                #Remove ANSI characters
                pytaOutput = re.sub(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]','',buf.getvalue()).replace('\n','<br />').replace('[','&emsp;[')
        except Exception as e:
            pytaOutput = str(e)
        
        try:
            os.remove(submittedCodeFile.name)
        except (OSError, UnboundLocalError):
            pass

        pytaResult['test_val'] = pytaOutput
        
        self.pyta = pytaOutput
        self.save()

        return pytaResult

    def run_pyta_testcase(self, pyta_output):
        """
        Run testcase for PyTA tagged problems to check for
        presence of a certain error code.
        """
        testcases = self.problem.testcase_set.all()
        pyta_testcase = testcases[len(testcases)-1]
        err_code = pyta_testcase.test_input.strip()

        ret = {}
        ret['test_desc'] = pyta_testcase.description
        ret['expected_output'] = ['string',99999,"No " + err_code + " Found"]
        
        if err_code in pyta_output['test_val']:
            ret['passed_test'] = False
            ret['test_val'] = ['string',99999,err_code + " Found"]
        else:
            ret['passed_test'] = True
            ret['test_val'] = ['string',99999,"No " + err_code + " Found"]

        TestRun.objects.create(submission=self, testcase=pyta_testcase,
                                       test_passed=ret['passed_test'])
        self.set_score()
        
        ret['debug'] = False
        if pyta_testcase.is_visible:
            ret['test_input'] = pyta_testcase.test_input.replace('\n','<br />')
            ret['debug'] = True
        else:
            ret['test_input'] = None
        
        return ret


class PyTAClickEvent(AbstractSelfAwareModel, SubmissionPreprocessorMixin):
    """
    A PyTA error message click event.

    A PyTAClickEvent has a submission_id and click_count. It is created when 
    the PyTA error message dropdown is expanded and click_count is updated 
    after every subsequent click.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    click_count = models.PositiveIntegerField(default=1)


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
