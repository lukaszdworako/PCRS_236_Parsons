function SubmissionWrapper(wrapperDivId) {
    this.wrapperDivId = wrapperDivId;
    this.wrapperDiv = $('#' + wrapperDivId);
    this.problemId = wrapperDivId.split("-")[1];
    // FIXME I don't like the isEditor property...
    // If this is in a visualizer code editor
    this.isEditor = this.wrapperDivId.split("-")[2];
    // Null is evil, but these MUST be changed in the subclass constructors.
    this.language = null;
    this.language_version = null
}

/**
 * Factory method for creating language-specific submission wrappers.
 */
SubmissionWrapper.createWrapperFromDivId = function(wrapperDivId) {
    if (wrapperDivId.indexOf("c-") > -1){
        return new CSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("python-") > -1){
        return new PythonSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("java-") > -1){
        return new JavaSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("sql-") > -1){
        return new SQLSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("ra-") > -1){
        return new RASubmissionWrapper(wrapperDivId);
    }
}

SubmissionWrapper.prototype.pageLoad = function() {
    var that = this;
    this.wrapperDiv.find('#submit-id-submit').click(function(event) {
        event.preventDefault();
        that.submitAllCode();
    });
    this.wrapperDiv.find("[name='history']").click(function() {
        that.loadAndShowHistory();
    });

    this.wrapperDiv.children('#grade-code').hide();
    this.createCodeMirrors();
}

SubmissionWrapper.prototype.createCodeMirrors = function() {
    var $submissionDiv = this.wrapperDiv.find("#div_id_submission");
    myCodeMirrors[this.wrapperDivId] = to_code_mirror(
        this.language, this.language_version,
        $submissionDiv, $submissionDiv.text(), false);
}

SubmissionWrapper.prototype.submitAllCode = function() {
    var code = this.getAllCode();
    if (code == '') {
        alert('There is no code to submit.');
    } else {
        // Replace all the tabs with 4 spaces before submitting
        code = code.replace(/\t/g, '    ');
        this.getTestcases(code);
    }
}

// FIXME this is called in editor.js.

/**
 * Submit the current code and populate the grad table.
 */
SubmissionWrapper.prototype.getTestcases = function(code) {
    var call_path = "";

    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' + this.wrapperDivId.split("-")[1]+ '/run';
    }

    // FIXME nuuuu not language checks!
    // Not including java yet, since debugger is not implemented
    if (this.language == 'c') {
        document.getElementById('feedback_code').value = code;
    }

    var postParams = { csrftoken: csrftoken, submission: code };

    // Activate loading pop-up
    $('#waitingModal').modal('show');

    var that = this;
    $.post(call_path,
            postParams,
            function(data) {
                that._getTestcasesCallback(data);
                // Deactivate loading pop-up
                $('#waitingModal').modal('hide');
            },
        "json")
     .fail(
        function(jqXHR, textStatus, errorThrown) {
            // Deactivate loading pop-up
            $('#waitingModal').modal('hide');
        });
}

SubmissionWrapper.prototype._getTestcasesCallback = function(data) {
    if (data['past_dead_line']) {
        alert("This submission is past the deadline!")
        this.wrapperDiv.find('#deadline_msg').remove();
        this.wrapperDiv.find('#alert').after(
            '<div id="deadline_msg" class="red-alert">' +
            'Submitted after the deadline!<div>');
    }

    // FIXME rats nest
    var use_gradetable = ( ! this.isEditor) || this.language == 'ra' || this.language == 'sql';
    // use_simpleui is global... gur.
    if (use_simpleui == 'False' && use_gradetable) {
        this.wrapperDiv.find("#grade-code").show();
    }

    var score = data['score'];
    var max_score = data['max_score'];

    if ( ! this.isEditor) {
        var $alertBox = this.wrapperDiv.find('#alert');
        $alertBox.show();
        var decider = score == max_score;

        $alertBox.toggleClass("red-alert", ! decider);
        $alertBox.toggleClass("green-alert", decider);
        $alertBox.children('icon').toggleClass("remove-icon", ! decider);
        $alertBox.children('icon').toggleClass("ok-icon", decider);

        if (decider) {
            $alertBox.children('span').text("Your submission is correct!");

            this.wrapperDiv
                .find('.screen-reader-text')
                .prop('title', 'Your solution is correct!');
        } else {
            var resultText = "Your solution passed " +
                score + " out of " + max_score + " cases!";

            $alertBox.children('span').text(resultText);
            this.wrapperDiv.find('.screen-reader-text').prop(resultText);
        }
    }

    // FIXME ugly global variables
    error_msg = data['results'][1];
    testcases = data['results'][0];

    this.prepareGradingTable({
        'testcases': data['results'][0],
        'best_score': data['best'],
        'max_score': max_score,
        'past_dead_line': data['past_dead_line'],
        'sub_pk': data['sub_pk'],
        'error_msg': data['results'][1] || null,
    });
}

