function JavaSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "java";
    this.language_version = 'text/x-java';
}
JavaSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
JavaSubmissionWrapper.prototype.constructor = JavaSubmissionWrapper;

/**
 * @override
 */
JavaSubmissionWrapper.prototype.createCodeMirrors = function() {
    var $codeDiv = this.wrapperDiv.find("#div_id_submission");
    myCodeMirrors[this.wrapperDivId] =
        emplaceTabbedCodeMirrorOnCodeDiv($codeDiv);
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype.getAllCode = function() {
    var hash = CryptoJS.SHA1(this.problemId);
    return myCodeMirrors[this.wrapperDivId].getHashedCode(hash);
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    CSubmissionWrapper.prototype.prepareGradingTable.apply(this, arguments);
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._createTestCaseRow = function(testcase) {
    var $newRow = SubmissionWrapper.prototype._createTestCaseRow.apply(
        this, arguments);

    if ('exception' in testcase) {
        return $newRow;
    }

    $newRow.append('<td>' + testcase.test_desc + '</td>');
    $newRow.append('<td>' +
       '<div>' +
       '<span class="stringObj">' +
       testcase.test_val +
       '</span>' +
       '</div></td>');

    this._addFaceColumnToTestRow($newRow, testcase.passed_test);
    this._addA11yToTestRow($newRow, testcase.test_val,
        testcase.passed_test, testcase.expected_output);
    // NOTE: We might remove this in place of a single debug button.
    $newRow.append('<td class="debug">-</td>');

    return $newRow;
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._createHistoryCodeMirror = function(mirrorId) {
    var $codeDiv = $("#" + mirrorId);
    cmh_list[mirrorId] = emplaceTabbedCodeMirrorOnCodeDiv($codeDiv);
}

