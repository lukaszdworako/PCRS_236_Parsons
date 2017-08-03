function PythonSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "python";
    this.language_version = 3;
    this.visualizer = new PythonVisualizer();
    this.visualizer.setProblemId(this.problemId);
    this.tcm = null; // Set in createCodeMirrors (on page load)
}
PythonSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
PythonSubmissionWrapper.prototype.constructor = PythonSubmissionWrapper;

/**
 * @override
 */
PythonSubmissionWrapper.prototype._showEditorTraceDialog = function(code) {
    var code = this.tcm.getCodeMirror(0).getDoc().getValue();
    if (code) {
        this.visualizer.setCode(code);
        this.visualizer.loadVisualizer();
    } else {
        alert('Please enter some code before visualizing');
    }
}

/**
 * @override
 */
PythonSubmissionWrapper.prototype.getAllCode = function() {
    var hash = CryptoJS.SHA1(this.problemId);
    return this.tcm.getHashedCode(hash);
}

/**
 * @override
 */
PythonSubmissionWrapper.prototype.createCodeMirrors = function() {
    this.tcm = this.createSubmissionMirror();
}

function getPyTAClickEvent() {
    $.post("/problems/python/pyta");
}

PythonSubmissionWrapper.prototype._createPyTADropdown = function(testcase) {
    this.wrapperDiv.find('#gradeMatrix').before('<div class="dropdown" id="PyTADropdown" onclick="getPyTAClickEvent()" style="width:100%;"><button class="btn dropdown-toggle" type="button" data-toggle="dropdown" style="width:100%;background-color:#a94442;border-color:#ebccd1;color:#f2dede;margin-bottom:5px;">Expand for Detailed Error Message <span class="caret"></span></button><ul class="dropdown-menu" style="width:100%;position:relative;margin-bottom:5px;top:-6px;padding:0;box-shadow:none;"><li class="red-alert" style="width:100%;margin:0px;">' + testcase.test_val + '</li></ul></div>');    
}

/**
 * @override
 */
PythonSubmissionWrapper.prototype._createTestCaseRow = function(testcase) {
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

    var expTestValDiv = $('<div class="ExecutionVisualizer"></div>');
    var testResultDiv = $('<div class="ExecutionVisualizer"></div>');

    $newRow.append($('<td class="expected"></td>')
        .append($('<div class="ptd"></div>')
            .append(expTestValDiv)));
    $newRow.append($('<td class="result"></td>')
        .append($('<div class="ptd"></div>')
            .append(testResultDiv)));

    renderData_ignoreID(testcase.test_val, testResultDiv);
    renderData_ignoreID(testcase.expected_output, expTestValDiv);

    this._addFaceColumnToTestRow($newRow, testcase.passed_test);
    this._addDebugColumnToTestRow($newRow, testcase.debug);
    this._addA11yToTestRow($newRow,
        this._accessibilityOutput(testcase.test_val),
        testcase.passed_test,
        this._accessibilityOutput(testcase.expected_output));

    return $newRow;
}

/**
 * @override
 */
PythonSubmissionWrapper.prototype._prepareVisualizer = function(row) {
    var testcaseCode = row.find(".expression_div").text();
    var code = this.tcm.getValue() + '\n' + testcaseCode;

    this.visualizer.setCode(code);
    this.visualizer.loadTestCaseVisualizer(testcaseCode);
}

/**
 * Convert the given "input" in to a string representing the
 * students python solution.
 */
PythonSubmissionWrapper.prototype._accessibilityOutput = function(input) {
    var brakets_o = {"list":"[","tuple":"(","dict":"{"};
    var brakets_c = {"list":"]","tuple":")","dict":"}"};

    if (input.length == 2) {
        return this._accessibilityOutput(
            input[0]) + ":" + this._accessibilityOutput(input[1]);
    } else if (input[0] == "list" || input[0] == "tuple" || input[0] == "dict") {
        var output = brakets_o[input[0]];
        for (var o_index = 2; o_index < input.length; o_index++) {
            output += this._accessibilityOutput(input[o_index]);
            if (o_index != input.length - 1) {
                output += ", ";
            }
        }
        output += brakets_c[input[0]];
        return output
    } else if (input[0] == "string") {
        return "'" + input[2] + "'";
    } else if(input[0] == "float") {
        if (String(input[2]).indexOf(".") > -1) {
            return input[2];
        } else {
            return input[2] + ".0"
        }
    } else {
        return input[2]
    }
}

