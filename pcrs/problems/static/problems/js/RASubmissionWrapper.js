function RASubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "ra";
    this.language_version = 'text/x-sql';
}
RASubmissionWrapper.prototype = Object.create(SQLSubmissionWrapper.prototype);
RASubmissionWrapper.prototype.constructor = RASubmissionWrapper;

/**
 * @override
 */
RASubmissionWrapper.prototype.createCodeMirrors = function() {
    SQLSubmissionWrapper.prototype.createCodeMirrors.apply(this, arguments);

    if (this.isEditor) {
        var mirror = this.tcm.getCodeMirror(0);
        mirror.getDoc().setValue("\\project_{eid} sales;");
    }
}

