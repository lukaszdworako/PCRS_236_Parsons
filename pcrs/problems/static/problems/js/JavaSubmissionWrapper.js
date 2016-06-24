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
    var $codeDiv = this.wrapperDiv.find(this.isEditor
        ? '#div_id_code_box' : '#div_id_submission');

    var code;

    if (this.isEditor) {
        code = '[file Hello.java]\n' +
            'public class Hello {\n' +
            '    public static void main(String args[]) {\n' +
            '       System.out.println("Well hello there");\n' +
            '    }\n' +
            '}\n' +
            '\n' +
            '[/file]\n';
        var mode = cmModeForLanguageAndVersion(
            this.language, this.language_version);
        this.tcm.setNewFileOptions({
            'name': 'NewFile.java',
            'code': '',
            'mode': mode,
            'theme': user_theme,
        });
        this.tcm.enableTabEditingWidgets();
    } else {
        code = $codeDiv.find('textarea').text();
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

