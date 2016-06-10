function PythonSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "python";
    this.language_version = 3;
}
PythonSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
PythonSubmissionWrapper.prototype.constructor = PythonSubmissionWrapper;

/**
 * @override
 */
PythonSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    prepareGradingTableLegacy(this.wrapperDivId,
                        testData['best_score'],
                        testData['past_dead_line'],
                        testData['sub_pk'],
                        testData['max_score']);
}

