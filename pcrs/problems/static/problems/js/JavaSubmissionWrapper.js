function JavaSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "java";
    this.language_version = 'text/x-java';
    this.tcm = new TabbedCodeMirror();
    this.lastSubmissionPk = 0;
}
JavaSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
JavaSubmissionWrapper.prototype.constructor = JavaSubmissionWrapper;

/**
 * @override
 */
JavaSubmissionWrapper.prototype.createCodeMirrors = function() {
    var $codeDiv = this.wrapperDiv.find(this.isEditor
        ? '#div_id_code_box' : '#div_id_submission');

    var code = $codeDiv.find('textarea').text();

    if (this.isEditor) {
        var mode = cmModeForLanguageAndVersion(
            this.language, this.language_version);
        this.tcm.setNewFileOptions({
            'name': 'NewFile.java',
            'code': '',
            'mode': mode,
            'theme': user_theme,
        });
        this.tcm.enableTabEditingWidgets();
    }

    setTabbedCodeMirrorFilesFromTagText(this.tcm, code);
    // Replace the code div with the tabbed code mirror
    $codeDiv.before(this.tcm.getJQueryObject());
    $codeDiv.remove();

    myCodeMirrors[this.wrapperDivId] = this.tcm;
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._showEditorTraceDialog = function() {
    var code = this._generateCodeForEditor();
    $('#waitingModal').modal('show');
    getVisualizerComponents(code, '', 9999999);
    $('#visualizerModal').modal('show');
    // FIXME proper-i-fy-this  - and when you fix it, fix the Python one too
    setTimeout(PythonSubmissionWrapper._waitVis, 100);
}

JavaSubmissionWrapper.prototype._generateCodeForEditor = function() {
    var files = this.tcm.getFiles();
    var code = '';

    for (var i = 0; i < files.length; i++) {
        code += '[file ' + files[i].name + ']\n' +
            files[i].code +
            '\n[/file]\n';
    }
    return code;
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

    return $newRow;
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    SubmissionWrapper.prototype.prepareGradingTable.apply(this, arguments);
    var $gradingTable = this.wrapperDiv.find("#gradeMatrix");

    this.lastSubmissionPk = testData['sub_pk'];

    if (this.wrapperDiv.find('#visualizeButton').length == 0) {
        var that = this;
        $gradingTable.before(
            $('<a id="visualizeButton" class="btn btn-info" role="button"></a>')
                .text('Visualize')
                .click(function() {
                    that._visualizeHistoryEntryPk(that.lastSubmissionPk);
                }));
    }
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._createHistoryCodeMirror = function(entry,
        mirrorId) {
    var $codeDiv = $("#" + mirrorId);
    var codeText = $codeDiv.text();
    var tcm = new TabbedCodeMirror();

    setTabbedCodeMirrorFilesFromTagText(tcm, codeText);

    var that = this;
    $codeDiv
        .before($('<a class="btn btn-danger pull-right" role="button"></a>')
            .text('Revert')
            .click(function() {
                that._revertToCodeFromHistoryModal(codeText);
            }))
        .before($('<a class="btn btn-info pull-right" role="button"></a>')
            .text('Visualize')
            .click(function() {
                that._visualizeHistoryEntryPk(entry['sub_pk']);
            }))
        // Replace the code div with the tabbed code mirror
        .before(tcm.getJQueryObject())
        .remove();

    cmh_list[mirrorId] = tcm;
}

JavaSubmissionWrapper.prototype._revertToCodeFromHistoryModal = function(code) {
    /*
     * This can't be a modal confirmation since the history modal is
     * already being shown. Bootstrap doesn't support multiple modals being
     * open at the same time.
     */
    if ( ! confirm('Revert current code to this submission?')) {
        return;
    }

    setTabbedCodeMirrorFilesFromTagText(this.tcm, code);

    var $historyDiv = $('#history_window_' + this.wrapperDivId);
    $historyDiv.modal('hide');
    this.wrapperDiv.find('#grade-code').hide();
    this.wrapperDiv.find('#alert').hide();
}

/**
 * Jumps to the visualizer for the given submission history entry.
 */
JavaSubmissionWrapper.prototype._visualizeHistoryEntryPk = function(entryPk) {
    window.location.href = root + 'editor/java/visualize/' + entryPk;
}

