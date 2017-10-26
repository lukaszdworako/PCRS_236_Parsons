function SubmissionWrapper(wrapperDivId) {
    this.wrapperDivId = wrapperDivId;
    this.wrapperDiv = $('#' + wrapperDivId);
    this.submissionHistory = [];
    // If this is in a visualizer code editor
    this.isEditor = this.wrapperDivId.split("-")[2] === 'editor';
    this.problemId = this.isEditor ? '9999999' : wrapperDivId.split("-")[1];
    // Null is evil, but these MUST be changed in the subclass constructors.
    this.language = null;
    this.language_version = null;
}

SubmissionWrapper.prototype.getCmMode = function() {
    return cmModeForLanguageAndVersion(this.language, this.language_version);
}

/**
 * Factory method for creating language-specific submission wrappers.
 */
SubmissionWrapper.createWrapperFromDivId = function(wrapperDivId) {
    if (wrapperDivId.indexOf("c-") > -1) {
        return new CSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("python-") > -1) {
        return new PythonSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("java-") > -1) {
        return new JavaSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("sql-") > -1) {
        return new SQLSubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("ra-") > -1) {
        return new RASubmissionWrapper(wrapperDivId);
    } else if (wrapperDivId.indexOf("r-") > -1) {
        return new RSubmissionWrapper(wrapperDivId);
    }
}

SubmissionWrapper.prototype.pageLoad = function() {
    var that = this;
    if (this.isEditor) {
        this.wrapperDiv.find('#submit-id-trace').click(function(event) {
            event.preventDefault();
            var code = that.getAllCode();

            if (code == '') {
                alert('There is no code to submit.');
                return;
            }

            that._showEditorTraceDialog();
        });
    } else {
        this.wrapperDiv.find('#submit-id-submit').click(function(event) {
            event.preventDefault();
            that.submitAllCode();
        });
        this.wrapperDiv.find("[name='history']").click(function() {
            that.loadAndShowHistory();
        });
    }

    this.wrapperDiv.children('#grade-code').hide();
    this.createCodeMirrors();
}

SubmissionWrapper.prototype.createCodeMirrors = function() {
    throw new Error('This method must be overridden');
}

// TODO: Replace createCodeMirrors with this!
// Eventually, every language should use a submission tabbed code mirror.
// At that point, tcm should be a property of all SubmissionWrappers
SubmissionWrapper.prototype.createSubmissionMirror = function() {
    var tcm = new SubmissionTabbedCodeMirror();
    tcm.setNewFileOptions({
				'name': 'NewFile.' + this.language,
				'code': '',
        'mode': this.getCmMode(),
        'theme': user_theme, // global... gur
    });

    var $submissionDiv = this.wrapperDiv.find(this.isEditor
        ? '#div_id_code_box' : '#div_id_submission');

    var code = $submissionDiv.find('textarea').text();
    tcm.addFilesFromTagText(code);

    // Replace the code div with the tabbed code mirror
    $submissionDiv.before(tcm.getJQueryObject());
    $submissionDiv.remove();

    if ( ! this.isEditor) {
        // Prevent users from obliterating changes accidentally.
        $(window).bind('beforeunload', function() {
            if ( ! tcm.isClean()) {
                return 'You have unsubmitted changes.';
            }
        });
    }

    return tcm;
}

