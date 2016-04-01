import re
from hashlib import sha1

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete

from problems.pcrs_languages import GenericLanguage
from pcrs.model_helpers import has_changed
from problems.models import (AbstractProgrammingProblem, AbstractSubmission,
                             AbstractTestCase, AbstractTestRun,
                             testcase_delete, problem_delete)
from .java_language import CompilationError


class Problem(AbstractProgrammingProblem):
    """
    A coding problem.

    A coding problem has all the properties of a problem, and
    a language and starter code
    """

    language = models.CharField(max_length=50,
                                choices=(('java', 'Java'),),
                                default='java')


class Submission(AbstractSubmission):
    """
    A coding problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def run_testcases(self, request, save=True):
        """
        Run all testcases for the submission and create testrun objects.
        Return the list of testrun results.
        """

        runner = GenericLanguage(self.problem.language)
        self.preprocess_tags()
        try:
            runner.lang.compile(self.user.username, self.mod_submission)    # necessary since language requires compilation
        except CompilationError as e:
            error = str(e).replace('\n', '<br />')
            return [{'passed_test': False, 'exception_type': 'error', 'exception': error, 'test_val': error}], None

        try:
            results = []
            for testcase in self.problem.testcase_set.all():
                run = testcase.run(runner)

                try:
                    passed = run['passed_test']
                except KeyError:    # Timeout, usually because of infinite loop
                    passed = False
                    #error = "Timeout occurred: do you have an infinite loop?"
                if save:
                    TestRun.objects.create(submission=self, testcase=testcase,
                                           test_passed=passed)

                run['test_desc'] = testcase.description
                run['expected_output'] = testcase.expected_output.strip().replace('\n', '<br />')
                run['debug'] = False
                if testcase.is_visible:
                    run['test_input'] = testcase.test_input
                    # run['debug'] = True     # Always False, until debugger is implemented
                else:
                    run['test_input'] = None
                results.append(run)
        except:
            runner.lang.clear()
            raise         # reraise

        runner.lang.clear()    # Removing compiled files
        return results, None

    # Adapted from models.py in the C framework
    def preprocess_tags(self):
        self.hidden_lines_list = []
        self.non_hidden_lines_list = []

        #if code from editor, just return code -- there were no tags
        if self.problem_id == 9999999:
            if len(self.submission) == 0:
                raise Exception("No code found!")
            self.mod_submission = self.submission
            return

        #Code not from editor, process tags
        student_code_key = sha1(str(self.problem_id).encode('utf-8')).hexdigest()
        student_code_key_list = [m.start() for m in re.finditer(student_code_key, self.submission)]
        student_code_key_len = len(student_code_key)
        student_code_key_list_len = len(student_code_key_list)

        # Could not find student code
        if student_code_key_list_len == 0:
            raise Exception("No student code found!")

        # Get student code from submission and add it to the official exercise (from the database)
        if student_code_key_list_len % 2 != 0:
            student_code_key_list = student_code_key_list[:-1]

        student_code_list = []
        while len(student_code_key_list) >= 2:
            student_code_list.append(
                self.submission[student_code_key_list[0] + student_code_key_len + 1: student_code_key_list[1]])
            del student_code_key_list[0], student_code_key_list[0]

        # Create variable mod_submission to handle the fusion of student code with starter_code from the database
        self.mod_submission = self.problem.starter_code
        last_tag_size = len('[/student_code]') + 2
        while len(student_code_list) > 0 and self.mod_submission.find('[student_code]') != -1:
            student_code = student_code_list.pop(0)
            self.mod_submission = self.mod_submission[: self.mod_submission.find('[student_code]')] + \
                                    student_code +\
                                    self.mod_submission[self.mod_submission.find('[/student_code]')+last_tag_size:]

        # Replace hashed key with text (Implementation start/end)
        x = 0
        while x < student_code_key_list_len:
            m = re.search(student_code_key, self.submission)
            self.submission = self.submission[: m.start()] + self.submission[m.end():]
            x += 1

        # Remove blocked tags from the source code
        self.mod_submission = self.mod_submission.replace("[blocked]\r\n", '').replace("[/blocked]\r\n", '')
        self.mod_submission = self.mod_submission.replace("[blocked]", '').replace("[/blocked]", '')

        # Store hidden code lines for previous use when showing compilation and warning errors
        inside_hidden_tag = False
        line_num = 1
        for line in self.mod_submission.split('\n'):
            if line.find("[hidden]") > -1:
                inside_hidden_tag = True
                continue
            elif line.find("[/hidden]") > -1:
                inside_hidden_tag = False
                continue
            if inside_hidden_tag:
                self.hidden_lines_list.append(line_num)
            else:
                self.non_hidden_lines_list.append(line_num)
            line_num += 1
        self.non_hidden_lines_list.pop()

        # Remove hidden tags from the source code
        self.mod_submission = self.mod_submission.replace("[hidden]\r\n", '').replace("[/hidden]\r\n", '')
        self.mod_submission = self.mod_submission.replace("[hidden]", '').replace("[/hidden]", '')


class TestCase(AbstractTestCase):
    """
    A coding problem testcase.

    A testcase has an input and expected output and an optional description.
    The test input and expected output may or may not be visible to students.
    This is controlled by is_visible flag.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
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

    def run(self, runner):
        return runner.lang.run_test(self.test_input, self.expected_output)


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


# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)
post_delete.connect(problem_delete, sender=Problem)
