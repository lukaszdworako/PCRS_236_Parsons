var pythonVisError = false;

function executePythonVisualizer(option, data) {
/**
 * Python visualizer representation.
 */
    switch(option) {
        case "create_visualizer":
            createVisualizer(data);
            break;

        case "gen_execution_trace_params":
            getExecutionTraceParams(data);
            break;

        case "render_data":
            codeStr = data.codeStr;
            targetElement = data.targetElement;
            renderVal(codeStr, targetElement);
            break;

        default:
            return "option not supported";
    }

    function createVisualizer(data) {
    /**
     * Verify trace does not contain errors and create visualizer,
     * othervise don't enter visualization mode.
     */
        if (!errorsInTracePy(data)) {
            // assign global
            visualizer = createVisualizerPy(data);
            visualizer.updateOutput();
        }

    }

    function errorsInTracePy(data) {
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
        // don't enter visualize mode if there are killer errors:
        var errors_caught = false;

        if (data.exception) {
            alert(data.exception);
            errors_caught = true;
            pythonVisError = true;
        }
        else {
            pythonVisError = false;
            trace = data.trace;

            if (trace.length == 0) {
                var errorLineNo = trace[0].line - 1; /* CodeMirror lines are zero-indexed */
                if (errorLineNo !== undefined) {
                    // highlight the faulting line in mainCodeMirror
                    mainCodeMirror.focus();
                    mainCodeMirror.setCursor(errorLineNo, 0);
                    mainCodeMirror.setLineClass(errorLineNo, null, 'errorLine');

                    mainCodeMirror.setOption('onChange', function() {
                        mainCodeMirror.setLineClass(errorLineNo, null, null); // reset line back to normal
                        mainCodeMirror.setOption('onChange', null); // cancel
                    });
                }

                alert("Syntax error, cannot visualize code execution");
                errors_caught = true;
            }

            else if (trace[trace.length - 1].exception_msg) {
                alert(trace[trace.length - 1].exception_msg);
                errors_caught = true;
            }

            else if (!trace) {
                alert("Unknown error.");
                errors_caught = true;

            }
        }

        return errors_caught;
    }

    function createVisualizerPy(data) {
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
        var pyVisualizer = new ExecutionVisualizer('visualize-code',
                                               data,
                                               {startingInstruction:  0,
                                                updateOutputCallback: function() {$('#urlOutput,#embedCodeOutput').val('');},
                                                // tricky: selector 'true' and 'false' values are strings!
                                                disableHeapNesting: ('true' == 'true'),
                                                drawParentPointers: ('true' == 'true'),
                                                textualMemoryLabels: ('true' == 'true'),
                                                //allowEditAnnotations: true,
                                               });


        // set keyboard bindings
        $(document).keydown(function(k) {
            if (k.keyCode == 37) { // left arrow
                if (pyVisualizer.stepBack()) {
                    k.preventDefault(); // don't horizontally scroll the display
                    keyStuckDown = true;
                }
            }
            else if (k.keyCode == 39) { // right arrow
                if (pyVisualizer.stepForward()) {
                    k.preventDefault(); // don't horizontally scroll the display
                    keyStuckDown = true;
                }
            }
        });

        $(document).keyup(function(k) {
          keyStuckDown = false;
        });

        // also scroll to top to make the UI more usable on smaller monitors
        $(document).scrollTop(0);

        return pyVisualizer;
    }

    function getExecutionTraceParams(initPostParams) {
    /**
     * Update dictionary initPostParams with additional parameters
     * that will be used to create a visualizer.
     */
        cumulative_mode = 'false';
        heap_primitives = 'true';
        initPostParams.add_params = JSON.stringify({cumulative_mode : cumulative_mode, heap_primitives : heap_primitives});

    }

    function renderVal(codeStr, targetElement) {
    /**
     * Make sure to clean targetElement, then call actual visualizer function.
     */
        targetElement.empty();
        renderData_ignoreID(codeStr, targetElement);
    }
}
