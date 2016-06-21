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

/**
 * @override
 */
RASubmissionWrapper.prototype.createCodeMirrors = function() {
    SubmissionWrapper.prototype.createCodeMirrors.apply(this, arguments);

    if (this.isEditor) {
        var mirror = myCodeMirrors[this.wrapperDivId];
        mirror.getDoc().setValue("\\project_{eid} sales;");
    }
}

