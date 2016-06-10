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
    highlightCodeMirrorWithTags(mirror, codeObj.blocked_ranges);
    preventDeleteLastLine(mirror);
}

/**
 * @override
 */
CSubmissionWrapper.prototype.getAllCode = function() {
    var hash = CryptoJS.SHA1(this.problemId);
    return TabbedCodeMirror._getHashedCodeFromMirror(
        myCodeMirrors[this.wrapperDivId], hash);
}

/**
 * @override
 */
CSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    var testcases = testData['testcases'];
    // Handle compilation error and warning messages
    var dont_visualize = handleCompileMessages(this.wrapperDivId, testcases);

    if (this.isEditor) {
        /*
         * If it's the editor, start calling
         * visualizer functions now so long as no errors exist.
         */
        if ( ! dont_visualize) {
            getVisualizerComponents(code, "", 9999999);
        }
        return;
    }

    prepareGradingTableLegacy(this.wrapperDivId,
                        testData['best_score'],
                        testData['past_dead_line'],
                        testData['sub_pk'],
                        testData['max_score']);
}

