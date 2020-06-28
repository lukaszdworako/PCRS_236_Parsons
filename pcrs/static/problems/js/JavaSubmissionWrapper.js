function JavaSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "java";
    this.language_version = 'text/x-java';
    this.lastSubmissionPk = 0;
    this.visualizer = new JavaVisualizer();
    this.visualizer.setProblemId(this.problemId);
    this.tcm = null; // Will be set in createCodeMirrors (page load)
}
JavaSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
JavaSubmissionWrapper.prototype.constructor = JavaSubmissionWrapper;

/**
 * @override
 */
JavaSubmissionWrapper.prototype.createCodeMirrors = function() {
    this.tcm = this.createSubmissionMirror();

    if (this.isEditor) {
        this.tcm.setNewFileOptions({
            'name': 'NewFile.java',
            'code': '',
            'mode': this.getCmMode(),
            'theme': user_theme,
        });
        this.tcm.setForcedFileExtension('java');
        this.tcm.enableTabEditingWidgets();
    }
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._showEditorTraceDialog = function() {
    this.visualizer.setFiles(this.tcm.getFiles());
    var that = this;
    this.visualizer.setCompileErrorCallback(function(file, line, message) {
        that.displayCodeError(file, line, message);
    });
    this.visualizer.loadVisualizer();
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype.getAllCode = function() {
    var hash = CryptoJS.SHA1(this.problemId);
    return this.tcm.getHashedCode(hash);
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
    /*
     * In PCRS-Java, a single exception means a compile error occured,
     * knocking down the entire test stack. So we want to hide the test table.
     */
    if (testData.testcases.length > 0 && testData.testcases[0].exception) {
        testData.error_msg = testData.testcases[0].exception;
    }

    SubmissionWrapper.prototype.prepareGradingTable.apply(this, arguments);
    var $gradingTable = this.wrapperDiv.find("#gradeMatrix");

    this.lastSubmissionPk = testData['sub_pk'];
    this._injectVisualizationButton($gradingTable);

    if (testData.error_msg) {
        $gradingTable.find('.pcrs-table-head-row').hide();
        this.wrapperDiv.find('#visualizeButton').hide();
    } else {
        $gradingTable.find('.pcrs-table-head-row').show();
        this.wrapperDiv.find('#visualizeButton').show();
    }
    this.tcm.markClean();
}

/**
 * If it doesn't already exist, injects a visualizer button to the given table.
 */
JavaSubmissionWrapper.prototype._injectVisualizationButton = function($table) {
    if (this.wrapperDiv.find('#visualizeButton').length > 0) {
        return;
    };
    var that = this;
    $table.before(
        $('<a id="visualizeButton" class="btn btn-info" role="button"></a>')
            .text('Visualize')
            .click(function() {
                that._visualizeHistoryEntryPk(that.lastSubmissionPk);
            }));
}

/**
 * @override
 */
JavaSubmissionWrapper.prototype._addHistoryEntryButtons =
        function($row, entry) {
    SubmissionWrapper.prototype._addHistoryEntryButtons.apply(this, arguments);

    var that = this;
    $row.find('#buttonArea').append(
        $('<a class="btn btn-info" role="button"></a>')
            .text('Visualize')
            .click(function() {
                that._visualizeHistoryEntryPk(entry['sub_pk']);
            }));
}

/**
 * Jumps to the visualizer for the given submission history entry.
 */
JavaSubmissionWrapper.prototype._visualizeHistoryEntryPk = function(entryPk) {
    // Open it in a new tab
    window.open(root + '/editor/java/visualize/' + entryPk, '_blank');
}

/**
 * Highlights the given line and displays the given error message.
 *
 * @param file {string}
 * @param line {number} zero-indexed
 */
JavaSubmissionWrapper.prototype.displayCodeError = function(file, line,
        message) {
    var $alertBox = this.wrapperDiv.find('#alert');
    $alertBox.show();
    $alertBox.toggleClass('red-alert', true);
    $alertBox.children('icon').toggleClass('remove-icon', true);
    $alertBox.children('span').text(message);
    this.wrapperDiv.find('.screen-reader-text').text(message);

    // Not an error with a specific file.
    if (file == '') {
        return;
    }

    var tabIndex = this.tcm.indexForTabWithName(file);
    var mirror = this.tcm.getCodeMirror(tabIndex);
    this.tcm.setActiveTabIndex(tabIndex);

    var errorClass = 'CodeMirror-error-background';
    // highlight the faulting line in the current file
    mirror.focus();
    mirror.setCursor(line, 0);
    mirror.addLineClass(line, '', errorClass);

    var that = this;
    var changeHandler = function() {
        // Reset line back to normal
        mirror.removeLineClass(line, '', errorClass);
        mirror.off('change', changeHandler);
        that.wrapperDiv.find('#alert').hide();
    }
    mirror.on('change', changeHandler);
}

