import re
import html

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete

from problems.helper import remove_tag
from problems.pcrs_languages import GenericLanguage
from problems.models import (AbstractProgrammingProblem, AbstractSubmission,
    SubmissionPreprocessorMixin, AbstractSelfAwareModel, AbstractTestCase,
    AbstractTestRun, problem_delete)
from .java_language import CompilationError

test_suite_template = """import org.junit.*;
import static org.junit.Assert.*;

public class Tests {
    @Before
    public void setUp() {
    }

    @After
    public void tearDown() {
    }

    // <public test case description goes here>
    @Test
    public void test() {
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

    def __init__(self, *args, **kwargs):
        super(AbstractProgrammingProblem, self).__init__(*args, **kwargs)

        '''
        If the test suite is sent from a kwarg, we still want the
        test cases to regenerate when this problem is saved.
        '''
        if kwargs.get('test_suite'):
            self._initial_test_suite = test_suite_template
        else:
            self._initial_test_suite = self.test_suite

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)

        # CodeMirror inserts carriage returns, but we don't like them!
        carriageReturnRegex = re.compile('\r')
        self.test_suite = re.sub(carriageReturnRegex, '', self.test_suite)
        self.solution = re.sub(carriageReturnRegex, '', self.solution)
        self.starter_code = re.sub(carriageReturnRegex, '', self.starter_code)

        if self.pk:
            if self.submission_set.all() and self._testSuiteHasChanged():
                raise ValidationError({'test_suite': [
                    'Submissions must be cleared before editing a testcase.',
                ]})

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # In the editor, we don't save testcases
        if not self.is_editor_problem():
            # We need the problem to exist before generating test cases
            if not self.pk:
                pass
                super().save(force_insert, force_update, using, update_fields)

            '''
            We have to generate the test case table whenever we save a problem.
            It seems a bit hacky to do this, but most of PCRS depends on
            problems having a dedicated test case table.
            '''
            self._repopulateTestCaseTable()
            self.max_score = len(self.testcase_set.all())
        super().save(force_insert, force_update, using, update_fields)

    def _repopulateTestCaseTable(self):
        # Regenerate the test case table entries for this problem's test_suite
        testCaseInfo = self._generateTestInfo(self.test_suite)

        for testcase in self.testcase_set.all():
            testcase.delete()
        for test in testCaseInfo:
            self.testcase_set.create(
                test_name=test['name'],
                description=test['description'])

    def _testSuiteHasChanged(self):
        ''''Determines if the problem submission resulted in changed test code.
        This will ignore comments/descriptions and superfluous whitespace.
        NOTE: The current limitation is assertion messages. At some point
              it would be nice to ignore assert messages.

        Returns:
            True if the test code has changed, otherwise False.
        '''
        newSuiteCode = self._compressSuperfluousCode(self.test_suite)
        oldSuiteCode = self._compressSuperfluousCode(self._initial_test_suite)
        return newSuiteCode != oldSuiteCode

    def _compressSuperfluousCode(self, code):
        '''Can be used to compare two pieces of code.

        This will strip whitespace and most comments

        Args:
            code: String to strip from.
        Returns:
            A string, stripped of comments and whitespace (except newlines)
        '''
        # Remove (most) line comments
        code = re.sub(re.compile('\n[ \t]*\/\/[^\n]*'), '', code)
        # Remove (most) block comments
        code = re.sub(re.compile('\n[ \t]*\/\*.*?\*\/', re.DOTALL), '', code)
        # Compress irrelevant whitespace
        code = re.sub(re.compile('(?<=\n)[ \t\n]+', re.DOTALL), '', code)

        return code

    def _generateTestInfo(self, test_code):
        reg = re.compile(
            # Comment / Description capturing
            '(\/\/[^\n]*|\/\*+'        # Line comments & block comment starts
            '(?:.|\n[\t ]*\*[\t ]+)*?' # Block comment content
            '\n[\t ]*\*+\/)?[\t ]*\n'  # Block comment endings
            # Only capture methods annotated with @Test
            '[\t ]*@Test(?:\(.*?\))?\s*'
            # Capture method name
            'public\s*void\s*([\w_]+)'
        )
        return [
            {
                'name': m[1],
                'description': self._stripComment(m[0]),
            }
            for m in re.findall(reg, test_code)
        ]

    def _stripComment(self, comment):
        ''''Determines if the problem submission resulted in changed test code.
        This will ignore comments/descriptions and superfluous whitespace.
        NOTE: The current limitation is assertion messages. At some point
              it would be nice to ignore assert messages.

        Returns:
            True if the test code has changed, otherwise False.
        '''
        comment = re.sub('[\t ]*\/\/[\t ]*', '', comment)
        comment = re.sub('\/\*+', '', comment)
        comment = re.sub('\*+\/', '', comment)
        comment = re.sub('\n[\t ]*\*[\t ]*', '\n', comment)
        return comment.strip()


class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
    """
    A coding problem submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def get_displayable_submission(self):
        '''We want to return the tags for the history modal in PCRS-Java.
        '''
        code = self.fuseStudentCodeIntoStarterCode()
        code = remove_tag('[hidden]', '[/hidden]', code)
        return code

    def run_testcases(self, request, save=True):
        """
        Run all testcases for the submission and create testrun objects.
        Return the list of testrun results.
        """

        runner = GenericLanguage(self.problem.language)
        files = self.preprocessTags()

        try:
            # necessary since language requires compilation
            runner.lang.compile(self.user.username, files, self.problem.test_suite)
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
            test_name = testcase.test_name
            description = testcase.description
            description = html.escape(description) if description else '(hidden)'
            res = {
                'passed_test': True,
                'test_desc': description,
                #'debug': self.problem.isTestVisible(test_name)
                'debug': False, # Always false until debugger is implemented
                #'exception_type': 'error', (none initially)
                #'runtime_error': 'error message',
                'test_val': '',
            }
            failures = test_results['failures']
            if test_name in failures:
                message = self._formatTextForHTML(failures[test_name])
                res['test_val'] = message if len(message.strip()) > 0 else '(hidden)'
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


class TestCase(AbstractTestCase):
    """
    A coding problem testcase.

    Visibility of test case information is controlled by is_visible.
    These test cases are generated when setting the problem test_suite.
    """
    problem = models.ForeignKey(Problem,
        on_delete=models.CASCADE, null=False, blank=False)
    test_name = models.TextField()

    def __str__(self):
        if self.description:
            return '{0}: {1}'.format(self.test_name, self.description)
        else:
            return self.test_name

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        # Skip the parent because it calls save on Problem, which we don't want
        AbstractSelfAwareModel.save(self,
            force_insert, force_update, using, update_fields)


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
            'description': self.testcase.description,
        }

post_delete.connect(problem_delete, sender=Problem)

