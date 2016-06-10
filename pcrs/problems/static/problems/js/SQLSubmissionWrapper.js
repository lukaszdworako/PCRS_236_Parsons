function SQLSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "sql";
    this.language_version = "text/x-sql";
}
SQLSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
SQLSubmissionWrapper.prototype.constructor = SQLSubmissionWrapper;

/**
 * @override
 */
SQLSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    prepareSqlGradingTableLegacy(this.wrapperDivId,
                           testData['best'],
                           testData['past_dead_line'],
                           testData['sub_pk'],
                           testData['max_score'],
                           this.isEditor);
}