/**
 * Display the results of the SQL and RA test cases
 *
 * @param testData.best_score {number} The users best score
 * @param testData.max_score {number} The maximum possibly score
 * @param testData.past_dead_line {boolean} If it is past the problem deadline
 * @param testData.sub_pk {number} The Primary Key of the submission
 */
SubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    var div_id = this.wrapperDivId;
    var best = testData['best_score'];
    var past_dead_line = testData['past_dead_line'];
    var sub_pk = testData['sub_pk'];
    var max_score = testData['max_score'];
    var error_msg = testData['error_msg'];
    var testcases = testData['testcases'];

    var $gradingTable = this.wrapperDiv.find("#gradeMatrix");
    $gradingTable.find(".red-alert").remove();
    $gradingTable.find('.pcrs-table-row').remove();

    var score = 0;
    var tests = [];

    if (error_msg != null) {
        $gradingTable.append($('<th class="red-alert"></th>')
            .attr('style', 'width:100%;')
            .attr('colspan', '12')
            .text(error_msg));
    } else {
	    for (var i = 0; i < testcases.length; i++) {
            var testcase = testcases[i];
            if (testcase.test_desc == '') {
                testcase.test_desc = "No Description Provided"
            }
            // FIXME this should only be in PCRS-Python, no?
            testcase.expected_output = testcase.expected_output
                ? create_output(testcase.expected_output)
                : null;

            tests.push({
                'visible': testcase.test_input != null,
                'input': testcase.test_input,
                'output': testcase.expected_output,
                'passed': testcase.passed_test,
                'description': testcase.test_desc
            });

            if (testcase.passed_test) {
                score++;
            }

            var $newRow = this._createTestCaseRow(testcase);
            $gradingTable.append($newRow);
	    }
    }

    // FIXME somehow, show the tabs.

    var historyData = {
        'sub_time':new Date(),
        'submission': this.getAllCode(),
        'score':score,
        'best':best,
        'past_dead_line':past_dead_line,
        'problem_pk':this.problemId,
        'sub_pk':sub_pk,
        'out_of':max_score,
        'tests': tests
    };

    if (best && ! past_dead_line) {
        update_marks(this.wrapperDivId, score, max_score);
    }
}

/**
 * Retrieves the lumped code for submitting.
 *
 * If your code wrapper has tags, include them here.
 */
SubmissionWrapper.prototype.getAllCode = function() {
    return myCodeMirrors[this.wrapperDivId].getValue();
}

/**
 * Create a test case row for the grading table.
 *
 * Note that this will create simple row initially - child classes add content.
 */
SubmissionWrapper.prototype._createTestCaseRow = function(testcase) {
    var div_id = this.wrapperDivId;
    var $newRow = $('<tr class="pcrs-table-row"></tr>');

    if ("exception" in testcase) {
        $newRow.append('<th class="red-alert" colspan="12" style="width:100%;">' +
            testcase.exception + '</th>');
    }

    return $newRow;
}

/**
 * Adds a status smiley/frowney face to a test row.
 */
