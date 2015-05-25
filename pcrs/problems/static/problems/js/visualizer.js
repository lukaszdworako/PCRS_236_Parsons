/**
 * Generic Visualizer, that is used by all languages.
 * To plug in a language, create a corresponing function. Function must support
 * required options, regardless of existence of visualizer for the language.
 * If a visualizer exists, function must support all options, and language has to be
 * added to supportedVisualization array.
 *
 *                          Usage options:
 *
 * "create_visualizer": creates visualizer of required language
 *     data: format depends on the language.
 *
 * "gen_execution_trace_params": update dictionary with additional parameters required
 *  to generate execution trace. Make sure to JSON.stringify add_params.
 *     data: {language : language, user_script : code}
 *     updated data: {language : language, user_script : code, add_params : {}}
 *
 * "render_data" (required): render code string and populate
 *  corresponding cell in grading table
 *     data: {codeStr : encodedResult, targetElement : $('#tcase_ td.testOutputCell')}
 *
 */

function executeGenericVisualizer(option, data, newCode, newOrOld) {
    console.log("got to visualizer.js");
    var supportedVisualization = ['python', 'c'];

    if (visualizationSupported()){
        if (language == 'python') {
            return executePythonVisualizer(option, data);
        }
        else if (language == 'c') {
            return executeCVisualizer(option, data, newCode, newOrOld);
        }
    }else{
        alert("No support for visualization available!");
        return null;
    }

    function visualizationSupported() {
    /**
     * Return boolean true if global language is in the array supportedVisualization;
     * false otherwise.
     */
        return $.inArray(language, supportedVisualization) > -1;
    }

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
            if (errorsInTracePy(data)) {
                changeView("edit-code");
            }

            else {
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

            }

            else {
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

    function executeCVisualizer(option, data, newCode, newOrOld) {
    /**
     * C visualizer representation.
     */
        console.log(data);
        switch(option) {

            case "create_visualizer":
                if(!errorsInTraceC(data)) {
                    if(newOrOld == "old") {
                        createVisualizer(data, newCode);
                    }
                    else {
                        createNewVisualizer(data, newCode);
                    }
                }
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

        function replaceAll(find, replace, str) {
          return str.replace(new RegExp(find, 'g'), replace);
        }

        function errorsInTraceC(data){

            if(data.hasOwnProperty('exception')){
                alert(replaceAll("<br />", "\n", data['exception']));
                return true;
            }
            return false;
        }

        function createVisualizer(data, newCode) {
            /**
             * Verify trace does not contain errors and create visualizer,
             * othervise don't enter visualization mode.
             */


            console.log("new code is "+newCode);
            debugger_data = data;
            console.log("data is "+debugger_data)

            if(!c_debugger_load) {
                c_debugger_load = true;

                // Refresh Code Mirror
                $('#visualizerModal').on('shown.bs.modal', function () {
                    myCodeMirrors[debugger_id].refresh();
                });

                // Bind debugger buttons
                $('#previous_debugger').bind('click', function () {
                    if (debugger_index >= 1) {
                        debugger_index--;
                    }
                    update_debugger_table(debugger_data);
                });

                $('#next_debugger').bind('click', function () {
                    if (typeof (data[debugger_index + 1]) != 'undefined') {
                        debugger_index++;
                        update_debugger_table(debugger_data);
                    }
                });

                $('#reset_debugger').bind('click', function () {
                    debugger_index = 0;
                    update_debugger_table(debugger_data);
                });
            }

            debugger_index = 0;
            last_stepped_line_debugger = 0;

            myCodeMirrors[debugger_id].setValue(newCode);

            // Initialize debugger for the first time
            update_debugger_table(debugger_data);

            $('#visualizerModal').modal('show');

        }

        /*FOR THE NEW VISUALIZER*/
        function createNewVisualizer(data, newCode) {
            /**
             * Verify trace does not contain errors and create visualizer,
             * othervise don't enter visualization mode.
             */
            console.log("new code is "+newCode);
            debugger_data = data;
            console.log(debugger_data);

            if(!c_debugger_load) {
                c_debugger_load = true;
                // Refresh Code Mirror
                $('#newvisualizerModal').on('shown.bs.modal', function () {
                    myCodeMirrors[debugger_id].refresh();
                });

                // Bind debugger buttons
                $('#new_previous_debugger').bind('click', function () {
                    if (debugger_index >= 1) {
                        debugger_index--;
                    }
                    update_debugger_table(debugger_data, "prev");
                });

                $('#new_next_debugger').bind('click', function () {
                    if (typeof (data[debugger_index + 1]) != 'undefined') {
                        debugger_index++;
                        update_debugger_table(debugger_data, "next");
                    }
                });

                $('#new_reset_debugger').bind('click', function () {
                    debugger_index = 0;
                    update_debugger_table(debugger_data, "reset");
                });

                //Clear the stack and heap tables
                $('#new_debugger_table_stack').empty();
                $('#new_debugger_table_heap').empty();
            }

            debugger_index = 1;
            json_index = 0;
            last_stepped_line_debugger = 0;

            console.log(myCodeMirrors);
            console.log(myCodeMirrors[debugger_id]);

            codeToShow = removeHashkeyForDisplay(debugger_id);
            myCodeMirrors[debugger_id].setValue(codeToShow);

            // Initialize debugger for the first time
            update_new_debugger_table(debugger_data, "reset");

            $('#newvisualizerModal').modal('show');

        }

        function update_new_debugger_table(data, update_type){
            myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');
            if(update_type == "next") {
                while(debugger_data["steps"][0]) {
                    //
                }
            }
        }


        function update_debugger_table(data) {

            $('#debugger_table_stack').empty();
            $('#debugger_table_heap').empty();
            myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');
            console.log("down here data is <below> while debugger index is at "+debugger_index);
            console.log(data);
            for(var i = 0; i < data[debugger_index].length; i++) {

                console.log(data[debugger_index][i]);

                myCodeMirrors[debugger_id].addLineClass(parseInt(data[debugger_index][i][0]-1), '', 'CodeMirror-activeline-background');

                if(data[debugger_index][i][6] != "True") {
                    $('#debugger_table_stack').append('<tr>' +
                    '<th class="text-nowrap" scope="row">' + data[debugger_index][i][4] + '</th>' +
                    '<td>' + data[debugger_index][i][2] + '</td>' +
                    '<td>' + data[debugger_index][i][3] + '</td>' +
                    '<td>' + data[debugger_index][i][1] + '</td>' +
                    '</tr>');
                    $('#new_debugger_table_stack').append('<tr>' +
                    '<th class="text-nowrap" scope="row">' + data[debugger_index][i][4] + '</th>' +
                    '<td>' + data[debugger_index][i][2] + '</td>' +
                    '<td>' + data[debugger_index][i][3] + '</td>' +
                    '<td>' + data[debugger_index][i][1] + '</td>' +
                    '</tr>');
                }
                else {
                    $('#debugger_table_heap').append('<tr>' +
                    '<th class="text-nowrap" scope="row">' + data[debugger_index][i][3] + '</th>' +
                    '<td>' + data[debugger_index][i][5] + '</td>' +
                    '</tr>');
                    $('#new_debugger_table_heap').append('<tr>' +
                    '<th class="text-nowrap" scope="row">' + data[debugger_index][i][3] + '</th>' +
                    '<td>' + data[debugger_index][i][5] + '</td>' +
                    '</tr>');
                }
                last_stepped_line_debugger = parseInt(data[debugger_index][i][0]-1);
            }

        }

        function getExecutionTraceParams(initPostParams) {
        /**
         * Update dictionary initPostParams with additional parameters
         * that will be used to create a visualizer.
         */
            initPostParams.add_params = JSON.stringify({test_case : initPostParams.test_case});
        }

        function renderVal(codeStr, targetElement) {
        /**
         * Make sure to clean targetElement, then call actual visualizer function.
         */
            targetElement.empty();
            renderData_ignoreID(codeStr, targetElement);
        }
    }
}
