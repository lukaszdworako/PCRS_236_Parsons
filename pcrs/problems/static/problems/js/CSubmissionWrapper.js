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
CSubmissionWrapper.prototype.getTestcases = function(code) {
    SubmissionWrapper.prototype.getTestcases.apply(this, arguments);
    // For the debugger
    document.getElementById('feedback_code').value = code;
}

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
    highlightCodeMirrorWithTags(mirror, codeObj.block_ranges);
    preventDeleteLastLine(mirror);
}

/**
 * @override
 */
CSubmissionWrapper.prototype.getAllCode = function() {
    return this._addHashkey(myCodeMirrors[this.wrapperDivId]);
}

/**
 * @override
 */
CSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    if (this.isEditor) {
        var testcases = testData['testcases'];
        // Handle compilation error and warning messages
        var shouldVisualize = this._handleCompileMessages(testcases);
        /*
         * If it's the editor, start calling
         * visualizer functions now so long as no errors exist.
         */
        if (shouldVisualize) {
            getVisualizerComponents(code, '', 9999999);
        }
        return;
    }

    SubmissionWrapper.prototype.prepareGradingTable.apply(this, arguments);
}

/**
 * Handle error and warning messages.
 *
 * Errors will be highlighted in red.
 * Warnings will be highlighted in yellow.
 */
CSubmissionWrapper.prototype._handleCompileMessages = function(testcases) {
    // Handle C warnings and exceptions
    this.wrapperDiv.find('#c_warning').remove();
    this.wrapperDiv.find('#c_error').remove();

    // Find testcase with warning/error
    var bad_testcase = null;
    for (var i = 0; i < testcases.length; i++) {
        if ("exception_type" in testcases[i]) {
            bad_testcase = testcases[i];
            break;
        }
    }

    var shouldVisualize = true;

    if (bad_testcase != null) {
        var class_type;
        if (bad_testcase.exception_type == "warning") {
            class_type = 'alert alert-warning';
        } else if (bad_testcase.exception_type == "error") {
            class_type = 'alert alert-danger';
            shouldVisualize = false;
        }

        var bad_testcase_message = "";
        if ("exception" in bad_testcase) {
            bad_testcase_message = bad_testcase.exception;
        } else if ("runtime_error" in bad_testcase) {
            bad_testcase_message = "Runtime error for input '" +
                bad_testcase.test_input +
                "':<br/>" + bad_testcase.runtime_error;
        }

        this.wrapperDiv
            .find('#alert')
            .after('<div id="c_warning" class="' +
                class_type + '" style="font-weight: bold">' +
                bad_testcase_message + '</div>');
    }

    // The grade table clutters up the interface when we have compile errors
    if (shouldVisualize) {
        $('#gradeMatrix').show();
    } else {
        $('#gradeMatrix').hide();
    }

    return shouldVisualize;
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
    var newCode = this._addHashkey(myCodeMirrors[this.wrapperDivId]);
    getVisualizerComponents(newCode, testcaseCode, this.problemId);
}

/**
 * Generate a Hashkey based on the problem_id to identify
 * where the student code starts and ends.
 */
CSubmissionWrapper.prototype._addHashkey = function(mirror) {
    var hashCode = CryptoJS.SHA1(this.problemId);
    var code = '';
    var inside_student_code = false;

    for (var i = 0; i < mirror.lineCount(); i++){
        var wrapClass = mirror.lineInfo(i).wrapClass;

        if (wrapClass == 'CodeMirror-activeline-background') {
            if (inside_student_code) {
                code += hashCode + '\n';
                inside_student_code = false;
            }
        } else {
            if ( ! inside_student_code) {
                code += hashCode + '\n';
                inside_student_code = true;
            }
        }

        code += mirror.getLine(i);
        code += '\n';
    }
    code += hashCode;
    return code;
}