SubmissionWrapper.prototype._addFaceColumnToTestRow = function($row, passed) {
    var smFace = passed ? happyFace : sadFace;
    $row.append($('<td class="passed"></td>').html(smFace.clone()));
}

/**
 * Adds accessibility test results to a test row.
 */
SubmissionWrapper.prototype._addA11yToTestRow = function($row, result, passed,
        expected) {
    var pass_status = passed ? 'passed' : 'failed'
    $row.append('<a class="at" href="">This testcase has ' + pass_status +
        '. Expected: ' + expected +
        '. Result: ' + result + '</a>');
}

/**
 * Adds a debug button column to the test row.
 *
 * @see _prepareVisualizer
 */
SubmissionWrapper.prototype._addDebugColumnToTestRow = function($row, debug) {
    if (debug) {
        var $button = $('<button class="debugBtn" type="button"></button>')
            .attr('data-toggle', 'modal')
            .attr('data-target', '#visualizerModal')
            .text('Trace');
        $row.append($('<td class="debug"></td>').append($button));

        var that = this;
        $button.bind('click', function() {
            setTimeout(function() {
                $('#waitingModal').modal('show');
                that._prepareVisualizer($row);
                $('#waitingModal').modal('hide');
            }, 250);
        });
    } else {
        // Test cases that don't allow debugging.
        $row.append('<td class="debug">-</td>')
    }
}

/**
 * Prepare coding problem visualizer.
 *
 * This does nothing by default - interesting things happen in subclasses.
 */
SubmissionWrapper.prototype._prepareVisualizer = function(row) {
}

/**
 * Get submission history for a coding problem based on id of the problem.
 */
SubmissionWrapper.prototype.loadAndShowHistory = function() {
    var postParams = {
        csrftoken: csrftoken
    };

    // Empty the accordion, in case any manual insertions were performed.

    var problem_path = root + '/problems/' + this.language + '/' + this.problemId +'/history';
    var that = this;
    $.post(problem_path, postParams,
        function(data) {
            that.showHistoryModal(data);
        }, 'json')
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus);
        });
}

/**
 * Show the history modal with the given entries.
 */
SubmissionWrapper.prototype.showHistoryModal = function(entries) {
    var $historyDiv = $('#history_window_' + this.wrapperDivId);
    var $accordion = $historyDiv.find('#history_accordion');
    // Delete the old
    $accordion.empty();
    // Add the new
    for (var x = 0; x < entries.length; x++) {
        this._addHistoryEntry(entries[x], $accordion);
    }
}

/**
 * Add "data" to the history inside the given "div_id"
 */
SubmissionWrapper.prototype._addHistoryEntry = function(entry, $accordion) {
    var sub_time = new Date(entry['sub_time']);
    var panel_class = "pcrs-panel-default";
    var star_text = "";

    sub_time = jsDateTimeToPCRSDatetime(sub_time);

    if (entry['past_dead_line']) {
        panel_class = "pcrs-panel-warning";
        sub_time = sub_time + " Submitted after the deadline";
    }
    if (entry['best'] && ! entry['past_dead_line']) {
        panel_class = "pcrs-panel-star";
    }

    var mirrorId = 'history_mirror_' + entry['problem_pk'] + '_' + entry['sub_pk'];
    var template = Handlebars.getTemplate('hb_history_row');
    var config = {
        panelClass: panel_class,
        problemPk:  entry['problem_pk'],
        subPk:      entry['sub_pk'],
        title:      sub_time,
        score:      entry['score'],
        maxScore:   entry['out_of'],
        isBest:     entry['best'] && ! entry['past_dead_line'],
        testcases:  entry['tests'],
        mirrorId:   mirrorId,
        submission: entry['submission'],
    };

    $accordion.append(template(config));
    this._createHistoryCodeMirror(mirrorId);
}

SubmissionWrapper.prototype._createHistoryCodeMirror = function(mirrorId) {
    create_to_code_mirror(this.language, this.language_version, mirrorId);
}

