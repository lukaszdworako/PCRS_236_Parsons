/**
 * Parent Visualizer class to handle loading and displaying visualizers.
 */
function Visualizer() {
    this.problemId = 9999999; // Editor id
    // This must be set in subclasses
    this.language = null;
    this.code = '';
}

Visualizer.prototype.setProblemId = function(problemId) {
    this.problemId = problemId;
}

/**
 * Sets the code to use when loading the visualization.
 */
Visualizer.prototype.setCode = function(code) {
    this.code = code;
}

/**
 * Loads a visualizer with the current code.
 */
Visualizer.prototype.loadVisualizer = function() {
    var postParams = this._generatePostParams();
    this._loadVisualizerWithPostParams(postParams);
}

/**
 * Loads the visualizer in testcase mode.
 */
Visualizer.prototype.loadTestCaseVisualizer = function(testcaseCode) {
    var postParams = this._generatePostParams();
    postParams.test_case = testcaseCode;
    this._loadVisualizerWithPostParams(postParams);
}

Visualizer.prototype._loadVisualizerWithPostParams = function(postParams) {
    $('#waitingModal').modal('show');
    var url = root + 'problems/' + this.language + '/visualizer-details';
    var that = this;
    $.post(url, postParams, function(data) {
            that._showVisualizerWithData(data);
            $('#waitingModal').modal('hide');
        }, "json")
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus);
            $('#waitingModal').modal('hide');
        });
}

/**
 * Override this if you want to add extra post parameters.
 */
Visualizer.prototype._generatePostParams = function() {
    var postParams = {
        language: this.language,
        user_script: this.code,
        problemId: this.problemId,
        /*
         * The server expects these, so we must always specify them
         * even though not all language visualizers use them.
         */
        test_case: '',
        add_params: '{}',
    };
    return postParams;
}

/**
 * Does nothing by default - subclasses should display the visualizer modal.
 */
Visualizer.prototype._showVisualizerWithData = function(data) {
}

