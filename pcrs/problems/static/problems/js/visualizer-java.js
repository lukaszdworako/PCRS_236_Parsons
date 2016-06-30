function executeJavaVisualizer(option, data) {
    // FIXME this should be a parameter passed in!
    // TODO subclass SubmissionWrapper
    var wrapperDiv = $('#java-1-editor');
    var tcm = myCodeMirrors['java-1-editor'];

    switch(option) {
        case "create_visualizer":
            createVisualizer(data);
            break;

        case "gen_execution_trace_params":
            getExecutionTraceParams(data);
            break;

        case "render_data":
            throw new Error('This method is legacy! Why is it being called?');
            break;

        default:
            return "option not supported";
    }

    /**
     * Update dictionary initPostParams with additional parameters
     * that will be used to create a visualizer.
     */
    function getExecutionTraceParams(initPostParams) {
        initPostParams.add_params = JSON.stringify({
        });
    }

    /**
     * Verify trace does not contain errors and create visualizer,
     * othervise don't enter visualization mode.
     */
    function createVisualizer(data) {
        if (data.trace) {
            data.trace = JSON.parse(data.trace).trace;
        }

        // FIXME hax!
        if (pythonVisError = errorsInTraceJava(data)) {
            return;
        }

        var files = tcm.getFiles();

        var visualizer = createVisualizerJava({
            files: files,
            trace: data.trace,
        });
        visualizer.updateOutput();
    }

    /**
     * This function has been taken from:
     *
     * Online Python Tutor
     * https://github.com/pgbovine/OnlinePythonTutor/
     *
     * Copyright (C) 2010-2013 Philip J. Guo (philip@pgbovine.net)
     *
     * Return boolean true if there are errors in trace, false otherwise.
     * Note that this function raises alerts.
     */
    function errorsInTraceJava(data) {
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
            displayErrorInStepJson(lastStep);
            return true;
        }

        return false;
    }

    function displayErrorInStepJson(json) {
        // CodeMirror lines are zero-indexed
        var errorLineNo = json.line - 1;

        var tabIndex = tcm.indexForTabWithName(json.file);
        var mirror = tcm.getCodeMirror(tabIndex);
        tcm.setActiveTabIndex(tabIndex);

        var errorClass = 'CodeMirror-error-background';
        // highlight the faulting line in the current file
        mirror.focus();
        mirror.setCursor(errorLineNo, 0);
        mirror.addLineClass(errorLineNo, '', errorClass);

        var changeHandler = function() {
            // Reset line back to normal
            mirror.removeLineClass(errorLineNo, '', errorClass);
            mirror.off('change', changeHandler);
            wrapperDiv.find('#alert').hide();
        }
        mirror.on('change', changeHandler);

        /*
         * FIXME Once we inherit from SubmissionWrapper, we shouldn't
         * access this globally.
         */
        var $alertBox = wrapperDiv.find('#alert');
        $alertBox.show();
        $alertBox.toggleClass('red-alert', true);
        $alertBox.children('icon').toggleClass('remove-icon', true);
        $alertBox.children('span').text(json.exception_msg);
        wrapperDiv.find('.screen-reader-text').text(json.exception_msg);
    }

    /**
     * Content of this function has been taken from:
     *
     * Online Python Tutor
     * https://github.com/pgbovine/OnlinePythonTutor/
     *
     * Copyright (C) 2010-2013 Philip J. Guo (philip@pgbovine.net)
     *
     * Return an instance of Python visualizer.
     */
    function createVisualizerJava(data) {
        var javaVisualizer = new ExecutionVisualizer('visualize-code', data, {
            startingInstruction:  0,
            updateOutputCallback: function() {
                $('#urlOutput,#embedCodeOutput').val('');
            },
            // tricky: selector 'true' and 'false' values are strings!
            disableHeapNesting: ('true' == 'true'),
            drawParentPointers: ('true' == 'true'),
            textualMemoryLabels: ('true' == 'true'),
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
}

