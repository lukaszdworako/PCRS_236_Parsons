import re

from django import test

from problems_java.models import Problem, Submission
from tests.ViewTestMixins import UsersMixin

class TestSubmissionByCompiling(UsersMixin, test.TestCase):
    '''Tests the compile procedure

    Note that we should try to compile as few things as
    possible to allow the test suite to run quickly. To test JUnit output and
    stack trace stripping, it is probably best to access the
    private methods in java_language.py
    '''

    def setUp(self):
        UsersMixin.setUp(self)
        test_suite = (
            'import org.junit.Test;\n'
            'import static org.junit.Assert.*;\n'
            'public class Tests {\n'
            '    @Test\n'
            '    public void testArithmetic() {\n'
            '        assertEquals(4, 2 + 2);\n'
            '    }\n'
            '    // Test security.\n'
            '    @Test\n'
            '    public void testSecurity() {\n'
            '        Hello.writeToFile();\n'
            '    }\n'
            '    @Test\n'
            '    public void testSayHello() {\n'
            '        assertEquals("hello", Hello.sayHello());\n'
            '    }\n'
            '}\n')
        starter_code = (
                '[student_code]\n'
                '\n'
                '[/student_code]\n'
        )
        Problem.objects.create(
            pk=1, name='test_problem', visibility='open', max_score=3,
            test_suite=test_suite, starter_code=starter_code)

    def testCompileAndVerifyOutput(self):
        prob = Problem.objects.get(pk=1)
        code = (
                # A bit of a hack to get the tag preprocessor to work.
                # This is the sha1 encoding of the primary key "1"
                # (See preprocess_tags in problems_java/models.py)
                '356a192b7913b04c54574d18c28d46e6395428ab\n'
                '\npublic class Hello {\n'
                '    public static String sayHello() {\n'
                '        return "hello";\n'
                '    }\n'
                '    public static void writeToFile() {\n'
                '        try {\n'
                '            new java.io.File("test.txt").createNewFile();\n'
                '        } catch (java.io.IOException e) {\n'
                '            e.printStackTrace();\n'
                '        }\n'
                '    }\n'
                '}\n'
                '356a192b7913b04c54574d18c28d46e6395428ab\n')
        sub = Submission.objects.create(problem=prob,
            user=self.student, section=self.section, score=2, submission=code)
        sub.save()

        response, _ = sub.run_testcases(None)
        self.assertEqual(len(response), 3)

        testArithmeticResult = response[0]
        testSecurityResult   = response[1]
        testSayHello         = response[2]

        self.assertTrue(
            testArithmeticResult['passed_test'],
            'This should pass')
        self.assertRegex(
            testArithmeticResult['test_desc'].lower(), re.compile('hidden'),
            'The test method description is empty, so we should indicate "hidden"')
        self.assertEqual(
            testArithmeticResult['test_val'], '',
            'The test value should be empty')

        self.assertFalse(
            testSecurityResult['passed_test'],
            'This should be sandboxed and fail')
        self.assertEqual(
            testSecurityResult['test_desc'], 'Test security.',
            'The description was not returned.')
        self.assertRegex(
            testSecurityResult['test_val'], re.compile('java.security.*Hello\.writeToFile\(.*?\)\n?', re.DOTALL),
            'Your test value should be a stack trace that reveals no test case internals')

        self.assertTrue(testSayHello['passed_test'])

