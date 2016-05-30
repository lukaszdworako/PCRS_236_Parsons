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
            '    // Ello, govna!\n'
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
        self.problem = Problem(pk=1,
            name='test_problem', visibility='open', max_score=3,
            test_suite=test_suite, starter_code=starter_code)
        self.problem.save()

    def testCompileAndVerifyOutput(self):
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
        sub = Submission.objects.create(problem=self.problem,
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

        self.assertTrue(testSayHello['passed_test'])

        self.assertFalse(
            testSecurityResult['passed_test'],
            'This should be sandboxed and fail')
        self.assertEqual(
            testSecurityResult['test_desc'], 'Test security.',
            'The description was not returned properly.')
        self.assertRegex(
            testSecurityResult['test_val'], re.compile('java.security.*Hello\.writeToFile\(.*?\)\n?', re.DOTALL),
            'Your test value should be a stack trace that reveals no test case internals')


class TestProblemHelpers(test.TestCase):
    def setUp(self):
        self.problem = Problem.objects.create(pk=2,
            name='test_problem', visibility='open', max_score=3,
            test_suite='', starter_code='')

    def testStripComment(self):
        commentString = (
            '/** ***\n'
            '  \t * * Hello, *world!\n\n'
            '\t */'
        )
        result = self.problem._stripComment(commentString)
        self.assertEqual(result, "***\n* Hello, *world!")

        result = self.problem._stripComment("\t   \n \t  \t//    hai   \t")
        self.assertEqual(result, "hai")

    def testCompressSuperfluousCode(self):
        code = (
            'import java.io.File;\n'
            '\n'
            '\t \t// It should remove this comment\n'
            '//\n'
            'class Foob {\n\n\n\n\n'
            '  \t  private String hai = "// This should not be stripped";\n'
            '}\n'
            '\n'
            '        /*\n'
            '  \t  What about block comments?\n'
            '                */\n'
        )
        result = self.problem._compressSuperfluousCode(code)
        compressedCode = (
            'import java.io.File;\n'
            'class Foob {\n'
            'private String hai = "// This should not be stripped";\n'
            '}\n'
        )
        self.assertEqual(result, compressedCode, 'Code compression is broken')

    def testGenerateTestInfo(self):
        code = (
            '/* Blah */\n'
            'public class Foob {\n'
            '/*\ntest\n*/\n'
            '    // This comment shouldn\'t be taken as the description.\n'
            '\n'
            '    @Test(expected=blah)\n'
            '\n'
            '\n'
            '    public   void   testHai_there(void bar);\n'
            '\n'
            '    /**\n'
            '     * This is an\n'
            '     * important test.\n'
            '     *****************/\n'
            '    @Test\n'
            '    public void testImportantStuff();\n'
            '\n'
            '    // This will be ignored, since it doesn\'t have the annotation.\n'
            '    public void notATest();\n'
            '\n'
            '    //       Line comment.\n'
            '    @Test\n'
            '    public void testLineComment();\n'
            '}\n'
        )

        resultDict = self.problem._generateTestInfo(code)
        self.assertEqual(len(resultDict), 3,
            'One of the test annotations wasn\'t recocnized')

        self.assertEqual(resultDict[0]['name'], 'testHai_there')
        self.assertEqual(resultDict[0]['description'], '')
        self.assertEqual(resultDict[1]['name'], 'testImportantStuff')
        self.assertEqual(resultDict[1]['description'], 'This is an\nimportant test.')
        self.assertEqual(resultDict[2]['name'], 'testLineComment')
        self.assertEqual(resultDict[2]['description'], 'Line comment.')

