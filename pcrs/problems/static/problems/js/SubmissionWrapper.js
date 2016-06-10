function SubmissionWrapper(wrapperDivId) {
    this.wrapperDivId = wrapperDivId;
    this.wrapperDiv = $('#' + wrapperDivId);
    this.problemId = wrapperDivId.split("-")[1];
    // I don't like this... it should be a sub class.
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
    this.wrapperDiv.find("[name='history']").one("click", (function() {
        // FIXME: Show multiple files / tabs in Java wrappers.
        getHistory(that.wrapperDivId);
    }));

    this.wrapperDiv.children('#grade-code').hide();
    this.createCodeMirrors();
}

SubmissionWrapper.prototype.createCodeMirrors = function() {
    var submissionDiv = this.wrapperDiv.find("#div_id_submission");
    myCodeMirrors[this.wrapperDivId] = to_code_mirror(
        this.language, this.language_version,
        submissionDiv, submissionDiv.text(), false);
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

SubmissionWrapper.prototype.getTestcases = function(code) {
    var call_path = "";

    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' + this.wrapperDivId.split("-")[1]+ '/run';
    }

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

    var use_gradetable = ( ! this.isEditor) || this.language == 'ra' || this.language == 'sql';
    // use_simpleui is global... gur.
    if (use_simpleui == 'False' && use_gradetable) {
        this.wrapperDiv.find("#grade-code").show();
    }

    var score = data['score'];
    var max_score = data['max_score'];
    var decider = score == max_score;

    if ( ! this.isEditor) {
        var $alertBox = this.wrapperDiv.find('#alert');

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
            this.wrapperDiv.find('.screen-reader-text').text(resultText);
        }
    }

    // FIXME ugly global variables right now.
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

SubmissionWrapper.prototype.prepareGradingTable = function() {}

/**
 * Retrieves the lumped code for submitting.
 *
 * If your code wrapper has tags, include them here.
 */
SubmissionWrapper.prototype.getAllCode = function() {
    return myCodeMirrors[this.wrapperDivId].getValue();
}