SubmissionWrapper.prototype._showEditorTraceDialog = function() {
    var code = this.getAllCode();
    this.getTestcases(code);
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

/**
 * Submit the current code and populate the grade table.
 */
SubmissionWrapper.prototype.getTestcases = function(code) {
    var call_path = "";
    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' +
            this.wrapperDivId.split("-")[1]+ '/run';
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

SubmissionWrapper.prototype._shouldUseGradeTable = function() {
    return ! this.isEditor;
}

SubmissionWrapper.prototype._getTestcasesCallback = function(data) {
    if (data['past_dead_line']) {
        alert("This submission is past the deadline!")
        this.wrapperDiv.find('#deadline_msg').remove();
        this.wrapperDiv.find('#alert').after(
            '<div id="deadline_msg" class="red-alert">' +
            'Submitted after the deadline!<div>');
    }

    // use_simpleui is global... gur.
    if (use_simpleui == 'False' && this._shouldUseGradeTable()) {
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

    if (error_msg) {
        $gradingTable.append($('<th class="red-alert"></th>')
            .attr('style', 'width:100%;')
            .attr('colspan', '12')
            .html(error_msg));
        return;
    }

    //PyTA
    lastCase = testcases[testcases.length - 1]
    if (testcases.length > 0 && lastCase.hasOwnProperty("PyTA")) {
        this.wrapperDiv.find("[id^=PyTADropdown]").remove();
        this._createPyTADropdown(lastCase);
        testcases.splice(testcases.length-1, 1);
        if (lastCase.passed_test) {
            this.wrapperDiv.find("[id^=PyTADropdown]").hide()
        }
    }

    this._addTestCasesToTable(testcases, $gradingTable);

    if (best && ! past_dead_line) {
        var score = this._calculateSubmissionScore(testcases);
        update_marks(this.wrapperDivId, score, max_score);
    }
}

SubmissionWrapper.prototype._addTestCasesToTable = function(testcases,
        $gradingTable) {
    for (var i = 0; i < testcases.length; i++) {
        var testcase = this._formatTestCaseObject(testcases[i]);
        var $newRow = this._createTestCaseRow(testcase);
        $gradingTable.append($newRow);
    }
}

SubmissionWrapper.prototype._calculateSubmissionScore = function(testcases) {
    var score = 0;
    for (var i = 0; i < testcases.length; i++) {
        if (testcases[i].passed_test) {
            score++;
        }
    }
    return score;
}

SubmissionWrapper.prototype._formatTestCaseObject = function(testcase) {
    if (testcase.test_desc == '') {
        testcase.test_desc = "No Description Provided"
    }
    return testcase;
}

/**
 * Retrieves the lumped code for submitting.
 *
 * If your code wrapper has tags, include them here.
 */
SubmissionWrapper.prototype.getAllCode = function() {
    throw new Error('This method must be overridden');
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
        $newRow.append($('<th class="red-alert" colspan="12"></th>')
            .attr('style', 'width: 100%;')
            .append("<code>" + testcase.exception + "</code>"));
    }

    return $newRow;
}

/**
 * Adds a status smiley/frowney face to a test row.
 */
SubmissionWrapper.prototype._addFaceColumnToTestRow = function($row, passed) {
    var $face = $('<img>').attr({
        src: passed ? happyFaceURL : sadFaceURL, // Globals :|
        alt: passed ? 'Smiley Face' : 'Sad Face',
        height: '36',
        width: '36',
    });
    $row.append($('<td class="passed"></td>').append($face));
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
                that._prepareVisualizer($row);
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

    var problem_path = root + '/problems/' + this.language + '/' +
        this.problemId + '/history';
    var that = this;
    $.post(problem_path, postParams,
        function(data) {
            that.setHistoryEntries(data);
            that.showHistoryModal();
        }, 'json')
        .fail(function(jqXHR, textStatus, errorThrown) {
            alert('Failed fetching history. Please try again.');
            console.log(textStatus);
        });
}

/**
 * Show the history modal with the given entries.
 */
SubmissionWrapper.prototype.showHistoryModal = function(entries) {
    $('#history_window_' + this.wrapperDivId).modal('show');
}

/**
 * Set's the history.
 *
 * @param entries {array} The history entries.
 * @see _addHistoryEntryToAccordion for entry format
 */
SubmissionWrapper.prototype.setHistoryEntries = function(entries) {
    this.submissionHistory = entries;

    var $historyDiv = $('#history_window_' + this.wrapperDivId);
    var $accordion = $historyDiv.find('#history_accordion');
    // Delete the old
    $accordion.empty();
    // Add the new
    for (var x = 0; x < entries.length; x++) {
        this._addHistoryEntryToAccordion(entries[x], $accordion);
    }
}

/**
 * Add the given entry to the specified history accordion.
 *
 * @param entry {object}
 * @param $accordion {object} A jQuery accordion object
 */
SubmissionWrapper.prototype._addHistoryEntryToAccordion = function(entry,
        $accordion) {
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

    var mirrorId = 'history_mirror_' + entry['problem_pk'] + '_' +
        entry['sub_pk'];

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
    };

    var $row = $(template(config));
    $accordion.append($row);

    var tcm = this._createHistoryCodeMirror(entry);
    $("#" + mirrorId).replaceWith(tcm.getJQueryObject());

    $row.find('a.pcrs-panel-title').click(function() {
        // Wait for the accordion to expand before rendering. Ugly, I know :(
        setTimeout(function () {
            tcm.refresh()
        }, 1);
    });

    this._addHistoryEntryButtons($row, entry);
}

SubmissionWrapper.prototype._addHistoryEntryButtons = function($row, entry) {
    var that = this;
    $row.find('#buttonArea').append(
        $('<a class="btn btn-danger" role="button"></a>')
            .text('Revert')
            .click(function() {
                that._revertToCodeFromHistoryModal(entry.submission);
            }));
}

SubmissionWrapper.prototype._createHistoryCodeMirror = function(entry) {
    var tcm = new SubmissionTabbedCodeMirror();

    tcm.setNewFileOptions({
        'readOnly': true,
        'mode': this.getCmMode(),
        'theme': user_theme, // global... gur
    });
    tcm.addFilesFromTagText(entry.submission);

    return tcm;
}

SubmissionWrapper.prototype._revertToCodeFromHistoryModal = function(code) {
    /*
     * This can't be a modal confirmation since the history modal is
     * already being shown. Bootstrap doesn't support multiple modals being
     * open at the same time.
     */
    if ( ! confirm('Revert current code to this submission?')) {
        return;
    }

    this.tcm.addFilesFromTagText(code);

    var $historyDiv = $('#history_window_' + this.wrapperDivId);
    $historyDiv.modal('hide');
    this.wrapperDiv.find('#grade-code').hide();
    this.wrapperDiv.find('#alert').hide();
}
