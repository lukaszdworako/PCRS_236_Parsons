import re
import html
from hashlib import sha1

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.db.models.signals import m2m_changed

from problems.pcrs_languages import GenericLanguage
from pcrs.model_helpers import has_changed
from problems.models import (AbstractProgrammingProblem, AbstractSubmission,
                             AbstractTestCase, AbstractTestRun,
                             testcase_delete, problem_delete)
from .java_language import CompilationError
from pcrs.models import AbstractSelfAwareModel

test_suite_template = """import org.junit.Test;
import static org.junit.Assert.*;

public class Tests {
    // <public test case description goes here>
    @Test
    public void exampleTestCase() {
        // Hides the assertion if there is no description.
        assertEquals(4, 2 + 2);
        // If you provide a description, the assert won't be hidden.
        assertEquals("Arithmetic is broken! ", 5, 3 + 2);
    }
}
"""

class Problem(AbstractProgrammingProblem):
    """
    A coding problem.

    A coding problem has all the properties of a problem, and
    a language and starter code
    """
    test_suite = models.TextField(blank=True, default=test_suite_template)
    language = models.CharField(max_length=50,
                                choices=(('java', 'Java'),),
                                default='java')

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)

        if self.pk:
            if len(self.submission_set.all()) > 0 and has_changed(self, 'test_suite'):
                raise ValidationError({'test_suite': [
                    'Submissions must be cleared before editing a testcase.',
                ]})

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # We need to check this here because it resets after saving.
        testsHaveChanged = has_changed(self, 'test_suite')
        super().save(force_insert, force_update, using, update_fields)
        if testsHaveChanged:
            self._repopulateTestCaseTable()
            super().save(force_insert, force_update, using, update_fields)

    def _repopulateTestCaseTable(self):
        # Generate test case objects automatically from the test suite
        self._deleteOldTestCases()
        testCaseInfo = self._generateTestCaseInfo(self.test_suite)
        for test in testCaseInfo:
            self.testcase_set.create(
                test_name=test['name'],
                description=test['description'])

        self.max_score = len(testCaseInfo)

    def _generateTestCaseInfo(self, test_code):
        # CodeMirror uses CRLFs for some reason :|
        test_code = re.sub('\r', '', test_code)
        reg = (
            '(\/\/[^\n]*|\/\*+.*?\*+\/)?[\t ]*\n' # Capture comments
            '[\t ]*@Test(?:\(.*\))?\s*' # Only methods annotated with @Test
            'public\s*void\s*([\w_]+)' # Capture method name
        )
        return [{
            'name': m[1],
            'description': self._stripComment(m[0])
        } for m in re.findall(reg, test_code, re.DOTALL)]

    def _deleteOldTestCases(self):
        for testcase in self.testcase_set.all():
            testcase.delete()

    def _stripComment(self, comment):
        comment = re.sub('[\t ]*\/\/[\t ]*', '', comment)
        comment = re.sub('\/\*+', '', comment)
        comment = re.sub('\*+\/', '', comment)
        comment = re.sub('[\t ]*\*[\t ]*', '', comment)
        return comment.strip()


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
            # necessary since language requires compilation
            runner.lang.compile(self.user.username, self.mod_submission, self.problem.test_suite)
            test_results = runner.lang.run_test_suite()
        except CompilationError as e:
            return self._createCompileErrorResponse(e)

        if 'exception' in test_results:
            return [{ 'passed_test': False,
                      'exception_type': 'error',
                      'exception': test_results['exception'],
                      'test_val': test_results['exception']}], None

        results = []
        for testcase in self.problem.testcase_set.all():
            description = html.escape(testcase.description) if len(testcase.description) > 0 else '(hidden)'
            res = {
                'passed_test': True,
                'test_desc': description,
                #'debug': testcase.is_visible
                'debug': False, # Always false until debugger is implemented
                #'exception_type': 'error', (none initially)
                #'runtime_error': 'error message',
                'test_val': '',
            }
            test_name = testcase.test_name
            failures = test_results['failures']
            if test_name in failures:
                message = self._formatTextForHTML(failures[test_name])
                res['test_val'] = message if len(message) > 0 else '(hidden)'
                res['passed_test'] = False
            if save:
                TestRun.objects.create(submission=self, testcase=testcase,
                                       test_passed=res['passed_test'])
            results.append(res)

        runner.lang.clear() # Removing compiled files
        return results, None

    def _formatTextForHTML(self, text):
        return str(html.escape(text)).replace('\n', '<br />')

    def _createCompileErrorResponse(self, e: CompilationError):
        error = 'Compile error:<br />' + str(e).replace('\n', '<br />')
        return [{ 'passed_test': False,
                  'exception_type': 'error',
                  'exception': error,
                  'test_val': error}], None

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

    Visibility of test case information is controlled by is_visible.
    These test cases are generated when setting the problem test_suite.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
    test_name = models.TextField()

    def __str__(self):
        if self.description:
            return '{0}: {1}'.format(self.test_name, self.description)
        else:
            return self.test_name

    def save(self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        # Skip the parent because it calls save on Problem, which we don't want
        AbstractSelfAwareModel.save(self, force_insert, force_update, using,
                update_fields)


class TestRun(AbstractTestRun):
    """
    A coding problem testrun, created for each testcase on each submission.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)

    def get_history(self):
        return {
            'visible': self.testcase.is_visible,
            'passed': self.test_passed,
            'description': self.testcase.description
        }

post_delete.connect(problem_delete, sender=Problem)

