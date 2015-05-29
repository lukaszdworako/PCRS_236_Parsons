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
            var main_line;
            var removedLines;
            var start_line;

            div_id = debugger_id.substring(0, debugger_id.length - 1);
            removedLines = removeHashkeyForDisplay(div_id, newCode);
            codeToShow = removedLines[0];
            main_line = removedLines[1];
            //If the main function is inside the student-visible code, start on this line:
            //otherwise, start on the first student-visible line
            if(main_line >= 0) {
                start_line = main_line
            }
            else {
                start_line = 0;
            }

            if(!c_debugger_load) {
                c_debugger_load = true;
                // Refresh Code Mirror
                $('#newvisualizerModal').on('shown.bs.modal', function () {
                    myCodeMirrors[debugger_id].refresh();
                });

                // Bind debugger buttons
                $('#new_previous_debugger').bind('click', function () {
                    if ((cur_line -1) >= start_line) {
                        last_stepped_line_debugger = cur_line;
                        cur_line--;
                        update_new_debugger_table(debugger_data, "prev", start_line);
                    }
                });

                $('#new_next_debugger').bind('click', function () {
                    if (myCodeMirrors[debugger_id].lineInfo(cur_line+1) != null) {
                        last_stepped_line_debugger = cur_line;
                        cur_line++;
                        update_new_debugger_table(debugger_data, "next", start_line);
                    }
                });

                $('#new_reset_debugger').bind('click', function () {
                    last_stepped_line_debugger = cur_line;
                    cur_line = start_line;
                    json_index = 0;
                    //Clear the stack and heap tables
                    $('#name-type-section').empty();
                    $('#new_debugger_table_heap').empty();
                    update_new_debugger_table(debugger_data, "reset", start_line);
                });
            }

            //Clear the stack and heap tables
            $('#name-type-section').empty();
            $('#new_debugger_table_heap').empty();

            //Note: cur_line starts at 0 even though the line numbers start at 1: this is why
            //we add 1 to cur_line when we do checking vs. JSON files below.
            cur_line = start_line;
            json_index = 0;
            last_stepped_line_debugger = 0;

            myCodeMirrors[debugger_id].setValue(codeToShow);

            // Initialize debugger for the first time
            update_new_debugger_table(debugger_data, "reset", start_line);

            $('#newvisualizerModal').modal('show');

        }

        function update_new_debugger_table(data, update_type, start_line){
            myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');
            myCodeMirrors[debugger_id].addLineClass(cur_line, '', 'CodeMirror-activeline-background')
            //If resetting, first ensure all global variables are dealt with
            if(update_type == "reset") {
                globals = debugger_data["global_vars"];
                global_amt = globals.length;
                for(var i = 0; i < global_amt; i++) {
                    //Include global vars
                    add_to_name_table(globals[i]);
                    add_to_memory_table(globals[i]);
                    add_to_val_list(globals[i]);
                }
            }

            if((update_type == "next") || (update_type == "reset")) {
                // REMOVE LATER
                add_to_memory_table(debugger_data["steps"][json_index]);
                // REMOVE LATER

                while((json_index < debugger_data["steps"].length) && (debugger_data["steps"][json_index]["student_view_line"] <= (cur_line+1))) {
                    //Process JSON here to go forward a line(
                    add_to_name_table(debugger_data["steps"][json_index]);
                    //add_to_memory_table(debugger_data["steps"][json_index]);
                    add_to_val_list(debugger_data["steps"][json_index]);

                    if (json_index < (debugger_data["steps"].length-1)) {
                        json_index++;
                    }
                    else {
                        break;
                    }
                }
            }
            else if(update_type == "prev") {
                //Decrease the json index by 1 if it's not at the very beginning or end, since this step has not actually been applied
                //to the chart yet, it will be after the user presses next again
                if((cur_line > start_line) && ((myCodeMirrors[debugger_id].lineInfo(cur_line+1) != null))) {
                    json_index --;
                }
                while((json_index >= 0) && (debugger_data["steps"][json_index]["student_view_line"] > (cur_line+1))) {
                    console.log("step:"+debugger_data["steps"][json_index]["step"]);
                    console.log("in prev, cur line is "+cur_line+"and json index is "+json_index);
                    //Process JSON here to go backward a line
                    remove_from_name_table(debugger_data["steps"][json_index]);
                    remove_from_memory_table(debugger_data["steps"][json_index]);
                    remove_from_val_list(debugger_data["steps"][json_index]);

                    if (json_index > 0) {
                        json_index--;
                    }
                    else {
                        break;
                    }
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


        /*
        TO DO for name table functions:
            -Add in function return handling
            -Add in collapsing/expanding of previous/recent tables
            -Testing on more extensive JSON
        */

        //Applies the most recent forward-changes of the current step to the name table: the only time this might be
        //a removal is if a variable got freed on the heap
        function add_to_name_table(json_step) {
            if(!json_step.hasOwnProperty('changed_vars')) {
                return;
            }

            //Loop through all var changes in the step
            for(var i=0; i<json_step['changed_vars'].length; i++) {

                //Check if it's new - if so, adding it
                if(json_step['changed_vars'][i]['new']) {

                    //If the variable is a pointer, only add it if its marked to show up in the name table
                    if(!(json_step['changed_vars'][i].hasOwnProperty('is_ptr')) || (json_step['changed_vars'][i]['is_ptr']=="name")) {

                        //Check if it's in the stack, heap, or data to decide what we're looking for
                        if(json_step['changed_vars'][i]['location'] == "stack") {
                            table_name = json_step['function'];
                        }
                        else if (json_step['changed_vars'][i]['location'] == "heap") {
                            table_name = 'Heap';
                        }
                        else {
                            table_name = 'Data';
                        }

                        var cur_frame;
                        cur_frame = $('#names-'+table_name);

                        //Check if there's a current frame up for this:
                        if(cur_frame.length == 0) {
                        //If not, create a whole new name table
                            $('#name-type-section').append('<h4>'+table_name+'</h4> <table id="names-' +table_name+
                            '" class="table table-bordered" style="width: 100%; float:left;">'+
                            '<thead>'+
                                '<tr>'+
                                '<th width="60%">Name</th>' +
                                '<th width="40%">Type</th>' +
                                '</tr>' +
                            '</thead>' +
                            '<tbody id="name-body-'+table_name+'">' +
                            '</tbody>' +
                            '</table>');
                        }

                        //Add a row to the existing name table
                        $('#name-body-'+table_name).append('<tr id="'+table_name+'-'+json_step['changed_vars'][i]['var_name']+'" data-address="'+
                            json_step['changed_vars'][i]['addr']+'">' +
                            '<td class="var-name">' + json_step['changed_vars'][i]['var_name'] + '</td>' +
                            '<td class="var-type">' + json_step['changed_vars'][i]['type'] + '</td>' +
                        '</tr>');
                    }
                }

                //If not new, will only be deleting it if on the heap table (verify this)
                else if ((json_step['changed_vars'][i]['location']) == "Heap" && (json_step['changed_vars'][i].hasOwnProperty('freed'))) {
                        //Remove this var from table
                        $('#Heap-'+json_step['changed_vars'][i]['var_name']).remove();
                        check_rm_empty_table("names-Heap");
                }
            }
            //Do collapsing/expanding of tables here, make sure the table of the last var change is expanded
        }

        function add_to_memory_table(json_step) {
            console.log('GOOBY PLSSSSSSSSSSSS');
            console.log('step: ' + json_step.step);
            console.log(json_step);
            if(json_step.hasOwnProperty('changed_vars')) {
                add_changed_vars_to_memory_table(json_step);
            }
            if(json_step.hasOwnProperty('return')) {
                add_return_to_memory_table(json_step);
            }
        }

        function add_changed_vars_to_memory_table(json_step){
            var changed_vars = json_step.changed_vars;
            var num_changed_vars = changed_vars.length;
            for(var i=0; i < num_changed_vars; i++) {

            }
        }

        function add_return_to_memory_table(json_step){
            // TODO: implement
        }


        function add_to_val_list(json_step) {
            //implement me!

        }

        //Applies the most recent backward-changes of the current step to the name table: the only time this might be
        //an addition is if a variable got freed on the heap in the last step, adding it back
        function remove_from_name_table(json_step) {
            if(!json_step.hasOwnProperty('changed_vars')) {
                return;
            }

            //Loop through all var changes in the step
            for(var i=0; i<json_step['changed_vars'].length; i++) {

                //Check if it's new - if so, removing it
                if(json_step['changed_vars'][i]['new']) {

                    //If the variable is a pointer, only remove it if its marked to show up in the name table
                    if(!(json_step['changed_vars'][i].hasOwnProperty('is_ptr')) || (json_step['changed_vars'][i]['is_ptr']=="name")) {

                        //Check if it's in the stack, heap, or data to decide what we're looking for
                        if(json_step['changed_vars'][i]['location'] == "stack") {
                            table_name = json_step['function'];
                        }
                        else if (json_step['changed_vars'][i]['location'] == "heap") {
                            table_name = 'Heap';
                        }
                        else {
                            table_name = 'Data';
                        }

                        var cur_frame;
                        cur_frame = $('#names-'+table_name);

                        $(table_name+'-'+json_step['changed_vars'][i]['var_name']).remove();

                        //Check if the table is now empty from this removal, remove if so
                        table_id = '#names-'+table_name;
                        check_rm_empty_table(table_id);
                    }
                }

                //If not new, will only be adding it if on the heap table and it was freed in the most recent step
                else if ((json_step['changed_vars'][i]['location']) == "heap" && (json_step['changed_vars'][i].hasOwnProperty('freed'))) {
                    //Add this var to the table

                    //Check if table exists: either create heap table, or add to heap table
                    var heap_frame = $('#names-Heap');

                    //Check if there's a current frame up for this:
                    if(heap_frame.length == 0) {
                    //If not, create a whole new name table
                        $('#name-type-section').append('<h4>Heap</h4> <table id="names-Heap"'+
                            'class="table table-bordered" style="width: 100%; float:left;">'+
                        '<thead>'+
                            '<tr>'+
                            '<th width="60%">Name</th>' +
                            '<th width="40%">Type</th>' +
                            '</tr>' +
                        '</thead>' +
                        '<tbody id="name-body-heap">' +
                        '</tbody>' +
                        '</table>');
                    }

                    //Add the new row to the existing heap name table
                    $('#name-body-heap').append('<tr id="heap-'+json_step['changed_vars'][i]['var_name']+'" data-address="'+
                        json_step['changed_vars'][i]['addr']+'">' +
                        '<td class="var-name">' + json_step['changed_vars'][i]['var_name'] + '</td>' +
                        '<td class="var-type">' + json_step['changed_vars'][i]['type'] + '</td>' +
                    '</tr>');
                }
            }
            //Do collapsing/expanding of tables here, make sure the table of the last var change is expanded
        }

        function remove_from_memory_table(json_step) {
            //implement me!
        }

        function remove_from_val_list(json_step) {
            //implement me!
        }

        function check_rm_empty_table(table_name) {
            //Check if a table is empty (has no rows in body)- if so, remove the whole table from the DOM
            //Call this any time a row is removed from a table
            var row_amt = $('#'+table_name+' tr').length;
            if (row_amt <= 1) {
                $('#'+table_name).remove();
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

function removeHashkeyForDisplay(div_id, newCode){
    /**
     * Generate a Hashkey based on
     * the problem_id to identify
     * where the student code starts and ends
     */
    var codeArray = newCode.split('\n');
    var line_count = codeArray.length;
    var code = "";
    var i;
    var main_line = -1;
    //var re = new RegExp(main\s*\([\s\w]*\));
    for (i = 0; i < line_count; i++){
        //wrapClass = newCode.lineInfo(i).wrapClass;
        if (codeArray[i] == CryptoJS.SHA1(div_id.split("-")[1])) {
            code += "";
        }
        else {
            code += codeArray[i];
            //Check for the main function declaration, this is the line we should start
            //student steps from, if it is not hidden
            if (codeArray[i].search('main\s*\([\s\w]*\)') >= 0){
                main_line = i;
            }
        }
        code += '\n';
    }
    return [code.substring(0, code.length-1), main_line];
}
