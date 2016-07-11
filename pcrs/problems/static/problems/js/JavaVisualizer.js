function JavaVisualizer() {
    Visualizer.call(this);
    this.language = 'java';
    this.compileErrorCallback = function(file, line, message) {};
    this.files = [];
}
JavaVisualizer.prototype = Object.create(Visualizer.prototype);
JavaVisualizer.prototype.constructor = JavaVisualizer;

/**
 * Convenience method to set the submission code by a file array.
 */
JavaVisualizer.prototype.setFiles = function(files) {
    this.files = files;
    this.setCode(this._generateEditorCodeFromFiles(files));
}

/**
 * @param callback {function} With params file, line, and message.
 */
JavaVisualizer.prototype.setCompileErrorCallback = function(callback) {
    this.compileErrorCallback = callback;
}

/**
 * @override
 */
JavaVisualizer.prototype._showVisualizerWithData = function(data) {
    if (data.trace) {
        data.trace = JSON.parse(data.trace).trace;
    }

    if (this._errorsInTrace(data)) {
        return;
    }

    $('#visualizerModal').modal('show');

    var pyTutor = this._createPyTutorVisualizer({
        files: this.files,
        trace: data.trace,
    });

    pyTutor.updateOutput();
}

/**
 * Turns a file list into a submittable code string with [file] tags.
 */
JavaVisualizer.prototype._generateEditorCodeFromFiles = function(files) {
    var code = '';
    for (var i = 0; i < files.length; i++) {
        code += '[file ' + files[i].name + ']\n' +
            files[i].code +
            '\n[/file]\n';
    }
    return code;
}

JavaVisualizer.prototype._errorsInTrace = function(data) {
    var trace = data.trace;

    if (data.exception) {
        alert(data.exception);
        return true;
    } else if ( ! trace || trace.length == 0) {
        alert("Unknown error.");
        return true;
    }

    var lastStep = trace[trace.length - 1];
    var isCompileError = trace.length == 1 && lastStep.exception_msg;
    if (isCompileError) {
        var file = lastStep.file;
        var line = lastStep.line - 1; // Should be 0-indexed
        var message = lastStep.exception_msg;
        this.compileErrorCallback(file, line, message);
        return true;
    }

    return false;
}

JavaVisualizer.prototype._createPyTutorVisualizer = function(data) {
    var javaVisualizer = new ExecutionVisualizer('visualize-code', data, {
        startingInstruction:  0,
        updateOutputCallback: function() {
            $('#urlOutput,#embedCodeOutput').val('');
        },
        disableHeapNesting: true,
        textualMemoryLabels: true,
        //allowEditAnnotations: true,
    });

    $(document).keydown(function(k) {
        // Left arrow
        if (k.keyCode == 37 && javaVisualizer.stepBack()) {
            // Don't horizontally scroll the display
            k.preventDefault();
        // Right arrow
        } else if (k.keyCode == 39 && javaVisualizer.stepForward()) {
            // Don't horizontally scroll the display
            k.preventDefault();
        }
    });

    // also scroll to top to make the UI more usable on smaller monitors
    $(document).scrollTop(0);

    return javaVisualizer;
}

