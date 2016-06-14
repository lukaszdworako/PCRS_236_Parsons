function CSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "c";
    this.language_version = 'text/x-csrc';
}
CSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
CSubmissionWrapper.prototype.constructor = CSubmissionWrapper;

/**
 * @override
 */
CSubmissionWrapper.prototype.createCodeMirrors = function() {
    var codeDiv = this.wrapperDiv.find('#div_id_submission');
    var codeObj = TagManager.stripTagsForStudent(codeDiv.text());

    myCodeMirrors[this.wrapperDivId] = to_code_mirror(
        this.language, this.language_version,
        this.wrapperDiv.find("#div_id_submission"), codeObj.code, false);

    // Debugger declaration
    debugger_id = this.wrapperDivId + 1;
    myCodeMirrors[debugger_id] = to_code_mirror(
        this.language, this.language_version,
        $("#id_preview_code_debugger"), codeObj.code, true);

    var mirror = myCodeMirrors[this.wrapperDivId];
    highlightCodeMirrorWithTags(mirror, codeObj.blocked_ranges);
    preventDeleteLastLine(mirror);
}

/**
 * @override
 */
CSubmissionWrapper.prototype.getAllCode = function() {
    var hash = CryptoJS.SHA1(this.problemId);
    return TabbedCodeMirror._getHashedCodeFromMirror(
        myCodeMirrors[this.wrapperDivId], hash);
}

/**
 * @override
 */
CSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    if (this.isEditor) {
        var testcases = testData['testcases'];
        // Handle compilation error and warning messages
        var dont_visualize = handleCompileMessages(this.wrapperDivId, testcases);
        /*
         * If it's the editor, start calling
         * visualizer functions now so long as no errors exist.
         */
        if ( ! dont_visualize) {
            getVisualizerComponents(code, "", 9999999);
        }
        return;
    }

    SubmissionWrapper.prototype.prepareGradingTable.apply(this, arguments);
}

/**
 * @override
 */
CSubmissionWrapper.prototype._createTestCaseRow = function(testcase) {
    var $newRow = SubmissionWrapper.prototype._createTestCaseRow.apply(
        this, arguments);

    if ('exception' in testcase) {
        return $newRow;
    }

    $newRow.append('<td class="description">' + testcase.test_desc + '</td>');

    if (testcase.test_input != null) {
        $newRow.append('<td class="expression"><div class="expression_div">' +
                testcase.test_input + '</div></td>');
    } else {
        $newRow.append('<td class="expression">' +
                "Hidden Test" +'</td>');
    }

    var expTestValDiv = $('<div class="ExecutionVisualizer"></div>')
        .append('<span class="stringObj">' + testcase.expected_output + '</span>');
    var testResultDiv = $('<div class="ExecutionVisualizer"></div>')
        .append('<span class="stringObj">' + testcase.test_val + '</span>');

    $newRow.append($('<td class="expected"></td>')
        .append($('<div class="ptd"></div>')
            .append(expTestValDiv)));
    $newRow.append($('<td class="result"></td>')
        .append($('<div class="ptd"></div>')
            .append(testResultDiv)));

    this._addFaceColumnToTestRow($newRow, testcase.passed_test);
    this._addDebugColumnToTestRow($newRow, testcase.debug);
    this._addA11yToTestRow($newRow, testcase.test_val,
        testcase.passed_test, testcase.expected_output);

    return $newRow;
}

/**
 * @override
 */
CSubmissionWrapper.prototype._prepareVisualizer = function(row) {
    var testcaseCode = row.find(".expression_div").text();
    var newCode =
        addHashkey(myCodeMirrors[this.wrapperDivId], this.problemId);
    getVisualizerComponents(newCode, testcaseCode, this.problemId);
}

