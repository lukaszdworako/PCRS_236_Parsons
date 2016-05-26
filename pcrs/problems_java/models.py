import re
import html
from hashlib import sha1

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete

from problems.pcrs_languages import GenericLanguage
from problems.models import (AbstractProgrammingProblem, AbstractSubmission,
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
        self._initial_test_suite = self.test_suite
        self._testCases = self._generateTestInfo(self.test_suite)

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
        self._testCases = self._generateTestInfo(self.test_suite)
        self.max_score = len(self._testCases)
        super().save(force_insert, force_update, using, update_fields)

    def getTestDescription(self, test_name):
        return self._testCases[test_name]

    def getAllTestNames(self):
        '''Retrieves the test method names.

        These can be used to identify the different tests.

        Returns:
            A lexicographically sorted list of test method names.
        '''
        return sorted(self._testCases.keys())

    def isTestVisible(self, test_name):
        # We say the test case is visible if it has a description.
        return True if self.getTestDescription(test_name).strip() else False

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
        return {
            m[1]: self._stripComment(m[0])
            for m in re.findall(reg, test_code)
        }

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
        for test_name in self.problem.getAllTestNames():
            description = self.problem.getTestDescription(test_name)
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
                res['test_val'] = message if len(message) > 0 else '(hidden)'
                res['passed_test'] = False
            if save:
                TestRun.objects.create(problem=self.problem, submission=self,
                                       test_name=test_name, test_passed=res['passed_test'])
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
        self.mod_submission = self._emplaceStudentCodeSnippets(student_code_list, self.problem.starter_code)

        # Replace hashed key with text (Implementation start/end)
        x = 0
        while x < student_code_key_list_len:
            m = re.search(student_code_key, self.submission)
            self.submission = self.submission[: m.start()] + self.submission[m.end():]
            x += 1

        # Remove blocked tags from the source code
        self.mod_submission = re.sub(r'\[\/?blocked\]\r?\n?', '', self.mod_submission)

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
        self.mod_submission = re.sub(r'\[\/?hidden\]\r?\n?', '', self.mod_submission)

    def _emplaceStudentCodeSnippets(self, student_code_list, starter_code):
        '''Emplaces the given code snippets into the given starter code.
        The [student_code] tags will be replaced appropriately.

        Args:
            student_code_list: A list of student code snippets.
            starter_code:      The starter code - probably from the Problem class.
        Returns:
            The given snippets emplaced into the corresponding code tag positions.
        '''
        emplacementRegex = re.compile('\[student_code\].*?\[\/student_code\]\r?\n?', re.DOTALL)
        while len(student_code_list) > 0 and starter_code.find('[student_code]') != -1:
            student_code = student_code_list.pop(0)
            starter_code = re.sub(emplacementRegex, student_code, starter_code, 1)
        return starter_code


class TestRun(AbstractTestRun):
    """
    A coding problem testrun, created for each test suite method on each submission.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                null=False, blank=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    test_name = models.TextField(blank=False)

    def get_history(self):
        return {
            'visible': self.problem.isTestVisible(self.test_name),
            'passed': self.test_passed,
            'description': self.problem.getTestDescription(self.test_name)
        }

post_delete.connect(problem_delete, sender=Problem)

