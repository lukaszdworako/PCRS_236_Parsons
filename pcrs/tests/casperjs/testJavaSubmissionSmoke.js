/*
 * This test suite will:
 * - Create a problem
 * - Run it through the student submission page
 * - Ensure test cases output proper results
 * - Delete the problem
 *
 * It was designed as a smoke test. If it passes, PCRS isn't completely broken
 */

var testDescription = 'Test creating a Java problem and verifying ' +
                      'test case output.';
casper.test.begin(testDescription, 4, function(test) {
    // Junk is in the strings for smoke testing.
    var problemName = 'Casper Problem';
    var problemDescription = 'Problem \nDescription\n{}^ü<b>hi</b>';
    var problemTag = 'casperjs_test';

    startAsPasswordlessAdmin();
    deleteProblem('java', problemName);

    casper.thenOpen(rootUrl + '/problems/java/create', function() {
        // Wait for all the DOM, code mirrors, and tag selectors to load
        this.waitForSelector('#div_id_starter_code .CodeMirror');
        this.waitForSelector('#div_id_solution .CodeMirror');
        this.waitForSelector('#div_id_test_suite .CodeMirror');
    });

    // Set the initial code
    casper.thenEvaluate(function() {
        // cmh_list is a global in PCRS. Ugly, I know.
        var starterCodeTabbedCodeMirror = cmh_list['id_starter_code'];
        var testSuiteCodeMirror = cmh_list['id_test_suite'];

        var helloCode =
            '[blocked]\n' +
            'public class Hello {\n' +
            '[/blocked]\n' +
            '[student_code]\n' +
            '    public static String sayHello() {\n' +
            '        return "hello";\n' +
            '    }\n' +
            '[/student_code]\n' +
            '[hidden]\n' +
            '\n' +
            '[/hidden]\n' +
            '[student_code]\n' +
            '    public static void writeToFile() {\n' +
            '        try {\n' +
            '            new java.io.File("test.txt").createNewFile();\n' +
            '        } catch (java.io.IOException e) {\n' +
            '            e.printStackTrace();\n' +
            '        }\n' +
            '    }\n' +
            '[/student_code]\n' +
            '[blocked]\n' +
            '}\n' +
            '[/blocked]\n';
        var fooCode =
           '[student_code]\n' +
           'class Foo {\n' +
           '    public static int number() {\n' +
           '        return 12;\n' +
           '    }\n' +
           '}\n' +
           '[/student_code]\n';

        starterCodeTabbedCodeMirror.addFile({
            'name': 'Hello.java',
            'code': helloCode,
        });
        starterCodeTabbedCodeMirror.addFile({
            'name': 'Foo.java',
            'code': fooCode,
        });
        // Default file named "NewFile.java" or something - We don't want it!
        starterCodeTabbedCodeMirror.removeFileAtIndex(0);

        testSuiteCodeMirror.setValue(
            'import org.junit.*;\n' +
            'import static org.junit.Assert.*;\n' +
            'public class Tests {\n' +
            '    @Test\n' +
            '    public void exampleTestCase() {\n' +
            '        assertEquals(4, 2 + 2);\n' +
            '        assertEquals("Arithmetic is broken!", 5, 3 + 2);\n' +
            '    }\n' +
            '    @Test\n' +
            '    public void testSecurity() {\n' +
            '        Hello.writeToFile();\n' +
            '    }\n' +
            '    @Test\n' +
            '    public void testSayHello() {\n' +
            '        assertEquals("hello", Hello.sayHello());\n' +
            '    }\n' +
            '    @Test\n' +
            '    public void testFortyTwo() {\n' +
            '        assertEquals(42, Foo.number());\n' +
            '    }\n' +
            '}\n'
        );
    });

    // Save the problem
    casper.then(function() {
        this.sendKeys('#id_name', problemName);
        this.sendKeys('#id_description', problemDescription);
        this.fill('form', {}, true);
    });

    // After saving the problem, run it
    casper.then(function() {
        this.waitForSelector('#submit-id-attempt');
    }).then(function() {
        this.click('#submit-id-attempt');
    });

    // Compile the student code
    casper.then(function() {
        this.waitForSelector('#submit-id-submit');
    }).then(function() {
        this.click('#submit-id-submit');
    });

    casper.then(function() {
        this.waitForSelector('.pcrs-table-row');
    });

    // Test if the correct test cases passed or failed
    casper.then(function() {
        test.assertEval(function() {
            var $row = $($('.pcrs-table-row')[0]);
            return $row.find('img[alt="Smiley Face"]').length == 1;
        });
        test.assertEval(function() {
            var $row = $($('.pcrs-table-row')[1]);
            return $row.find('img[alt="Sad Face"]').length == 1;
        });
        test.assertEval(function() {
            var $row = $($('.pcrs-table-row')[2]);
            return $row.find('img[alt="Smiley Face"]').length == 1;
        });
        test.assertEval(function() {
            var $row = $($('.pcrs-table-row')[3]);
            return $row.find('img[alt="Sad Face"]').length == 1;
        });
    });

    deleteProblem('java', problemName);

    casper.run(function() {
        test.done();
    });
});

