/*
 * This test suite will:
 * - Create a problem
 * - Run it through the student submission page
 * - Ensure test cases output proper results
 * - Delete the problem
 *
 * It was designed as a smoke test. If it passes, PCRS isn't completely broken
 */

var testDescription = 'Test creating a C problem and verifying ' +
                      'test case output.';
casper.test.begin(testDescription, 3, function(test) {
    // Junk is in the strings for smoke testing.
    var problemName = 'Casper Problem';
    var problemDescription = 'Problem \nDescription\n{}^ü<b>hi</b>';
    var problemTag = 'casperjs_test';
    var problemCode =
        '#include <stdio.h>\n' +
        '#include <stdlib.h>\n' +
        'int main(int argc, char **argv) {\n' +
        '    int values[3] = { 7, 2, 37 };\n' +
        '    printf("%d", values[atoi(argv[1])]);\n' +
        '    return(0);\n' +
        '}\n';

    startAsPasswordlessAdmin();
    deleteProblem('c', problemName);

    casper.thenOpen(rootUrl + '/problems/c/create', function() {
        // Wait for the codemirror to render.
        this.waitForSelector('#div_id_starter_code .CodeMirror');
    });
    // Set the starter code
    casper.thenEvaluate(function(code) {
        var mirror = cmh_list['id_starter_code'].getCodeMirror(0);
        mirror.getDoc().setValue(code);
    }, problemCode);

    // Submit the problem
    casper.then(function() {
        this.sendKeys('#id_name', problemName);
        this.sendKeys('#id_description', problemDescription);
        this.fill('form', {}, true);
    }).then(function() {
        this.waitForUrlChange();
    });

    addGenericTestCase(casper, '0', '7');
    addGenericTestCase(casper, '2', 'incorrect');
    addGenericTestCase(casper, '100000', 'overflow - segfault probably');

    // Jump to the student submission page
    casper.then(function() {
        this.waitForSelector('#submit-id-attempt');
    }).then(function() {
        this.click('#submit-id-attempt');
    })

    // Submit the student code for compilation & testing
    casper.then(function() {
        this.waitForSelector('#submit-id-submit');
    }).then(function() {
        this.click('#submit-id-submit');
    }).then(function() {
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
            return $row.find('.red-alert').length == 1;
        });
    });

    deleteProblem('c', problemName);

    casper.run(function() {
        test.done();
    });
});

