function RASubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "ra";
    this.language_version = 'text/x-sql';
}
RASubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
RASubmissionWrapper.prototype.constructor = RASubmissionWrapper;

/**
 * @override
 */
RASubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    SQLSubmissionWrapper.prototype.prepareGradingTable.apply(this, arguments);
}

/**
 * @override
 */
RASubmissionWrapper.prototype._shouldUseGradeTable = function() {
    SQLSubmissionWrapper.prototype._shouldUseGradeTable.apply(this, arguments);
}

