function JavaSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "java";
    this.language_version = 'text/x-java';
    this.tcm = new TabbedCodeMirror();
}
JavaSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
JavaSubmissionWrapper.prototype.constructor = JavaSubmissionWrapper;

/**
 * @override
 */
JavaSubmissionWrapper.prototype.createCodeMirrors = function() {
    var $codeDiv = this.wrapperDiv.find("#div_id_submission");
    var codeText = $codeDiv.text();

    setTabbedCodeMirrorFilesFromTagText(this.tcm, codeText);

    // Replace the code div with the tabbed code mirror
    $codeDiv.before(this.tcm.getJQueryObject());
    $codeDiv.remove();

    myCodeMirrors[this.wrapperDivId] = this.tcm;
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
    // NOTE: We might remove this in place of a single debug button.
    $newRow.append('<td class="debug">-</td>');
    this._addA11yToTestRow($newRow, testcase.test_val,
        testcase.passed_test, testcase.expected_output);

    return $newRow;
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._createHistoryCodeMirror = function(mirrorId) {
    var $codeDiv = $("#" + mirrorId);
    var codeText = $codeDiv.text();
    var tcm = new TabbedCodeMirror();
    console.log(codeText);

    setTabbedCodeMirrorFilesFromTagText(tcm, codeText);

    // Add a button to revert to this submission
    var that = this;
    $codeDiv.before($('<a class="btn btn-danger pull-right" role="button"></a>')
        .text('Revert')
        .click(function() {
            that._revertToCodeFromHistoryModal(codeText);
        }));

    // Replace the code div with the tabbed code mirror
    $codeDiv.before(tcm.getJQueryObject());
    $codeDiv.remove();

    cmh_list[mirrorId] = tcm;
}

JavaSubmissionWrapper.prototype._revertToCodeFromHistoryModal = function(code) {
    if ( ! confirm('Revert current code to this submission?')) {
        return;
    }

    setTabbedCodeMirrorFilesFromTagText(this.tcm, code);

    var $historyDiv = $('#history_window_' + this.wrapperDivId);
    $historyDiv.modal('hide');
    this.wrapperDiv.find('#grade-code').hide();
    this.wrapperDiv.find('#alert').hide();
}

