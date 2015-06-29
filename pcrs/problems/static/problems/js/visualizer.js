// These global variables should not be modified
var memory_map_cell_height = 37; // In pixels
var address_width = 45 // In %
var memory_map_cell_width = 13.75; // In %
var cur_stdout = "";
var return_to_clr = "";
var return_val;
//Function we've most recently returned from
var most_recently_returned = "";
//Function we've most recently entered: keep track of this for if we hit prev
var most_recently_entered = "";

// These global variables will change throughout the program
var largest_group_id;
var group_id_vals = {};
var group_id_start_addrs = {};
var start_addrs_to_group_id = {};
var hex_mode_on = false;

function zeroPad (str, max) {
  str = str.toString();
  return str.length < max ? zeroPad("0" + str, max) : str;
}

function toHexString(hexnum) {
    return "0x" + zeroPad(hexnum.toString(16), 16);
}

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

function executeGenericVisualizer(option, data, newCode) {
    console.log("got to visualizer.js");
    var supportedVisualization = ['python', 'c'];
    var value_list = {};

    if (visualizationSupported()){
        if (language == 'python') {
            return executePythonVisualizer(option, data);
        }
        else if (language == 'c') {
            return executeCVisualizer(option, data, newCode);
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

    function executeCVisualizer(option, data, newCode) {
    /**
     * C visualizer representation.
     */
        var newOrOld = "new";     // By default, use the new vis
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
             * otherwise don't enter visualization mode.
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
            var removedLines;
            var start_line = debugger_data["steps"][0]["student_view_line"];

            div_id = debugger_id.substring(0, debugger_id.length - 1);
            codeToShow = removeHashkeyForDisplay(div_id, newCode);

            if(!c_debugger_load) {
                c_debugger_load = true;
                // Refresh Code Mirror
                $('#newvisualizerModal').on('shown.bs.modal', function () {
                    myCodeMirrors[debugger_id].refresh();
                });

                // Bind debugger buttons
                $('#new_previous_debugger').bind('click', function () {
                    if (json_index > 0) {
                        last_stepped_line_debugger = cur_line;
                        cur_line = debugger_data["steps"][json_index-1]["student_view_line"]-1;
                        update_new_debugger_table(debugger_data, "prev");
                    }
                });

                $('#new_next_debugger').bind('click', function () {
                    if (json_index <(debugger_data["steps"].length-1)) {
                        last_stepped_line_debugger = cur_line;
                        json_index++;
                        cur_line = debugger_data["steps"][json_index]["student_view_line"]-1;
                        update_new_debugger_table(debugger_data, "next");
                    }
                });

                $('#new_reset_debugger').bind('click', function () {
                    last_stepped_line_debugger = cur_line;
                    cur_line = start_line-1;
                    json_index = 0;
                    // Reset the memory map tables
                    reset_memory_tables();

                    // Clear the name tables
                    $('#name-type-section').empty();
                    $('#new_debugger_table_heap').empty();
                    //Clear stdout
                    cur_stdout= "";
                    $("#std-out-textbox").html(cur_stdout);
                    update_new_debugger_table(debugger_data, "reset");
                });

                $('#toggle-hex-button').bind('click', function () {
                    toggle_hex();
                });

                $('#data-minimizer').bind('click', create_minimize_function("data-memory-map"));
                $('#heap-minimizer').bind('click', create_minimize_function("heap-memory-map"));
            }

            // Reset the memory map tables
            reset_memory_tables();

            // Clear the name tables
            $('#name-type-section').empty();
            $('#new_debugger_table_heap').empty();

            cur_stdout= "";
            $("#std-out-textbox").html(cur_stdout);

            //Codemirror starts line count at 0, subtract 1 from start line so it's accurate
            cur_line = start_line-1;
            json_index = 0;
            last_stepped_line_debugger = 0;

            myCodeMirrors[debugger_id].setValue(codeToShow);

            // Initialize debugger for the first time
            update_new_debugger_table(debugger_data, "reset");

            $('#newvisualizerModal').modal('show');

        }

        function update_new_debugger_table(data, update_type){
            myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');
            myCodeMirrors[debugger_id].addLineClass(cur_line, '', 'CodeMirror-activeline-background')

            //Removes any name table rows that must be removed with this step
            $(return_to_clr).remove();
            return_to_clr = "";

            //If resetting, first ensure all global variables are dealt with
            if(update_type == "reset") {
                globals = debugger_data["global_vars"];
                global_amt = globals.length;
                for(var i = 0; i < global_amt; i++) {
                    //Include global vars
                    add_to_name_table(globals[i]);
                    add_to_val_list(globals[i]);
                    add_to_memory_table(globals[i]);
                }
            }

            var json_step = debugger_data["steps"][json_index];
            console.log("JSON STEP IS:");
            console.log(json_step);
            if((update_type == "next") || (update_type == "reset")) {
                console.log("step:"+debugger_data["steps"][json_index]["step"]);
                console.log("in next, cur line is "+cur_line+"and json index is "+json_index);

                if(json_step.hasOwnProperty('on_entry_point')) {
                    // Create the empty table even before any variables get assigned
                    get_var_location('stack', json_step['function']);
                    add_first_name_table(json_step);
                    $("#name-table-"+json_step['function']).show()
                    most_recently_entered = json_step['function'];
                }

                //Case where there's changed variables
                if(json_step.hasOwnProperty('changed_vars')) {
                    add_to_name_table(json_step);
                    add_to_val_list(json_step);
                    add_to_memory_table(json_step);
                }
                //Case where it's a function return
                if((json_step.hasOwnProperty('return')) || (json_step.hasOwnProperty('returned_fn_call'))) {
                    console.log("calling add to name table func");
                    add_return_name_table(json_step);
                }

                if(json_step.hasOwnProperty('returned_fn_call')) {
                    // Remove the previous stack frame and name table of this function
                    $("#name-table-"+most_recently_returned).hide();
                    $("#stack-frame-tables div[stack-function='" + json_step['returned_fn_call'] + "']:first").remove();
                }

                //Case where it has standard output
                if(json_step.hasOwnProperty('std_out')) {
                    add_to_std_out(json_step);
                }
            }

            else if(update_type == "prev") {
                console.log("json index:"+json_index);
                console.log("step:"+json_step["step"]);
                console.log("in prev, cur line is "+cur_line+"and json index is "+json_index);
                //Process JSON here to go backward a line
                if(json_step.hasOwnProperty('changed_vars')) {
                    remove_from_name_table(json_step);
                    remove_from_val_list(json_step);
                    remove_from_memory_table(json_step);
                    //Case where it's a function return
                }
                //Case where it has standard output
                if(json_step.hasOwnProperty('std_out')) {
                    remove_from_std_out(json_step);
                }
                json_index--;
                json_step = debugger_data["steps"][json_index];
                if(json_step.hasOwnProperty('return') || json_step.hasOwnProperty('returned_fn_call') ) {
                    //console.log("have a return, json step is ");
                    add_return_name_table(json_step);
                }
                if(json_step.hasOwnProperty('return')) {
                    // Remove the previous stack frame and name table of this function
                    $("#name-table-"+most_recently_returned).show();
                }
                if(most_recently_entered != "") {
                    $("#name-table-"+most_recently_entered).hide();
                    most_recently_entered = "";
                }
                if(json_step.hasOwnProperty('on_entry_point')) {
                    most_recently_entered = json_step['function'];
                }
            }

            if((most_recently_entered != "") && (!json_step.hasOwnProperty('on_entry_point'))) {
                most_recently_entered = "";
            }

            console.log("value_list is: ");
            console.log(value_list);
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
            var table_name;
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
                            add_name_table_frame(table_name);
                        }

                        //Add a row to the existing name table
                        $('#name-body-'+table_name).append('<tr id="'+table_name+'-'+json_step['changed_vars'][i]['var_name']+'" data-address="'+
                            json_step['changed_vars'][i]['addr']+'">' +
                            '<td class="var-name hide-overflow" title="' + json_step['changed_vars'][i]['var_name'] + '">' + json_step['changed_vars'][i]['var_name'] + '</td>' +
                            '<td class="var-type hide-overflow" title="' + json_step['changed_vars'][i]['type'] + '">' + json_step['changed_vars'][i]['type'] + '</td>' +
                        '</tr>');

                        $('#name-body-'+table_name + " tr[id='"+table_name+'-'+json_step['changed_vars'][i]['var_name']+"']").hover(
                            create_hover_highlight_function_names(),
                            create_hover_unhighlight_function_names()
                            );
                    }
                }

                //If not new, will only be deleting it if on the heap table (verify this)
                else if ((json_step['changed_vars'][i]['location']) == "Heap" && (json_step['changed_vars'][i].hasOwnProperty('freed'))) {
                        //Remove this var from table
                        $('#Heap-'+json_step['changed_vars'][i]['var_name']).remove();
                        //check_rm_empty_table("names-Heap");
                }
            }
            //Do collapsing/expanding of tables here, make sure the table of the last var change is expanded
        }

        function add_name_table_frame(table_name) {
            $('#name-type-section').prepend('<span id="name-table-'+table_name+'"> <table id="names-' +table_name+
            '" class="table table-bordered" style="width: 100%; float:left;">'+
            '<thead>'+
                '<tr>'+
                 '<th colSpan=2>'+table_name + '</th>'+
                '</tr>'+
                '<tr>'+
                '<th width="60%">Name</th>' +
                '<th width="40%">Type</th>' +
                '</tr>' +
            '</thead>' +
            '<tbody id="name-body-'+table_name+'">' +
            '</tbody>' +
            '</table></span>');
        }

        function add_first_name_table(json_step) {
            table_name = json_step['function'];
            var cur_frame;
            cur_frame = $('#names-'+table_name);

            //Check if there's a current frame up for this:
            if(cur_frame.length == 0) {
            //If not, create a whole new name table
                add_name_table_frame(table_name);
            }
        }


        function add_to_memory_table(json_step) {
            add_to_memory_table_only(json_step);
            regenerate_all_label_tables();
        }

        function add_to_memory_table_only(json_step) {
            // This function exists because while removing, we want to only add variables to the cell tables then generate labels in one go, but with adding, we have to regenerate the label tables after each step

            // Add changed_vars to memory table
            var changed_vars = json_step.changed_vars;
            var func_name = json_step["function"];
            for(var i=0; i < changed_vars.length; i++) {
                add_one_var_to_memory_table(changed_vars[i], func_name);
            }
        }

        function add_one_var_to_memory_table(changed_var, func_name) {
            // Store values for possible use later
            var start_addr = parseInt(changed_var["addr"], 16);
            var value = changed_var["value"];
            var hex_value = changed_var["hex_value"].match(/.{1,2}/g).slice(1); // Turn into array of 1-byte hex values
            var func_location = changed_var["location"];
            var cells_needed = parseInt(changed_var["max_size"]);

            var location = get_var_location(func_location, func_name);

            // Don't continue if we have nowhere to add the variable, to prevent the browser hanging indefinitely
            if(!location){
                return;
            }

            // Add the cell rows first
            var new_var_cell_rows = $(create_new_var_cell_rows(start_addr, cells_needed, value, hex_value));

            // Append at the end if this address is greater than any currently in the table
            var simply_append_rows = $(location + " > table.memory-map-cell-table > tbody td[addr]").filter(function() {
                    return parseInt($(this).attr('addr'), 16) > start_addr;

            }).length == 0;
            console.log("Simply append: ", simply_append_rows);

            insert_cell_rows(location, start_addr, cells_needed, new_var_cell_rows, simply_append_rows);
        }

        function create_new_var_cell_rows(start_addr, cells_needed, value, hex_value) {
            var end_addr = start_addr + cells_needed - 1;
            var rows_needed = (Math.floor(end_addr/4)) - (Math.floor(start_addr/4)) + 1;

            // Create the rows
            var group_id = largest_group_id;
            largest_group_id++;
            group_id_vals[group_id] = value;
            group_id_start_addrs[group_id] = start_addr;
            start_addrs_to_group_id[start_addr] = group_id;

            var cell_rows = document.createElement("div");

            var hex_val_index = 0;
            var current_addr = start_addr;
            var remaining_cells = cells_needed;
            for(var r=1; r <= rows_needed; r++) {
                var row_start_addr = current_addr - (current_addr % 4);
                var start_cell_number = current_addr % 4;
                var current_cell_addr = row_start_addr;

                var cells_on_row = Math.min(remaining_cells, (4 - start_cell_number));

                // Add the row of hex value cells
                var cell_row = create_cell_base_row(row_start_addr);

                var c = 0;
                while(c < start_cell_number) {
                    var cell_hex_val = "&nbsp;";

                    if(current_cell_addr >= start_addr) {
                        cell_hex_val = hex_value[hex_val_index];
                        hex_val_index++;
                    }

                    var memory_map_cell = create_cell_cell(current_cell_addr, "", cell_hex_val, "");
                    cell_row.appendChild(memory_map_cell);

                    current_cell_addr++;
                    c++;
                }
                while(c < (start_cell_number + cells_on_row)) {
                    // Add the data cells
                    var clarity_classes = "clear-cell";
                    if(c == 3) {
                        clarity_classes = "right-edge-clear-cell";
                    }

                    if(rows_needed > 1){
                        // First row
                        if(r == 1) {
                            clarity_classes += " top-row-clear-cell";
                        } else if(r == rows_needed) {
                            clarity_classes += " bottom-row-clear-cell";
                        } else {
                            clarity_classes += " middle-row-clear-cell";
                        }
                    }

                    var memory_map_cell = create_cell_cell(current_cell_addr, group_id, hex_value[hex_val_index], clarity_classes);
                    cell_row.appendChild(memory_map_cell)
                    current_cell_addr++;
                    c++;
                    hex_val_index++;
                }
                while(c < 4) {
                    var cell_hex_val = "&nbsp;";

                    if(current_cell_addr <= end_addr) {
                        cell_hex_val = hex_value[hex_val_index];
                        hex_val_index++;
                    }

                    var memory_map_cell = create_cell_cell(current_cell_addr, "", cell_hex_val, "");
                    cell_row.appendChild(memory_map_cell);
                    current_cell_addr++;
                    c++;
                }

                cell_rows.appendChild(cell_row);

                // Advance to the next row
                current_addr = row_start_addr + 4;
                remaining_cells -= cells_on_row;
            }

            return cell_rows;
        }

        function insert_cell_rows(location, start_addr, cells_needed, new_var_cell_rows, simply_append_rows) {
            var location_cell_table = $(location + " > table.memory-map-cell-table > tbody ");

            if(simply_append_rows) {
                while(new_var_cell_rows.children().length > 0) {
                    location_cell_table.append(new_var_cell_rows.children().first());
                }

            } else {
                // Find location to insert
                var row_start_addr = start_addr - (start_addr % 4);
                var all_row_addrs = location_cell_table.find("tr[start-addr]").map(function() {
                    return parseInt($(this).attr("start-addr"), 16);
                }).toArray();

                // Find where to insert the row
                var insert_addr = 0;
                var smaller_addrs = all_row_addrs.filter(function(value) {
                    return (value <= row_start_addr);
                });
                if(smaller_addrs.length > 0) {
                    insert_addr = Math.max.apply(null, smaller_addrs);
                }

                // Get the address of the row just after the last row of this variable
                var end_addr = start_addr + cells_needed - 1;
                var row_end_addr = end_addr - (end_addr % 4);

                var after_end_addr = 0;
                var larger_addrs = all_row_addrs.filter(function(value) {
                    return (value > row_end_addr);
                });
                if(larger_addrs.length > 0) {
                    after_end_addr = Math.min.apply(null, larger_addrs);
                }

                // Remove all dot rows in between insert_addr and after_end_addr
                if(after_end_addr > 0) {
                    location_cell_table.find(" > tr[start-addr='" + toHexString(insert_addr) + "']").nextUntil("tr[start-addr='" + toHexString(after_end_addr) + "']").has("td.dot-line").remove();
                } else {
                    location_cell_table.find(" > tr[start-addr='" + toHexString(insert_addr) + "']").siblings().has("td.dot-line").remove();
                }


                // Insert the rows here, merging as needed
                insert_new_var_rows(location_cell_table, new_var_cell_rows, insert_addr, start_addr, after_end_addr, end_addr);

            }
        }

        function insert_new_var_rows(location_table, new_var_rows, insert_addr, start_addr, after_end_addr, end_addr) {
            var row_start_addr = start_addr - (start_addr % 4);
            var row_end_addr = end_addr - (end_addr % 4);

            // Insert the first row if it's at the beginning, or add a dot row before the first row if needed
            var insert_row = null;
            if(insert_addr > 0) {
                insert_row = location_table.find(" > tr[start-addr='" + toHexString(insert_addr) + "']");
                if((insert_addr != row_start_addr) && ((row_start_addr - insert_addr) > 4)) {
                    $(create_memory_map_dot_row()).insertAfter(insert_row);
                    insert_row = insert_row.next();
                }

            } else {
                location_table.prepend(new_var_rows.children().first());
                insert_row = location_table.children().first();
            }

            // At this point, insert_row represents the previously inserted row

            // Compare cell by cell and keep the overwriting ones; used for merging the cell table
            while(new_var_rows.children().length > 0) {
                var current_row = new_var_rows.children().first();
                var current_start_addr = current_row.attr("start-addr");
                var already_exists = location_table.find("tr[start-addr='" + current_start_addr + "']").length > 0;
                if(already_exists) {
                    // Combine current_row with the row where it'll be added
                    var existing_row = location_table.find("tr[start-addr='" + current_start_addr + "']");
                    var i = 0;
                    while(current_row.children().length > 0) {
                        // Only cells with a group-id count as part of the actual variable, the rest are ignored
                        if(current_row.children().first().attr("group-id")) {
                            $(existing_row.children()[i]).replaceWith(current_row.children().first());
                        } else {
                            $(current_row.children()[0]).remove();
                        }
                        i++;
                    }

                } else {
                    // Simply append the row to insert_row
                    current_row.insertAfter(insert_row);
                    insert_row = insert_row.next();
                }

                $(new_var_rows.children()[0]).remove();

            }

            // Insert a dot row after the last address if it is too far from the next address
            if((after_end_addr - row_end_addr) > 4) {
                $(create_memory_map_dot_row()).insertAfter(insert_row);
            }
        }

        function generate_label_table(location) {
            if(!location) {
                return;
            }

            // Generates the label table for the corresponding cell table at location
            // Relies on the map group_id_vals to get the label values
            var cell_table = $(location + " > table.memory-map-cell-table > tbody");
            var updated_label_table = document.createElement("tbody");

            var cell_table_rows = cell_table.children();
            var middle_rows_left = 0;
            var on_bottom_row = false;
            var in_middle = false;
            var previous_drawn_group_id = null;
            for(i=0; i < cell_table_rows.length; i++) {
                var current_row = $(cell_table_rows[i]);
                var current_row_addr = parseInt(current_row.attr("start-addr"), 16);

                var label_row = document.createElement("tr");

                if(current_row.find("td.dot-line").length > 0) {
                    label_row = create_memory_map_dot_row();
                } else {
                    label_row = create_label_base_row(current_row.attr("start-addr"));

                    if(middle_rows_left > 0) {
                        // Still drawing the middle rows of a wide label, so draw a standard row with no extra tds
                        middle_rows_left--;
                        if(middle_rows_left == 0) {
                            on_bottom_row = true;
                        }

                    } else {
                        // Merge individual cells across this row which are part of the same group
                        var td = null;

                        var c = 1;
                        while(c < 5) {
                            var colspan = 1;
                            var rowspan = 1;
                            var group_id = "";
                            var cell_value = "&nbsp;";
                            var clarity_classes = "";
                            var cells_on_row_in_group = 1;

                            var current_cell = $(current_row.children()[c]);
                            var current_cell_addr = parseInt(current_cell.attr("addr"), 16);
                            var current_cell_group_id = current_cell.attr("group-id");
                            if(current_cell_group_id) {
                                cells_on_row_in_group = current_cell.nextUntil("td[group-id!='" + current_cell_group_id + "']").length + 1;

                                // Finds all cells after the current one in the table, up until the first one with a different group-id
                                var group_end_addr = current_cell_addr + cells_on_row_in_group - 1;
                                var contiguous_cells_in_group = cells_on_row_in_group;
                                // Find how many cells are in this group if it extends past the current row
                                if((c + cells_on_row_in_group) > 4) {
                                    var sibling_rows = current_row.nextAll().toArray();
                                    var sr = 0;
                                    var bad_cell_found = false;

                                    // Exit upon seeing a dot row
                                    while((sr < sibling_rows.length)
                                            && ($(sibling_rows[sr]).find("td.dot-line").length == 0)
                                            && !bad_cell_found) {
                                        $(sibling_rows[sr]).find("td.memory-map-cell").each(function() {
                                            if(!bad_cell_found) {
                                                if($(this).attr("group-id") == current_cell_group_id) {
                                                    contiguous_cells_in_group++;
                                                    group_end_addr = parseInt($(this).attr("addr") ,16)
                                                } else {
                                                    bad_cell_found = true;
                                                }
                                            }
                                        });

                                        sr++;
                                    }

                                }


                                var rows_in_group = Math.floor(((group_end_addr - (group_end_addr % 4)) - current_row_addr) / 4) + 1;


                                colspan = cells_on_row_in_group;
                                group_id = current_cell_group_id;
                                if(rows_in_group > 1) {
                                    if(rows_in_group == 2 && !in_middle) {
                                        // Draw the label
                                        cell_value = group_id_vals[group_id];
                                        clarity_classes = "label-td"
                                        rowspan = rows_in_group;

                                        var last_row_extra_cells = ((group_end_addr%4) + 1) % 4;
                                        if(last_row_extra_cells > 0) {
                                            on_bottom_row = true;
                                        }

                                        if(c > 1 || last_row_extra_cells > 0) {
                                            rowspan--;
                                            clarity_classes += " top-row-clear-cell "
                                        }

                                        middle_rows_left = rowspan - 1;

                                    } else if(c == 1 && colspan == 4) {
                                        // Draw the label
                                        cell_value = group_id_vals[group_id];
                                        clarity_classes = "clear-cell middle-row-clear-cell label-td"
                                        rowspan = rows_in_group;
                                        if((group_end_addr % 4) > 0) {
                                            rowspan--;
                                        }

                                        middle_rows_left = rowspan - 1;
                                        if(middle_rows_left == 0) {
                                            on_bottom_row = true;
                                        }

                                    } else {
                                        // Draw the top row of the group
                                        clarity_classes = "top-row-clear-cell right-edge-clear-cell";
                                        in_middle = true;
                                    }

                                } else {
                                    if(on_bottom_row) {
                                        // Draw the bottom row
                                        clarity_classes = "clear-cell bottom-row-clear-cell";
                                        on_bottom_row = false;
                                        in_middle = false;

                                    } else {
                                        // Draw the label cell right now
                                        cell_value = group_id_vals[group_id];
                                        clarity_classes = "right-edge-clear-cell label-td";
                                    }

                                }
                            }

                            td = create_label_cell(colspan, rowspan, group_id, cell_value, clarity_classes);

                            label_row.appendChild(td);
                            c += cells_on_row_in_group;
                        }

                    }
                }

                updated_label_table.appendChild(label_row);
            }

            return updated_label_table;
        }

        function regenerate_all_label_tables() {
            regenerate_label_table("#data-memory-map");
            regenerate_label_table("#heap-memory-map");

            var num_stack_tables = $("#stack-frame-tables").children().length;
            var stack_table_location = "";
            for(var i=0; i < num_stack_tables; i++) {
                regenerate_label_table("#stack-frame-tables > div:eq(" + i + ")");
            }
        }

        function regenerate_label_table(location) {
            // This function is only a helper for regenerate_all_label_tables()
            var updated_label_table = generate_label_table(location)
            var location_label_table = $(location + " > table.memory-map-label-table > tbody ");

            // Hide the new table if hex mode is on
            if(hex_mode_on) {
                $(updated_label_table).find("td.memory-map-cell").hide();
                $(updated_label_table).css("z-index", 0)
            }

            var label_table_hidden = location_label_table.is(":hidden");
            console.log("Hidden: ", location_label_table.is(":hidden"));
            if(label_table_hidden) {
                $(updated_label_table).hide();
                $(updated_label_table).find("thead > tr:nth-child(2)").hide();
            }

            location_label_table.replaceWith(updated_label_table);
        }

        function get_var_location(func_location, func_name) {
            var location = "";
            if(func_location === "static") {
                location = "#data-memory-map";
            } else if(func_location === "heap") {
                location = "#heap-memory-map";
            } else if(func_location === "stack") {
                var stack_frame_exists = $("#stack-frame-tables > div[stack-function='" + func_name + "']").length > 0;

                if(!stack_frame_exists) {
                    var calling_line = json_index > 0 ? debugger_data["steps"][json_index-1]["student_view_line"] : 0;
                    var new_stack_frame = create_stack_frame_table(calling_line, func_name)
                    $("div#stack-frame-tables").prepend(new_stack_frame);
                }

                location = "div#stack-frame-tables > div[stack-function='" + func_name + "']:first";
            }

            return location;
        }


        function create_stack_frame_table(stack_frame_number, stack_function) {
            // Create the cells table
            var c_thead = document.createElement("thead");
            var c_tbody = document.createElement("tbody");

            //---

            var c_col_size_1 = document.createElement("col");
            c_col_size_1.setAttribute("width", address_width + "%");
            var c_col_size_2 = document.createElement("col");
            c_col_size_2.setAttribute("width", memory_map_cell_width + "%");
            var c_col_size_3 = document.createElement("col");
            c_col_size_3.setAttribute("width", memory_map_cell_width + "%");
            var c_col_size_4 = document.createElement("col");
            c_col_size_4.setAttribute("width", memory_map_cell_width + "%");
            var c_col_size_5 = document.createElement("col");
            c_col_size_5.setAttribute("width", memory_map_cell_width + "%");

            var l_col_size_1 = document.createElement("col");
            l_col_size_1.setAttribute("width", address_width + "%");
            var l_col_size_2 = document.createElement("col");
            l_col_size_2.setAttribute("width", memory_map_cell_width + "%");
            var l_col_size_3 = document.createElement("col");
            l_col_size_3.setAttribute("width", memory_map_cell_width + "%");
            var l_col_size_4 = document.createElement("col");
            l_col_size_4.setAttribute("width", memory_map_cell_width + "%");
            var l_col_size_5 = document.createElement("col");
            l_col_size_5.setAttribute("width", memory_map_cell_width + "%");

            //---

            var c_tr1_th = document.createElement("th");
            c_tr1_th.colSpan = "5";
            c_tr1_th.className = "heading-height";
            c_tr1_th.innerHTML = "&nbsp;";

            var c_tr1 = document.createElement("tr");
            c_tr1.appendChild(c_tr1_th);

            //---

            var c_tr2_th1 = document.createElement("th");
            c_tr2_th1.className = "heading-height";
            c_tr2_th1.innerHTML = "&nbsp;";

            var c_tr2_th2 = document.createElement("th");
            c_tr2_th2.className = "heading-height";
            c_tr2_th2.colSpan = "4";
            c_tr2_th2.innerHTML = "&nbsp;";

            var c_tr2 = document.createElement("tr");
            c_tr2.appendChild(c_tr2_th1);
            c_tr2.appendChild(c_tr2_th2);

            //---

            c_thead.appendChild(c_tr1);
            c_thead.appendChild(c_tr2);

            var cells_table = document.createElement("table");
            cells_table.className = "table-no-border memory-map-cell-table";
            cells_table.appendChild(c_col_size_1);
            cells_table.appendChild(c_col_size_2);
            cells_table.appendChild(c_col_size_3);
            cells_table.appendChild(c_col_size_4);
            cells_table.appendChild(c_col_size_5);
            cells_table.appendChild(c_thead);
            cells_table.appendChild(c_tbody);


            // Create the labels table
            var l_thead = document.createElement("thead");
            var l_tbody = document.createElement("tbody");

            //---

            var l_tr1_th = document.createElement("th");
            l_tr1_th.colSpan = "5";

            var minimizer = document.createElement("a");
            minimizer.href = "#";
            minimizer.className = "small-minimizer";

            var minimizer_span = document.createElement("span");
            minimizer_span.className = "minimizer-span";
            minimizer_span.innerHTML = "[-]";
            minimizer_span.addEventListener('click', stack_table_minimize_function);

            minimizer.appendChild(minimizer_span)

            var table_title = stack_function + (stack_frame_number > 0 ? ": " + stack_frame_number : "");

            l_tr1_th.appendChild(minimizer);
            $(l_tr1_th).append(table_title);


            var l_tr1 = document.createElement("tr");
            l_tr1.appendChild(l_tr1_th);

            //---

            var l_tr2_th1 = document.createElement("th");
            l_tr2_th1.className = "address-heading";
            l_tr2_th1.innerHTML = "Address";

            var l_tr2_th2 = document.createElement("th");
            l_tr2_th2.className = "values-heading";
            l_tr2_th2.colSpan = "4";
            l_tr2_th2.innerHTML = "Values"

            var l_tr2 = document.createElement("tr");
            l_tr2.appendChild(l_tr2_th1);
            l_tr2.appendChild(l_tr2_th2);

            //---

            l_thead.appendChild(l_tr1);
            l_thead.appendChild(l_tr2);

            var labels_table = document.createElement("table");
            labels_table.appendChild(l_col_size_1);
            labels_table.appendChild(l_col_size_2);
            labels_table.appendChild(l_col_size_3);
            labels_table.appendChild(l_col_size_4);
            labels_table.appendChild(l_col_size_5);
            labels_table.className = "table table-bordered memory-map-label-table";
            labels_table.appendChild(l_thead);
            labels_table.appendChild(l_tbody);


            // Wrap both tables correctly
            var stack_frame_table_wrapper = document.createElement("div");
            stack_frame_table_wrapper.className = "memory-map-table-wrapper";
            stack_frame_table_wrapper.setAttribute("stack-frame-number", stack_frame_number>0 ? stack_frame_number :0);
            stack_frame_table_wrapper.setAttribute("stack-function", stack_function);
            stack_frame_table_wrapper.appendChild(cells_table);
            stack_frame_table_wrapper.appendChild(labels_table);

            return stack_frame_table_wrapper;
        }

        function create_cell_cell(cell_addr, group_id, cell_value, clarity_classes) {
            var memory_map_cell = document.createElement("td");
            memory_map_cell.className = "memory-map-cell " + (hex_mode_on ? "" : "hidden-cell ");// + clarity_classes;
            memory_map_cell.setAttribute("addr", toHexString(cell_addr));

            if(cell_value && cell_value != "&nbsp;") {
                memory_map_cell.setAttribute("group-id", group_id);
                cell_value = "0x" + cell_value;
            }

            memory_map_cell.innerHTML = cell_value;

            if(group_id) {
                $(memory_map_cell).hover(
                    create_hover_highlight_function_memory(group_id),
                    create_hover_unhighlight_function_memory(group_id)
                    );
            }

            return memory_map_cell;
        }

        function create_label_cell(colspan, rowspan, group_id, cell_value, clarity_classes) {
            var memory_map_cell = document.createElement("td");
            memory_map_cell.className = "memory-map-cell " + clarity_classes;
            memory_map_cell.colSpan = colspan;
            memory_map_cell.rowSpan = rowspan;

            if(cell_value != "&nbsp;") {
                memory_map_cell.setAttribute("group-id", group_id);
            }
            memory_map_cell.innerHTML = cell_value;
            memory_map_cell.setAttribute("title", cell_value);

            if(group_id) {
                var group_start_addr = group_id_start_addrs[group_id];
                memory_map_cell.setAttribute("group-start-addr", toHexString(group_start_addr));

                $(memory_map_cell).hover(
                    create_hover_highlight_function_memory(group_id),
                    create_hover_unhighlight_function_memory(group_id)
                    );
            }

            return memory_map_cell;
        }

        function create_cell_base_row(start_addr){
            var hex_start_addr = toHexString(start_addr);
            var memory_map_row = document.createElement("tr");
            memory_map_row.setAttribute("start-addr", hex_start_addr);

            var td = document.createElement("td");
            td.className = "address-width";
            td.innerHTML = "&nbsp;";
            td.setAttribute("title", hex_start_addr);
            memory_map_row.appendChild(td);

            return memory_map_row;
        }

        function create_label_base_row(hex_start_addr) {
            var memory_map_row = document.createElement("tr");
            memory_map_row.setAttribute("start-addr", hex_start_addr);

            var td = document.createElement("td");
            td.className = "memory-map-address";
            td.innerHTML = hex_start_addr;
            td.setAttribute("title", hex_start_addr);
            memory_map_row.appendChild(td);

            return memory_map_row;
        }

        function create_memory_map_dot_row() {
            var dot_row = document.createElement("tr");

            var td = document.createElement("td");
            td.className = "dot-line";
            td.colSpan = "5";
            td.innerHTML = "•••";

            dot_row.appendChild(td);

            return dot_row;
        }

        function toggle_hex() {
            hex_mode_on = !hex_mode_on;

            // Have to bring out the right table to the front, to allow hovering
            $("table.memory-map-cell-table td.memory-map-cell").toggle();
            var cell_table_z = parseInt($("table.memory-map-cell-table").css("z-index"));
            $("table.memory-map-cell-table").css("z-index", cell_table_z == 1000 ? 0 : 1000);

            $("table.memory-map-label-table td.memory-map-cell").toggle();
            var label_table_z = parseInt($("table.memory-map-label-table").css("z-index"));
            $("table.memory-map-label-table").css("z-index", label_table_z == 1000 ? 0 : 1000);
        }

        function create_minimize_function(div_id) {
            return function() {
                if($(this).html() == "[-]") {
                    $(this).html("[+]");
                } else {
                    $(this).html("[-]");
                }

                $("#" + div_id + " tbody").fadeToggle();
            }
        }

        function stack_table_minimize_function() {
            if($(this).html() == "[-]") {
                $(this).html("[+]");
            } else {
                $(this).html("[-]");
            }

            $(this).parents("div.memory-map-table-wrapper").find("tbody").fadeToggle();
            $(this).parents("div.memory-map-table-wrapper").find("thead > tr:nth-child(2)").fadeToggle();
        }

        function find_elements_to_highlight(group_id) {
            var elements_to_highlight = [];

            var group_start_addr = group_id_start_addrs[group_id];
            var hex_group_start_addr = toHexString(group_start_addr);
            var name_table_row = $("div.name-type-section tr[data-address='" + hex_group_start_addr + "']");
            elements_to_highlight.push(name_table_row);

            var group = $("#stack-frame-tables td[group-id='" + group_id + "']");
            elements_to_highlight.push(group);

            // TODO: If it's a pointer, find all things down the chain of pointers and add them to the array

            return elements_to_highlight;
        }

        function create_hover_highlight_function_memory(group_id) {
            return function() {
                var elements_to_highlight = find_elements_to_highlight(group_id);

                var num_elements = elements_to_highlight.length;
                for(var i = 0; i < num_elements; i++) {
                    elements_to_highlight[i].addClass("highlight");
                }
            }
        }

        function create_hover_unhighlight_function_memory(group_id) {
            return function() {
                var elements_to_highlight = find_elements_to_highlight(group_id);

                var num_elements = elements_to_highlight.length;
                for(var i = 0; i < num_elements; i++) {
                    elements_to_highlight[i].removeClass("highlight");
                }
            }
        }

        function create_hover_highlight_function_names() {
            return function() {
                var group_start_addr = parseInt($(this).attr("data-address"), 16);
                var group_id = start_addrs_to_group_id[group_start_addr];

                var memory_map_group = $("#stack-frame-tables td[group-id='" + group_id + "']");

                $(this).addClass("highlight");
                memory_map_group.addClass("highlight");
            }
        }

        function create_hover_unhighlight_function_names() {
            return function() {
                var group_start_addr = parseInt($(this).attr("data-address"), 16);
                var group_id = start_addrs_to_group_id[group_start_addr];

                var memory_map_group = $("#stack-frame-tables td[group-id='" + group_id + "']");

                $(this).removeClass("highlight");
                memory_map_group.removeClass("highlight");
            }
        }

        function add_return_name_table(json_step) {
            //Add the new id to return_to_clr variable, so that it gets removed from the table on next step
            //Will always be on the stack
            var return_data;
            var table_name = json_step['function'];
            var cur_frame;
            cur_frame = $('#names-'+table_name);

            console.log("adding return to name table!");

            //Check if there's a current frame up for this:
            if(cur_frame.length == 0) {
            //If not, create a whole new name table - could be possible for a function with no vars that then returns
                $('#name-type-section').prepend('<span id="name-table-'+table_name+'"> <h4>'+table_name+'</h4> <table id="names-' +table_name+
                '" class="table table-bordered" style="width: 100%; float:left;">'+
                '<thead>'+
                    '<tr>'+
                    '<th width="60%">Name</th>' +
                    '<th width="40%">Type</th>' +
                    '</tr>' +
                '</thead>' +
                '<tbody id="name-body-'+table_name+'">' +
                '</tbody>' +
                '</table></span>');
            }

            if(json_step.hasOwnProperty('return')) {
                return_val = json_step["return"];
                return_data = 'Return <'+return_val+'>';
                most_recently_returned = json_step['function'];
            }
            else {
                //If this is the first time we're seeing this JSON step, the last value returned is stored in return_val and added to the JSON step
                if(!json_step.hasOwnProperty('return_val')) {
                    json_step["return_val"] = return_val;
                }
                return_data = json_step["returned_fn_call"]+' <'+json_step['return_val']+'>';
            }

            return_to_clr = '#'+table_name+'-return';
            console.log("want to add to "+table_name+ " and return data is "+return_data);
            //Add a row to the existing name table
            $('#name-body-'+table_name).append('<tr id="'+table_name+'-return"> <td colspan="2">' + return_data + '</td>' +
            '</tr>');
        }

        function add_to_val_list(json_step) {
        //value_list will contain all variables currently allocated, will look like: { "0x123": { value": ["xyz", "mzy" ...], "is_ptr": "T/F" } }

            //Loop through all var changes in the step
            for(var i=0; i<json_step['changed_vars'].length; i++) {

                var val_address = json_step['changed_vars'][i]["addr"];
                var ptr_size = null;
                if(json_step['changed_vars'][i]["new"]) {
                    var is_ptr_val = false;
                    if(json_step['changed_vars'][i].hasOwnProperty('is_ptr')) {
                        is_ptr_val = true;
                        ptr_size = json_step['changed_vars'][i]['ptr_size'];
                    }
                    new_value = {"value": [json_step['changed_vars'][i]["value"]], "is_ptr": is_ptr_val, "ptr_size":ptr_size};
                    value_list[val_address] = new_value;
                }

                //Case where variable is not new, was on the heap and got freed - push "#Freed#" onto the list as a marker that it's been freed
                else if((json_step['changed_vars'][i]['location']) == "Heap" && (json_step['changed_vars'][i].hasOwnProperty('freed'))) {
                    value_list[val_address]["value"].push("#Freed#");
                }

                //If the variable is not new and not freed, just push the new value onto its array
                else {
                    value_list[val_address]["value"].push(json_step['changed_vars'][i]["value"]);
                }
            }
        }

        function add_to_std_out(json_step) {
            //cur_stdout contains the full current stdout string that's been stepped to: will append to this and refresh the stdout window
            cur_stdout = cur_stdout.concat(json_step["std_out"]);
            console.log("cur stdout is " + cur_stdout);
            $("#std-out-textbox").html(cur_stdout);
        }


        //Applies the most recent backward-changes of the current step to the name table: the only time this might be
        //an addition is if a variable got freed on the heap in the last step, adding it back
        function remove_from_name_table(json_step) {
            var table_name;
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
                        $("#"+table_name+'-'+json_step['changed_vars'][i]['var_name']).remove();

                        //Check if the table is now empty from this removal, remove if so
                        table_id = '#names-'+table_name;
                        //check_rm_empty_table(table_id);
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
                        $('#name-type-section').prepend('<span id="name-table-Heap"><h4>Heap</h4> <table id="names-Heap"'+
                            'class="table table-bordered" style="width: 100%; float:left;">'+
                        '<thead>'+
                            '<tr>'+
                            '<th width="60%">Name</th>' +
                            '<th width="40%">Type</th>' +
                            '</tr>' +
                        '</thead>' +
                        '<tbody id="name-body-heap">' +
                        '</tbody>' +
                        '</table></span>');
                    }

                    //Add the new row to the existing heap name table
                    $('#name-body-heap').append('<tr id="heap-'+json_step['changed_vars'][i]['var_name']+'" data-address="'+
                        json_step['changed_vars'][i]['addr']+'">' +
                        '<td class="var-name hide-overflow" title="' + json_step['changed_vars'][i]['var_name'] + '">' + json_step['changed_vars'][i]['var_name'] + '</td>' +
                        '<td class="var-type hide-overflow" title="' + json_step['changed_vars'][i]['type'] + '">' + json_step['changed_vars'][i]['type'] + '</td>' +
                    '</tr>');
                }
            }
            //Do collapsing/expanding of tables here, make sure the table of the last var change is expanded
        }

        function reset_memory_tables() {
            largest_group_id = 1; // Not 0 because it would fail a check for adding the highlight functions
            $("#data-memory-map tbody").empty();
            $("#heap-memory-map tbody").empty();
            $("#stack-frame-tables").empty();
        }

        function remove_from_memory_table(json_step) {
            // Nuke all memory tables and rebuild them up to the previous step
            reset_memory_tables();

            var last_step = json_index-1;
            json_index = 0;
            for(var i=0; i <= last_step; i++) {
                var json_step = debugger_data["steps"][i];

                if(json_step.hasOwnProperty('on_entry_point')) {
                    // Create the empty table even before any variables get assigned
                    get_var_location('stack', json_step['function']);
                }

                if(json_step.hasOwnProperty('returned_fn_call')) {
                    // Remove the previous stack frame of this function
                    $("#stack-frame-tables div[stack-function='" + json_step['returned_fn_call'] + "']:first").remove();
                }

                if(json_step.hasOwnProperty('changed_vars')) {
                    add_to_memory_table_only(json_step);
                }
                json_index++;
            }

            // After we've inserted all the variables, we have to generate the corresponding label tables
            regenerate_all_label_tables();
        }

        function remove_from_val_list(json_step) {
        //value_list will contain all variables currently allocated, will look like: { "0x123": { value": "xyz", "is_ptr": "T/F" } }

            //Loop through all var changes in the step
            for(var i=0; i<json_step['changed_vars'].length; i++) {

                var val_address = json_step['changed_vars'][i]["addr"];

                if(json_step['changed_vars'][i]["new"]) {
                    delete value_list[val_address];
                }

                //Otherwise just pop the last value off the list
                else {
                    value_list[val_address]["value"].pop();
                }
            }
        }


        function remove_from_std_out(json_step) {
            //removes last n characters from cur_stdout
            len_to_rm = json_step["std_out"].length;
            cur_stdout = cur_stdout.substring(0, cur_stdout.length - len_to_rm);
            $("#std-out-textbox").html(cur_stdout);
        }

        function check_rm_empty_table(table_name) {
            //Check if a table is empty (has no rows in body)- if so, remove the whole table from the DOM
            //Call this any time a row is removed from a table
            var row_amt = $(table_name+" > tbody > tr").length;
            if (row_amt < 1) {
                $(table_name).parent().remove();
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
    for (i = 0; i < line_count; i++){
        //wrapClass = newCode.lineInfo(i).wrapClass;
        if (codeArray[i] == CryptoJS.SHA1(div_id.split("-")[1])) {
            code += "";
        }
        else {
            code += codeArray[i];
            //Check for the main function declaration, this is the line we should start
            //student steps from, if it is not hidden
        }
        code += '\n';
    }
    return code.substring(0, code.length-1);
}