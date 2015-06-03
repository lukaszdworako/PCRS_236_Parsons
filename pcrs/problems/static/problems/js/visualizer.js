var memory_map_cell_height = 37; // In pixels
var memory_map_cell_width = 17.5; // In %

function zeroPad (str, max) {
  str = str.toString();
  return str.length < max ? zeroPad("0" + str, max) : str;
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

function executeGenericVisualizer(option, data, newCode, newOrOld) {
    console.log("got to visualizer.js");
    var supportedVisualization = ['python', 'c'];
    var value_list = {};

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
                    //Clear the stack and heap tables
                    $('#name-type-section').empty();
                    $('#new_debugger_table_heap').empty();
                    update_new_debugger_table(debugger_data, "reset");
                });
            }

            //Clear the stack and heap tables
            $('#name-type-section').empty();
            $('#new_debugger_table_heap').empty();

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
                console.log("step:"+debugger_data["steps"][json_index]["step"]);
                console.log("in next, cur line is "+cur_line+"and json index is "+json_index);

                add_to_name_table(debugger_data["steps"][json_index]);
                add_to_memory_table(debugger_data["steps"][json_index]);
                add_to_val_list(debugger_data["steps"][json_index]);
            }

            else if(update_type == "prev") {
                console.log("json index:"+json_index);
                console.log("step:"+debugger_data["steps"][json_index]["step"]);
                console.log("in prev, cur line is "+cur_line+"and json index is "+json_index);
                //Process JSON here to go backward a line
                remove_from_name_table(debugger_data["steps"][json_index]);
                remove_from_memory_table(debugger_data["steps"][json_index]);
                remove_from_val_list(debugger_data["steps"][json_index]);
                json_index--;
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
                            $('#name-type-section').append('<span id="name-table-'+table_name+'"> <h4>'+table_name+'</h4> <table id="names-' +table_name+
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
            console.log('Adding to memory table');
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
            for(var i=0; i < changed_vars.length; i++) {
                var changed_var = changed_vars[i];

                var var_name = changed_var["var-name"];
                var addr = parseInt(changed_var["addr"], 16);
                var type = changed_var["type"];
                var is_new = changed_var["new"];
                var value = changed_var["value"];
                var invalid = changed_var["invalid"];
                var location = changed_var["location"];
                var cells_needed = changed_var["max_size"];

                if(location === "static") {
                    location = "#static-memory-map";
                } else if(location === "heap") {
                    location = "#heap-memory-map";
                } else if(location === "stack") {
                    if(is_new) {
                        // TODO: Create a new stack frame
                    } else {
                        // TODO: Find which function it belongs to
                    }
                }

                var is_array = type.indexOf("[]") >= 0;

                var memory_map_tbody = $(location + " > tbody");
                var table_rows = $(location + " > tbody > tr[start-addr]");
                if(table_rows.toArray().length > 0) {
                    // Find location to insert
                    var current_addr = addr;
                    var row_start_addr = current_addr - (current_addr % 4);
                    var all_addrs = table_rows.map(function() {
                        return parseInt($(this).attr("start-addr"), 16);
                    }).toArray();

                    var largest_smaller_addr = Math.max.apply(null, all_addrs);

                    var smaller_addrs = all_addrs.filter(function(value, index, ar){return (value < addr);});
                    if(smaller_addrs.length > 0) {
                        largest_smaller_addr = Math.max.apply(null, smaller_addrs);
                    }

                    // Either insert or modify
                } else {
                    // Insert the first element
                    insert_first_element_in_memory_map(memory_map_tbody, addr, cells_needed, value, is_array);
                }
            }
        }

        function insert_first_element_in_memory_map(memory_map_tbody, start_addr, cells_needed, value, is_array) {
            var end_addr = start_addr + cells_needed;

            var middle_cells = cells_needed;
            var rows_needed = (Math.floor(end_addr/4)) - (Math.floor(start_addr/4)) + 1;

            if(rows_needed > 1) {
                var start_addr_extra_cells = (start_addr % 4) == 0 ? 0 : 4 - (start_addr % 4);
                var end_addr_extra_cells = (end_addr % 4);
                middle_cells = (cells_needed - start_addr_extra_cells - end_addr_extra_cells);
            }


            var current_addr = start_addr;
            var remaining_cells = cells_needed;
            var label_added = false;
            for(var r=1; r <= rows_needed; r++) {
                var row_start_addr = current_addr - (current_addr % 4);
                var start_cell_number = current_addr % 4;
                var current_cell_addr = row_start_addr;

                var start_addr_str = zeroPad(row_start_addr.toString(16), 8);
                var memory_map_row = create_memory_map_base_row(start_addr_str);

                // Add the cells of this row
                var cells_on_row = Math.min(remaining_cells, (4 - start_cell_number));

                var c = 0;
                while(c < start_cell_number) {
                    var memory_map_cell = create_regular_memory_map_cell(current_cell_addr);
                    memory_map_row.appendChild(memory_map_cell);
                    current_cell_addr++;
                    c++;
                }
                while(c < (start_cell_number + cells_on_row)) {
                    var cols = 2;
                    // Add the label cell
                    if((!label_added) && (!is_array)
                        && ((rows_needed < 3) || (current_cell_addr == row_start_addr))) {
                        var label_height_cells = Math.max((middle_cells / 4), 1);
                        var label_width_cells = cells_on_row;
                        var label_value = value;

                        var label_cell = create_label_cell(label_height_cells, label_width_cells, label_value);
                        memory_map_row.appendChild(label_cell);
                        cols = 1;
                        label_added = true;
                    }

                    // Add the data cells
                    var clarity_class = "clear-memory-map-cell";
                    if(rows_needed > 1){
                        // First row
                        if(r == 0) {
                            clarity_class = "top-row-clear-cell";
                        } else if(r == rows_needed) {
                            clarity_class = "bottom-row-clear-cell";
                        } else {
                            clarity_class = "middle-row-clear-cell";
                        }
                    }

                    var memory_map_cell = create_clear_memory_map_cell(current_cell_addr, clarity_class, cols);
                    memory_map_row.appendChild(memory_map_cell)
                    current_cell_addr++;
                    c++;
                }
                while(c < 4) {
                    var memory_map_cell = create_regular_memory_map_cell(current_cell_addr);
                    memory_map_row.appendChild(memory_map_cell);
                    current_cell_addr++;
                    c++;
                }

                memory_map_tbody.append(memory_map_row);

                // Advance to the next row
                current_addr = row_start_addr + 4;
                remaining_cells -= cells_on_row;
            }
        }

        function create_label_cell(label_height_cells, label_width_cells, label_value) {
            var label_cell = document.createElement("td");
            var label_height = (label_height_cells * memory_map_cell_height).toString() + "px";
            var label_width = (label_width_cells * memory_map_cell_width).toString() + "%";

            label_cell.className = "cell-label-td";
            label_cell.style.height = label_height;
            label_cell.style.width = label_width;
            label_cell.style.maxWidth = label_width;

            var label_cell_div = document.createElement("div");
            label_cell_div.className = "cell-label-div";
            label_cell_div.style.height = label_height;
            label_cell_div.innerHTML = label_value;

            label_cell.appendChild(label_cell_div);

            return label_cell;
        }

        function create_clear_memory_map_cell(cell_addr, clarity_class, cols) {
            var memory_map_cell = document.createElement("td");
            memory_map_cell.className = clarity_class;
            memory_map_cell.setAttribute("colspan", cols);
            memory_map_cell.setAttribute("addr", cell_addr.toString(16,8));

            return memory_map_cell;
        }

        function create_regular_memory_map_cell(cell_addr) {
            var memory_map_cell = document.createElement("td");
            memory_map_cell.className = "memory-map-cell";
            memory_map_cell.setAttribute("colspan", "2");
            memory_map_cell.setAttribute("addr", cell_addr.toString(16,8));

            return memory_map_cell;
        }

        function create_memory_map_base_row(start_addr) {
            var memory_map_row = document.createElement("tr");
            memory_map_row.setAttribute("start-addr", start_addr);

            var td = document.createElement("td");
            td.className = "memory-map-address";
            td.innerHTML = "0x" + start_addr;
            memory_map_row.appendChild(td);

            return memory_map_row;
        }

        function create_memory_map_break_row() {
            var break_row = document.createElement("tr");

            var td1 = document.createElement("td");
            td1.className = "memory-break-line-addr";

            var td2 = document.createElement("td");
            td2.className = "memory-break-line";
            td2.colSpan = "8";

            break_row.appendChild(td1);
            break_row.appendChild(td2);

            return break_row;
        }

        function add_return_to_memory_table(json_step) {
            // TODO: implement
        }


        function add_to_val_list(json_step) {
        //value_list will contain all variables currently allocated, will look like: { "0x123": { value": ["xyz", "mzy" ...], "is_ptr": "T/F" } }
            if(!json_step.hasOwnProperty('changed_vars')) {
                return;
            }
            //Loop through all var changes in the step
            for(var i=0; i<json_step['changed_vars'].length; i++) {

                var val_address = json_step['changed_vars'][i]["addr"]; 
                
                if(json_step['changed_vars'][i]["new"]) {
                    var is_ptr_val = false;
                    if(json_step['changed_vars'][i].hasOwnProperty('is_ptr')) {
                        is_ptr_val = true;
                    } 
                    new_value = {"value": [json_step['changed_vars'][i]["value"]], "is_ptr": is_ptr_val}
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
                        $("#"+table_name+'-'+json_step['changed_vars'][i]['var_name']).remove();

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
                        $('#name-type-section').append('<span id="name-table-Heap"><h4>Heap</h4> <table id="names-Heap"'+
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
        //value_list will contain all variables currently allocated, will look like: { "0x123": { value": "xyz", "is_ptr": "T/F" } }
            if(!json_step.hasOwnProperty('changed_vars')) {
                return;
            }
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
