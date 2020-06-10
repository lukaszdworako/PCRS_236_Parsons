/*
 * This test suite will:
 * - Create a problem
 * - Run it through the student submission page
 * - Ensure test cases output proper results
 * - Delete the problem
 *
 * It was designed as a smoke test. If it passes, PCRS isn't completely broken
 */

var testDescription = 'Test creating a Python problem and verifying ' +
                      'test case output.';
casper.test.begin(testDescription, 3, function(test) {
    // Junk is in the strings for smoke testing.
    var problemName = 'Casper Problem';
    var problemDescription = 'Problem \nDescription\n{}^ü<b>hi</b>';
    var problemCode =
        'def double(num):\n' +
        '    return num * 2\n' +
        'def triple(num):\n' +
        '    return num * 4\n';

    startAsPasswordlessAdmin();
    deleteProblem('python', problemName);

    casper.thenOpen(rootUrl + '/problems/python/create');

    // Submit the problem
    casper.then(function() {
        this.sendKeys('#id_name', problemName);
        this.sendKeys('#id_description', problemDescription);
        this.sendKeys('#id_starter_code', problemCode);
        this.fill('form', {}, true);
    }).then(function() {
        this.waitForUrlChange();
    });

    addGenericTestCase(casper, 'double(12)', '24');
    addGenericTestCase(casper, 'triple(4)', '12');
    addGenericTestCase(casper, 'invalid syntax', 'exception should be thrown');

    // Jump to the student submission page
    casper.then(function() {
        this.waitForSelector('#submit-id-attempt');
    }).then(function() {
        this.click('#submit-id-attempt');
    });

    // Submit the problem for compilation
    casper.then(function() {
        this.waitForSelector('#submit-id-submit');
    }).then(function() {
        this.click('#submit-id-submit');
    });

    // Ensure the test cases display appropriate results
    casper.then(function() {
        this.waitForSelector('.pcrs-table-row');
    }).then(function() {
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

    deleteProblem('python', problemName);

    casper.run(function() {
        test.done();
    });
});

