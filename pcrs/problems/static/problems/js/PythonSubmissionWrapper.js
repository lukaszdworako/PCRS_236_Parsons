function PythonSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "python";
    this.language_version = 3;
}
PythonSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
PythonSubmissionWrapper.prototype.constructor = PythonSubmissionWrapper;

/**
 * @override
 */
PythonSubmissionWrapper.prototype._createTestCaseRow = function(testcase) {
    newRow.append('<td class="description">' + testcase.test_desc + '</td>');

    if (testcase.test_input != null) {
        newRow.append('<td class="expression"><div class="expression_div">' +
                testcase.test_input + '</div></td>');
    } else {
        newRow.append('<td class="expression">' +
                "Hidden Test" +'</td>');
    }

    var expTestValDiv = $('<div class="ExecutionVisualizer"></div>');
    var testResultDiv = $('<div class="ExecutionVisualizer"></div>');

    newRow.append($('<td class="expected"></td>')
        .append($('<div class="ptd"></div>')
            .append(expTestValDiv)));
    newRow.append($('<td class="result"></td>')
        .append($('<div class="ptd"></div>')
            .append(testResultDiv)));

    renderData_ignoreID(testcase.test_val, testResultDiv);
    renderData_ignoreID(testcase.expected_output, expTestValDiv);

    this._addFaceColumnToTestRow(newRow, testcase.passed_test);
    this._addA11yToTestRow(newRow, create_output(testcase.test_val),
        testcase.passed_test, testcase.expected_output);
    this._addDebugColumnToTestRow(newRow, testcase.debug);
}

/**
 * @override
 */
PythonSubmissionWrapper.prototype._prepareVisualizer = function(row) {
    var testcaseCode = row.find(".expression_div").text();
    var newCode = myCodeMirrors[this.wrapperDivId].getValue() +
        "\n" + testcaseCode;
    getVisualizerComponents(newCode, testcaseCode, this.problemId);
}

