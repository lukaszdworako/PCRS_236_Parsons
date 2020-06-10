/*
 * Smoke test for the Java visualizer
 * This will simply open the visualizer, jump to the last step, and ensure
 * nothing went horribly wrong in doing so.
 */

var x = require('casper').selectXPath;

var testDescription = 'Smoke test for the Java visualizer';
casper.test.begin(testDescription, 1, function(test) {
    startAsPasswordlessAdmin();

    casper.thenOpen(rootUrl + '/editor/java/submit', function() {
        // Wait for all the DOM and code mirrors to appear
        this.waitForSelector('.CodeMirror');
    });

    // Open the visualizer dialog
    casper.then(function() {
        this.click('#submit-id-trace');
        this.waitForSelector('#jmpLastInstr');
    });
    // Jump to the end of the visualization
    casper.then(function() {
        this.click('#jmpLastInstr');
    });
    // Make sure nothing exploded during this process
    casper.then(function() {
        test.assertEval(function() {
            var curInstrText = $('#curInstr').text();
            return curInstrText == 'Program terminated';
        });
    });

    casper.run(function() {
        test.done();
    });
});

