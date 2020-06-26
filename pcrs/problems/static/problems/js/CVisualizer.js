/*
 * NOTE: We are now using polymorphism to handle language specific visualizers.
 * Eventually, in this file should be a method in the below class.
 */

function CVisualizer() {
    Visualizer.call(this);
    this.language = 'c';
}
CVisualizer.prototype = Object.create(Visualizer.prototype);
CVisualizer.prototype.constructor = CVisualizer;

/**
 * @override
 */
CVisualizer.prototype._showVisualizerWithData = function(data) {
    executeCVisualizer("create_visualizer", data, this.code);
}

/**
 * @override
 */
CVisualizer.prototype._generatePostParams = function() {
    var postParams = Visualizer.prototype._generatePostParams.apply(this, arguments);
    executeCVisualizer("gen_execution_trace_params", postParams, this.code);
    return postParams;
}

//
//
// LEGACY VISUALIZER CODE FORMAT BEGINS HERE
//
//

var debugger_id = ""; // Set in CSubmissionWrapper

var last_stepped_line_debugger = 0;
var c_debugger_load = false;
var debugger_data = null;
var debugger_index = 0;

// These global variables should not be modified
//---
var memory_map_cell_height = 37; // In pixels
var address_width = 45 // In %
var memory_map_cell_width = 13.75; // In %
//---

// These global variables will change throughout the program
//---
var cur_stdout = "";
var return_to_clr = "";
var return_val;
//Function we've most recently returned from
var most_recently_returned = "";
//Function we've most recently entered: keep track of this for if we hit prev
var most_recently_entered = "";

// Used for the memory map
var largest_array_id;
var largest_group_id;
var array_id_counter;
var group_id_vals = {};
var group_id_to_type = {};
var group_id_to_start_addr = {};
var start_addr_to_group_id = {};
var var_name_to_group_id = {};
var group_id_to_var_name = {};
var group_id_to_array_id = {};
var array_id_to_group_id = {};
var value_list = {};
var name_table_vars = {};

// Keeps track of how many stack frames have been created for a function
var stack_frame_levels = {};

// Keeps track of addresses that have been freed and are unusable
var free_list = {};

var hex_mode_on = false;
//---

/**
 * Generate a Hashkey based on
 * the problem_id to identify
 * where the student code starts and ends
 */
function removeHashkeyForDisplay(div_id, newCode) {
    var codeArray = newCode.split('\n');
    var line_count = codeArray.length;
    var hash_code = CryptoJS.SHA1(div_id.split("-")[1]);
    var code = "";
    var i;
    for (i = 0; i < line_count; i++){
        //wrapClass = newCode.lineInfo(i).wrapClass;
        if (codeArray[i] == hash_code) {
            continue;
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

function zeroPad(str, max) {
  str = str.toString();
  return str.length < max ? zeroPad("0" + str, max) : str;
}

function toHexString(hexnum, max) {
    max = typeof max !== 'undefined' ? max : 16;
    var str_hex_num = hexnum.toString(16);
    if(str_hex_num.indexOf("0x") === 0) {
        str_hex_num = str_hex_num.substr(2);
    }

    return "0x" + zeroPad(str_hex_num, max);
}

function hexToFloat(hexstring, type) {
    if(type === 'float') {     // Assuming 32-bit base values
        var size = 4;
    } else {
        var size = 8;
    }
    var buffer = new ArrayBuffer(size);
    var byteArr = new Uint8Array(buffer);
    if(type === 'float') {
        var val = new Float32Array(buffer);
    } else { // double of some sort -- and you're out of luck, "long double"
        var val = new Float64Array(buffer);
    }

    var i = 0;
    for(; i < hexstring.length; i += 2) {
        byteArr[size -1 - i / 2] = "0x" + hexstring.substr(i, 2);
    }

    return val[0].toFixed(6);
}

function hexToInt(hexstring) {
    // Javascript can't easily handle longs, because it doesn't have a 64 bit int type.
    hexstring = hexstring.slice(-12)   // Doing our best. Taking the last 48 bits.
    var binary_string = zeroPad(parseInt(hexstring, 16).toString(2), hexstring.length*4);
    var first_bit = binary_string[0];
    var magnitude = first_bit === '1' ? ~parseInt(binary_string, 2) + 1 : parseInt(binary_string, 2);
    return (first_bit === '1' ? '-' : '') + magnitude;
}

function hexToUnsignedInt(hexstring) {
    return parseInt(hexstring, 16);
}
function hexToChar(hexstring) {
    return String.fromCharCode(parseInt(hexstring, 16));
}
function hexToCharArray(hexstring) {
    hexstring = hexstring.toString().replace(/0x/g, ''); // Force conversion
    var str = [];
    for (var i = 0; i < hexstring.length; i += 2) {
        str.push(hexToChar(hexstring.substr(i, 2)));
    }

    return str;
}

function isDotRow(tr) {
    return tr.find("td.dot-line").length > 0;
}

function canFreeRow(tr, array_id) {
    return tr.find("td.memory-map-cell").filter(function() {
        return $(this).attr('array-id') == array_id || !$(this).attr('group-id');
    }).length == 4;
}

function repeat_string(str, count) {
    if (count < 1) {
        return '';
    }

    var result = '';
    while(count > 1) {
        count--;
        result += str;
    }
    return result + str;
}


/**
 * C visualizer representation.
 */
function executeCVisualizer(option, data, newCode) {
    switch(option) {
        case "create_visualizer":
            if( ! errorsInTraceC(data)) {
                    createVisualizer(data, newCode);
            }
            break;
        case "gen_execution_trace_params":
            getExecutionTraceParams(data);
            break;
        default:
            throw new Error('option not supported');
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
        value_list = {};
        name_table_vars = {};
        debugger_data = data;
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

            $('#nameTableDetailsModal div.pcrs-modal-footer button').click(function() {
                $("#newvisualizerModal").css("z-index", 1050);
                $("#nameTableDetailsModal").modal('hide');
            });

            // Bind debugger buttons
            $('#new_previous_debugger').bind('click', function () {
                if (json_index > 0) {
                    last_stepped_line_debugger = cur_line;
                    cur_line = debugger_data["steps"][json_index-1]["student_view_line"]-1;
                    update_new_debugger_table(debugger_data, "prev");
                } else {
                    last_stepped_line_debugger = cur_line;
                    cur_line = start_line-2;
                    json_index = -1;
                    // Reset the memory map tables
                    reset_memory_tables();

                    // Clear the name tables
                    $('#name-table-data tbody').empty();
                    $('#name-type-section').empty();
                    $('#new_debugger_table_heap').empty();

                    //Clear stdout
                    cur_stdout= "";
                    $("#std-out-textbox").html(cur_stdout);
                    myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');

                    // Re-add the global variables
                    add_globals();

                    // Reset the code in the CodeMirror window
                    myCodeMirrors[debugger_id].setValue(codeToShow);
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
                cur_line = start_line-2;
                json_index = -1;
                // Reset the memory map tables
                reset_memory_tables();

                // Clear the name tables
                $('#name-table-data tbody').empty();
                $('#name-type-section').empty();
                $('#new_debugger_table_heap').empty();
                //clear val list
                value_list = {};
                name_table_vars = {};
                //Clear stdout
                cur_stdout= "";
                $("#std-out-textbox").html(cur_stdout);
                myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');

                myCodeMirrors[debugger_id].setValue(codeToShow);

                add_globals();
            });

            $("#font_size_up").bind('click', function () {
                var code_window =  $("div#preview-code");
                var font_size = parseInt(code_window.css('font-size'));
                code_window.css('font-size', font_size+1 + 'px');

                myCodeMirrors[debugger_id].refresh();
            });
            $("#font_size_down").bind('click', function () {
                var code_window =  $("div#preview-code");
                var font_size = parseInt(code_window.css('font-size'));

                if(font_size > 0) {
                    code_window.css('font-size', font_size-1 + 'px');
                }

                myCodeMirrors[debugger_id].refresh();
            });
            $("#font_size_default").bind('click', function () {
                $("div#preview-code").css('font-size', '14px');
                myCodeMirrors[debugger_id].refresh();
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
        $('#name-table-data tbody').empty();
        $('#name-type-section').empty();
        $('#new_debugger_table_heap').empty();

        cur_stdout= "";
        $("#std-out-textbox").html(cur_stdout);

        //Codemirror starts line count at 0, subtract 1 from start line so it's accurate
        cur_line = start_line-2;
        json_index = -1;
        last_stepped_line_debugger = -1;

        myCodeMirrors[debugger_id].setValue(codeToShow);

        $('#newvisualizerModal').modal('show');

        // Uncomment when a way is figured out to separate variables (instead of highlighting all with the same name)
        //add_hover_to_code();
        add_globals();

    }

    function add_hover_to_code() {
        $('div.code-window-section span.cm-variable').each(function() {
            $(this).on({
                mouseenter: create_hover_highlight_function_code(),
                mouseleave: create_hover_unhighlight_function_code()
            });
        });
    }

    function update_new_debugger_table(data, update_type) {
        myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');
        myCodeMirrors[debugger_id].addLineClass(cur_line, '', 'CodeMirror-activeline-background')
        if((json_index+1 < debugger_data["steps"].length)
            && (debugger_data["steps"][json_index+1]['on_entry_point'])) {

            var function_call_line = parseInt(debugger_data["steps"][json_index+1]["student_view_line"]-1);
            myCodeMirrors[debugger_id].addLineClass(function_call_line, '', 'CodeMirror-activeline-background');
        }

        // Uncomment when a way is figured out to separate variables (instead of highlighting all with the same name)
        //add_hover_to_code();

        //Removes any name table rows that must be removed with this step
        $(return_to_clr).remove();
        return_to_clr = "";

        var json_step = debugger_data["steps"][json_index];
        if((update_type == "next")) {
            if(json_step['on_entry_point']) {
                // Create the empty table even before any variables get assigned
                get_var_location('stack', json_step['function'], undefined, true);

                add_first_name_table(json_step);
                $("#name-table-"+json_step['function']).show()
                most_recently_entered = json_step['function'];
            }

            //Case where there's changed variables
            if(json_step.hasOwnProperty('changed_vars')) {
                add_step_to_all_tables(json_step);
            }
            //Case where it's a function return
            if((json_step.hasOwnProperty('return')) || (json_step.hasOwnProperty('returned_fn_call'))) {
                add_return_name_table(json_step);
            }

            if(json_step.hasOwnProperty('returned_fn_call')) {
                // Remove the previous stack frame and name table of this function
                $("#name-table-"+most_recently_returned).remove();
                remove_stack_table(json_step['returned_fn_call'])
                to_remove_stack = name_table_vars[most_recently_returned]
                to_remove_stack[to_remove_stack.length -1].push(['return'])
            }

            //Case where it has standard output
            if(json_step.hasOwnProperty('std_out')) {
                add_to_std_out(json_step);
            }
        }

        else if(update_type == "prev") {
            // This just recreates the memory tables from the beginning up to one step before
            remove_from_memory_table();

            check_rm_return_nametable(json_step);

            //Process JSON here to go backward a line
            if(json_step.hasOwnProperty('changed_vars')) {
                remove_from_name_table(json_step);
                remove_from_val_list(json_step);
                //Case where it's a function return
            }
            //Case where it has standard output
            if(json_step.hasOwnProperty('std_out')) {
                remove_from_std_out(json_step);
            }
            json_index--;
            json_step = debugger_data["steps"][json_index];
            if(json_step.hasOwnProperty('return') || json_step.hasOwnProperty('returned_fn_call') ) {
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

            if((json_index+1 < debugger_data["steps"].length)
                && (debugger_data["steps"][json_index+1]['on_entry_point'])) {

                var function_call_line = parseInt(debugger_data["steps"][json_index+1]["student_view_line"]-1);
                myCodeMirrors[debugger_id].addLineClass(function_call_line, '', 'CodeMirror-activeline-background');
            }

            if((json_index+2 < debugger_data["steps"].length)
                && (debugger_data["steps"][json_index+2]['on_entry_point'])) {

                var function_call_line = parseInt(debugger_data["steps"][json_index+2]["student_view_line"]-1);
                myCodeMirrors[debugger_id].removeLineClass(function_call_line, '', 'CodeMirror-activeline-background');
            }
        }

        if((most_recently_entered != "") && (!json_step.hasOwnProperty('on_entry_point'))) {
            most_recently_entered = "";
        }
    }

    function add_step_to_all_tables(json_step) {
        // Have to add to memory table first to update the start_addr_to_group_id table, which the name table uses
        add_to_val_list(json_step);
        add_to_memory_table(json_step);
        add_to_name_table(json_step);
    }

    function add_globals() {
        globals = debugger_data["global_vars"];
        global_amt = globals.length;
        for(var i = 0; i < global_amt; i++) {
            //Include global vars
            var global_var = globals[i];

            var this_struct_level = (globals[i]['struct_levels']) && globals[i]['struct_levels'].length;
            var next_struct_level = (i+1 < global_amt && globals[i+1]['struct_levels']) ?
                                        globals[i+1]['struct_levels'].length
                                        : undefined;

            var is_last_struct_var = (i+1 == global_amt)
                                    || (this_struct_level && next_struct_level && (next_struct_level < this_struct_level));

            var var_group_id = get_var_group_id(global_var);
            add_one_var_to_val_list(global_var);
            add_one_var_to_memory_table(global_var, "", var_group_id);
            add_one_var_to_name_table(global_var, "", is_last_struct_var);
        }

        // Draw the label tables after all variables have been added
        regenerate_all_label_tables();
    }


    function update_debugger_table(data) {

        $('#debugger_table_stack').empty();
        $('#debugger_table_heap').empty();
        myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger, '', 'CodeMirror-activeline-background');
        for(var i = 0; i < data[debugger_index].length; i++) {
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
        var num_changed_vars = json_step['changed_vars'].length;
        for(var i=0; i<num_changed_vars; i++) {
            var this_struct_level = (json_step['changed_vars'][i]['struct_levels'])
                                        && json_step['changed_vars'][i]['struct_levels'].length;
            var next_struct_level = (i+1 < num_changed_vars && json_step['changed_vars'][i+1]['struct_levels']) ?
                                        json_step['changed_vars'][i+1]['struct_levels'].length
                                        : undefined;

            var is_last_struct_var =(i+1 == num_changed_vars)
                                    || (this_struct_level && next_struct_level && (next_struct_level < this_struct_level));

            add_one_var_to_name_table(json_step['changed_vars'][i], json_step['function'], is_last_struct_var);
        }
        //Do collapsing/expanding of tables here, make sure the table of the last var change is expanded
    }

    function add_one_var_to_name_table(changed_var, func_name, is_last_struct_var) {
        //Check if it's new - if so, adding it
        if (changed_var['location'] == "heap"
            || !changed_var['var_name']
            || changed_var['free']
            ) {
            // Ignore calls to free and adding of heap variables (because they don't have a name table)
            return;
        }

        if(changed_var['new']) {

            //If the variable is a pointer, only add it if its marked to show up in the name table
            if(!(changed_var.hasOwnProperty('is_ptr')) || (changed_var['is_ptr']=="name")) {

                //Check if it's in the stack, heap, or data to decide what we're looking for
                if(changed_var['location'] == "stack") {
                    table_name = func_name;
                } else {
                    table_name = 'data';
                }

                var cur_frame = $('#names-'+table_name+':first'); // Only take the top stack frame with this name

                // Check if there's a current frame up for this:
                var stack_frame_level = 1;
                if(cur_frame.length == 0) {
                    // If not, create a new stack frame for it
                    stack_frame_level = stack_frame_levels[table_name];
                    add_name_table_frame(table_name, stack_frame_level);
                }

                var name_tbody = $('#name-body-' + table_name);
                var insert_row = name_tbody.find("> tr:last");
                var var_name = changed_var['var_name'];

                // Create the different struct levels
                var struct_levels = changed_var['struct_levels'];
                var struct_parent = "";
                var level = 0;
                if(struct_levels) {
                    var level_delim = "";
                    var struct_tr = "", level_name = "";
                    for(var i = 0; i < struct_levels.length-1; i++) {
                        // Create a row for each level
                        level_name = struct_levels[i];
                        var var_id = struct_parent ? struct_parent + '.' + struct_levels[i] : struct_levels[i];

                        // Use level for the depth
                        struct_tr = create_name_table_row(var_id, level_name, "", "", struct_parent, true, level, false);

                        // Don't add new rows for existing hierarchies
                        var row_exists = $("tr[id='" + var_id + "']").length > 0;
                        if(!row_exists) {
                            if(insert_row.length > 0) {
                                insert_row.after(struct_tr);
                                insert_row = insert_row.next();
                            } else {
                                name_tbody.append(struct_tr);
                                insert_row = name_tbody.find("> tr:last");
                            }
                        }

                        // Update the parent name
                        struct_parent = var_id;

                        level++;
                    }

                    var_name = struct_levels[i];
                }

                // Add a row to the existing name table
                var name_tr = create_name_table_row(changed_var['var_name'], var_name, changed_var['type'], changed_var['addr'], struct_parent, false, level, is_last_struct_var);

                if(insert_row.length > 0) {
                    insert_row.after(name_tr);
                } else {
                    name_tbody.append(name_tr);
                }

                name_of_stack = func_name+'-'+stack_frame_level
                current_stack = name_table_vars[name_of_stack]
                //If the stack frame doesn't exist in name_table_vars yet add it
                if (!current_stack){
                    name_table_vars[name_of_stack] = []
                    current_stack = name_table_vars[name_of_stack]
                }

                current_frame = current_stack[current_stack.length -1]
                //If there are no frames for this stack yet
                if (!current_frame) {
                    current_stack.push([])
                    current_frame = current_stack[0]
                }
                //Create a new frame within the stack
                if ((current_frame[current_frame.length -1])&&(current_frame[current_frame.length -1][0] === "return") && (current_frame[current_frame.length -1].length === 1)){
                    current_stack.push([])
                    current_frame = current_stack[current_stack.length -1]
                }

                //Now append the var name and type to the dictionary
                current_frame.push([changed_var['var_name'],changed_var['type']])

                var name_row = $('#name-body-'+table_name+":first tr[id='"+changed_var['var_name']+"']");

                var group_start_addr = parseInt(name_row.attr("data-address"), 16);
                var name_row_group_id = start_addr_to_group_id[group_start_addr];
                name_row.hover(
                    create_hover_highlight_function(name_row_group_id),
                    create_hover_unhighlight_function(name_row_group_id)
                    );
            }
        }
    }

    function create_name_table_row(var_id, var_name, var_type, var_addr, struct_parent, has_children, depth, is_last) {
        var clean_name = var_name.replace(/\|| /g,'')
        var shade_width = depth * 15; // In px
        var shade_style = 'style="display: none;"';
        var img = "";

        if(depth > 0) {
            shade_style = 'style="width: '+shade_width+'px;"'
            img = "t-level-line.png";
        }

        if(is_last) {
            // TODO: Insert the appropriate image in the space cell
            img = "l-level-line.png";
        }

        var tr =
        $('<tr id="' + var_id + '" data-address="' + var_addr + '" struct-parent="' + struct_parent + '">' +
            '<td class="var-name hide-overflow" title="' + var_id + '">' +
                // An inner table is used to more finely divide up this individual cell
                '<table class="table table-no-border name-label-inner-table">' +
                    '<tbody>' +
                        '<tr>' +
                            '<td class="name-label-inner-td-space" ' + shade_style + '>' +
                                '<img class="name-table-level-line" src="/static/problems/img/' + img + '" />' +
                            '</td>' +
                            '<td class="name-label-inner-td">' +
                                var_name +
                            '</td>' +
                        '</tr>' +
                    '</tbody>' +
                '</table>' +
            '</td>' +
            '<td class="var-type hide-overflow" title="' + var_type + '">'
                + var_type +
            '</td>' +
        '</tr>');

        // Add a function to show and hide its children
        if(has_children) {
            var target_struct_parent = struct_parent ? struct_parent + '.' + clean_name : clean_name;
            tr.click(create_toggle_struct_function(target_struct_parent));
            tr.addClass('cursor-to-hand');
        }

        return tr;
    }

    function create_toggle_struct_function(target_struct_parent) {
        return function() {
            $("div.name-type-section tr[struct-parent]").filter(function() {
                return $(this).attr('struct-parent') == target_struct_parent
                        && $(this).attr('id').indexOf(target_struct_parent+'.') == 0;
            }).fadeToggle();
        }
    }

    function add_name_table_frame(table_name, stack_frame_num) {
        var table_id = 'name-table-' + table_name + '-' + stack_frame_num;
        var new_name_table = $(
        '<span id="'+table_id+'">' +
        '<table id="names-'+table_name+'" class="table table-bordered" style="width: 100%; float:left;">' +
        '<thead>' +
            '<tr>' +
             '<th title="Open expanded table view" colspan=2 class="names-stack-header cursor-to-hand">' +
                '<table class="table names-stack-header-table">' +
                    '<tbody>' +
                        '<tr>' +
                            '<td class="names-stack-header-label">' +
                                table_name +
                            '</td>' +
                            '<td class="names-stack-header-frame-num">' +
                                stack_frame_num +
                            '</td>' +
                        '</tr>' +
                    '</tbody>' +
                '</table>' +
             '</th>' +
            '</tr>' +

            '<tr>' +
                '<th width="50%">Name</th>' +
                '<th width="50%">Type</th>' +
            '</tr>' +
        '</thead>' +
        '<tbody id="name-body-'+table_name+'">' +
        '</tbody>' +
        '</table></span>');

        // Add expansion function
        new_name_table.find("th:first").click(create_expand_name_table_function(table_id));

        $('#name-type-section').prepend(new_name_table);
    }

    function create_expand_name_table_function(table_id) {
        return function() {
            // Make a copy of the table to put in the modal window
            var name_table_copy = $("#"+table_id).clone();

            // Remove the click and hover behaviours
            name_table_copy.find("*").removeClass("cursor-to-hand");
            name_table_copy.find("*").unbind("click");
            name_table_copy.find("*").unbind("mouseenter mouseleave")

            // Remove ids
            name_table_copy.find("*").removeAttr("id");

            // Put table info into modal window
            var name_modal_body = $("#nameTableDetailsDiv").find("div.pcrs-modal-body");
            name_modal_body.empty();
            name_modal_body.prepend(name_table_copy);

            // Open modal window with table info
            $("#newvisualizerModal").css("z-index", 500);
            $("#nameTableDetailsModal").modal({
                "show": true,
                "backdrop": false
            });
        };
    }

    function add_first_name_table(json_step) {
        var table_name = json_step['function'];
        var stack_frame_level = stack_frame_levels[table_name];

        // Always add this first table, since this function is only called on the entry point
        add_name_table_frame(table_name, stack_frame_level);
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
            var var_group_id = get_var_group_id(changed_vars[i]);

            if(changed_vars[i]['free']) {
                free_one_var_from_memory_table(changed_vars[i]);
            } else {
                var addr = changed_vars[i]["addr"];
                if(free_list[addr]) {
                    // If this address has been freed, do not add the variable but do update the value
                    // If we're remallocing, get the old value and remove the address from free_list
                    if(changed_vars[i]["location"].toLowerCase() === "heap") {
                        add_one_var_to_memory_table(changed_vars[i], func_name, var_group_id);
                    } else {
                        // Update the value, even if we're not showing the variable
                        free_list[addr] = {
                            "value": changed_vars[i]['value'],
                            "hex_value": changed_vars[i]['hex_value'],
                        }
                    }
                } else {
                    add_one_var_to_memory_table(changed_vars[i], func_name, var_group_id);
                }
            }
        }

        // After adding all variables to the table and finalizing their group-ids, add their highlight functions
        add_hover_highlight_to_cells();
    }

    function clear_group_id_maps(group_id) {
        // Clear all maps that use this group_id as a key
        delete group_id_vals[group_id];
        delete group_id_to_type[group_id];
        delete group_id_to_start_addr[group_id];
        delete group_id_to_var_name[group_id];
        delete group_id_to_array_id[group_id];
    }

    function free_one_var_from_memory_table(changed_var) {
        // Remove one variable from the memory map
        var hex_start_addr = changed_var['addr'];
        var start_addr = parseInt(hex_start_addr, 16);

        var first_cell = $("div.memory-map-section td[addr='" + hex_start_addr + "']:first");
        var array_id = first_cell.attr('array-id');
        var current_row = first_cell.parents('tr:first');


        // Find all the groups in this array (representing malloced addresses) and add them to the free list
        for(var arr_group_id in group_id_to_array_id) {
            if(group_id_to_array_id.hasOwnProperty(arr_group_id) && group_id_to_array_id[arr_group_id] == array_id) {
                var arr_hex_addr = toHexString(group_id_to_start_addr[arr_group_id]);
                var arr_val = value_list[arr_hex_addr];

                free_list[arr_hex_addr] = {
                    "value": arr_val['value'],
                    "hex_value": arr_val['hex_value'],
                }
            }
        }

        // Clear the map that uses this array id as a key
        delete array_id_to_group_id[array_id];

        // Remove all applicable entries in the various maps
        // Deal with only the unique group-ids
        var seen_group_ids = [];
        $("td.memory-map-cell[array-id='" + array_id + "']").each(function(){
            var group_id = $(this).attr('group-id');
            if($.inArray(group_id, seen_group_ids) === -1) {
                seen_group_ids.push(group_id);
                clear_group_id_maps(group_id);
            }
        });


        // Go through all rows in the memory map and either remove entire rows, or just blank out cells
        // Remove rows when all cells on the row are either part of this malloced memory, or have no group
        while(current_row.length !== 0 && !isDotRow(current_row)) {
            if(canFreeRow(current_row, array_id)) {
                // Remove an extra dot row if it exists
                if(isDotRow(current_row.prev()) && isDotRow(current_row.next())) {
                    current_row.next().remove();
                }

                // Remove this row and move on to the next one
                var next_row = current_row.next();
                current_row.remove();
                current_row = next_row

            } else {
                // Remove only the cells that need to be removed
                current_row.find("td[array-id='" + array_id + "']").map(
                    // Replace with an empty cell but with the same addr and title
                    function () {
                        $(this).replaceWith($(
                            "<td" +
                            " class='memory-map-cell uninitialized' " +
                            " uninitialized='true'" +
                            " title='" + $(this).attr('title') + "'" +
                            " addr='" + $(this).attr('addr') + "'" +
                            "></td>"
                            ))
                    });

                current_row = current_row.next();
            }
        }

        // Remove extra dot rows at the beginning and end
        var first_heap_row = $("div#heap-memory-map table.memory-map-cell-table tbody tr:first");
        if(isDotRow(first_heap_row)) {
            first_heap_row.remove();
        }
        var last_heap_row = $("div#heap-memory-map table.memory-map-cell-table tbody tr:last");
        if(isDotRow(last_heap_row)) {
            last_heap_row.remove();
        }
    }

    function add_one_var_to_memory_table(changed_var, func_name, group_id, array_id) {
        // Inner array values will be added later
        var addr = changed_var["addr"];
        var on_heap = changed_var["location"].toLowerCase() === "heap"
        var is_array = Boolean(changed_var["array"]);
        if(free_list[addr] && !is_array && on_heap) {
            // Restore the values when an address is being re-malloced
            changed_var["value"] = free_list[addr]["value"];
            changed_var["hex_value"] = free_list[addr]["hex_value"];

            // Remove from the free_list, because the address is not free anymore
            delete free_list[addr];
        }

        // Store values for use later
        var var_name = changed_var["var_name"];
        var type = changed_var["type"];
        var start_addr = parseInt(changed_var["addr"], 16);
        var value = changed_var["value"];
        var func_location = changed_var["location"];
        var cells_needed = parseInt(changed_var["max_size"]);
        var is_new = Boolean(changed_var["new"]);
        var is_uninitialized = Boolean(changed_var["uninitialized"]);
        var is_top_level = Boolean(changed_var["array_top_level"]);

        var location = get_var_location(func_location, func_name, start_addr);

        // Don't continue if we have nowhere to add the variable, to prevent the browser hanging indefinitely
        if(!location){
            return;
        }

        if(value.constructor === Array) {
            var array_group_id = group_id;

            // Top level of a nested array
            if(var_name) {
                var_name_to_group_id[var_name] = array_group_id;
                group_id_to_var_name[array_group_id] = var_name;
            }

            if(is_top_level) {
                array_id_counter = array_group_id;
            }

            if(!array_id) {
                array_id = get_var_array_id(array_group_id);

                group_id_to_array_id[array_group_id] = array_id;
                array_id_to_group_id[array_id] = array_group_id;
            }

            // Treat each value in the array as its own variable and insert individually, but with the same array-id
            for(var i = 0; i < value.length; i++) {
                add_one_var_to_memory_table(value[i], func_name, array_id_counter, array_id);

                if(value[i]["value"].constructor !== Array) {
                    // Group ids in arrays should be sequential because we can't assign names to inner arrays
                    array_id_counter++;
                    if(array_id_counter > largest_group_id) {
                        largest_group_id++;
                    }
                }
            }

        } else {
            // Insert a single variable with a regular value, not an array

            var hex_value = changed_var["hex_value"].match(/.{1,2}/g).slice(1); // Turn into array of 1-byte hex values

            // Update all the relevant info maps
            group_id_vals[group_id] = value;
            group_id_to_type[group_id] = type;

            group_id_to_start_addr[group_id] = start_addr;
            start_addr_to_group_id[start_addr] = String(group_id);

            if(array_id) {
                group_id_to_array_id[group_id] = array_id;
            }

            if(var_name) {
                var_name_to_group_id[var_name] = group_id;
                group_id_to_var_name[group_id] = var_name;
            }

            // Add the cell rows first
            var new_var_cell_rows = $(create_new_var_cell_rows(group_id, start_addr, cells_needed, value, hex_value, is_uninitialized, array_id));

            // Append as the first element if nothing else is in the table right now
            var simply_append_rows = location.find(" > table.memory-map-cell-table > tbody td[addr]").length == 0;

            insert_cell_rows(location, start_addr, cells_needed, new_var_cell_rows, simply_append_rows);
        }
    }

    function create_new_var_cell_rows(group_id, start_addr, cells_needed, value, hex_value, is_uninitialized, array_id) {
        var end_addr = start_addr + cells_needed - 1;
        var rows_needed = (Math.floor(end_addr/4)) - (Math.floor(start_addr/4)) + 1;

        // Create the rows
        var cell_rows = document.createElement("div");

        var hex_val_index = 0;
        hex_value = hex_value.slice(-cells_needed);
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

                var memory_map_cell = create_cell_cell(current_cell_addr, "", cell_hex_val, "", is_uninitialized, array_id);
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

                var memory_map_cell = create_cell_cell(current_cell_addr, group_id, hex_value[hex_val_index], clarity_classes, is_uninitialized, array_id);
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

                var memory_map_cell = create_cell_cell(current_cell_addr, "", cell_hex_val, "", is_uninitialized, array_id);
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
        var location_cell_table = location.find(" > table.memory-map-cell-table > tbody ");

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
                location_cell_table.find(" > tr[start-addr='" + toHexString(insert_addr) + "']").nextAll().has("td.dot-line").remove();
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
                    var first_child = current_row.children().first();
                    var new_cell_group_id = first_child.attr('group-id');

                    // Only cells with a group-id count as part of the actual variable, the rest are ignored
                    // If the old cell is uninitialized and the new value is the same, keep it
                    if(new_cell_group_id) {

                        var var_name = group_id_to_var_name[new_cell_group_id];
                        if(var_name && var_name[0] === '*') {
                            var old_group_id = $(existing_row.children()[i]).attr('group-id');
                            group_id_vals[old_group_id] = group_id_vals[new_cell_group_id];
                            first_child.attr('group-id', old_group_id);
                        }

                        var old_array_id = $(existing_row.children()[i]).attr('array-id');
                        if(old_array_id) {
                            first_child.attr('array-id', old_array_id);
                            group_id_to_array_id[first_child.attr('group-id')] = old_array_id;
                        }

                        // Save the last group address, if it exists
                        start_addr_to_group_id[parseInt(first_child.attr('addr'), 16)] = String(first_child.attr('group-id'));

                        $(existing_row.children()[i]).replaceWith(first_child);
                    } else {
                        $(current_row.children()[0]).remove();
                    }

                    i++;
                }

                // The cells have been extracted, but the <tr></tr> needs to be removed as well
                $(new_var_rows.children()[0]).remove();

            } else {
                // Simply append the row to insert_row
                current_row.insertAfter(insert_row);
                insert_row = insert_row.next();
            }
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
        var cell_table = location.find(" > table.memory-map-cell-table > tbody");
        var updated_label_table = document.createElement("tbody");

        var cell_table_rows = cell_table.children();
        var middle_rows_left = 0;
        var on_bottom_row = false;
        var on_last_row = false;
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
                        if(on_last_row) {
                            on_last_row = false;
                        } else {
                            on_bottom_row = true;
                        }
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
                        var is_uninitialized = current_cell.attr("uninitialized");
                        var array_id = current_cell.attr("array-id");

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
                                    cell_value = generate_label_value(group_id);;
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
                                    on_last_row = true;

                                } else if(c == 1 && colspan == 4) {
                                    // Draw the label
                                    cell_value = generate_label_value(group_id);;
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
                                    cell_value = generate_label_value(group_id);
                                    clarity_classes = "right-edge-clear-cell label-td";
                                }

                            }
                        }

                        td = create_label_cell(colspan, rowspan, group_id, cell_value, clarity_classes, is_uninitialized, array_id);

                        label_row.appendChild(td);
                        c += cells_on_row_in_group;
                    }

                }
            }

            updated_label_table.appendChild(label_row);
        }

        return updated_label_table;
    }

    function generate_label_value(group_id) {
        var label_value = group_id_vals[group_id];
        // Get all hex values of this group and convert appropriately
        // TODO: Remove calls to group_id_vals[group_id] and return the generated values
        var generated_label_value = '';
        var all_group_hex_values = $("table.memory-map-cell-table td[group-id='" + group_id + "'").map(function() {
            return $(this).html().replace(/0x/g, '');
        }).get().join('');

        var type = group_id_to_type[group_id];
        if(type.indexOf('*') > -1) {
            generated_label_value = '0x' + all_group_hex_values;

        } else if(type === 'char') {
            generated_label_value = hexToChar(all_group_hex_values);

        } else if(type.indexOf('unsigned') > -1) {
            generated_label_value = hexToUnsignedInt(all_group_hex_values);
        } else if(type === 'double' || type === 'float') {
            generated_label_value = hexToFloat(all_group_hex_values, type);
        } else {  // treat it like some kind of int
            generated_label_value = label_value;        // Since long can't be represented, this is more accurate
            //generated_label_value = hexToInt(all_group_hex_values);
        }

        //return label_value;
        return generated_label_value;
    }

    function regenerate_all_label_tables() {
        regenerate_label_table($("#data-memory-map"));
        regenerate_label_table($("#heap-memory-map"));

        var num_stack_tables = $("#stack-frame-tables").children().length;
        var stack_table_location = "";
        for(var i=0; i < num_stack_tables; i++) {
            regenerate_label_table($("#stack-frame-tables > div:eq(" + i + ")"));
        }
    }

    function regenerate_label_table(location) {
        // This function is only a helper for regenerate_all_label_tables()
        var updated_label_table = generate_label_table(location)
        var location_label_table = location.find(" > table.memory-map-label-table > tbody ");

        // Hide the new table if hex mode is on
        if(hex_mode_on) {
            $(updated_label_table).find("tr").addClass("hidden-row");
            location.find(" > table.memory-map-label-table").css("z-index", 0);
            location.find(" > table.memory-map-cell-table").css("z-index", 1000);

            if(location.find(" > table.memory-map-label-table thead tr").length > 1) {
                location.find(" > table.memory-map-label-table thead tr:nth-child(1)").css("visibility", "hidden");
            }
        }

        var label_table_hidden = location_label_table.is(":hidden");
        if(label_table_hidden) {
            $(updated_label_table).hide();
        }

        location_label_table.replaceWith(updated_label_table);
    }

    function get_var_location(func_location, func_name, start_addr, on_entry_point) {
        var exists_in_data = false;
        var exists_in_heap = false;
        var exists_in_stack = false;

        if(start_addr) {
            // Check if it already exists in the heap or data section
            start_addr = toHexString(start_addr);
            exists_in_data = $("div#data-memory-map td[addr='" + start_addr + "']").length > 0;
            exists_in_heap = $("div#heap-memory-map td[addr='" + start_addr + "']").length > 0;
            exists_in_stack = $("div#stack-frame-tables td[addr='" + start_addr + "']").length > 0;
        }

        if(exists_in_stack) {
            location = $("div#stack-frame-tables td[addr='" + start_addr + "']").parents("div.memory-map-table-wrapper");
            return location;
        }

        var location = null;
        if(func_location === "data" || exists_in_data) {
            location = $("#data-memory-map");
        } else if(func_location === "heap" || exists_in_heap) {
            location = $("#heap-memory-map");
        } else if(func_location === "stack") {
            var stack_frame_exists = $("#stack-frame-tables > div[stack-function='" + func_name + "']").length > 0;

            if(on_entry_point || !stack_frame_exists) {
                // Determine which stack level we are at, and increase it by 1
                var stack_level = 1;
                if(stack_frame_levels[func_name]) {
                    stack_frame_levels[func_name]++;
                    stack_level = stack_frame_levels[func_name];

                } else {
                    stack_frame_levels[func_name] = stack_level;
                }

                var calling_line = json_index > 0 ? debugger_data["steps"][json_index-1]["student_view_line"] : 0;
                var new_stack_frame = create_stack_frame_table(calling_line, func_name, stack_level);
                $("div#stack-frame-tables").prepend(new_stack_frame);
            }

            location = $("div#stack-frame-tables > div[stack-function='" + func_name + "']:first");
        }

        return location;
    }

    function get_var_group_id(changed_var) {
        var is_new = Boolean(changed_var["new"]);
        var var_name = changed_var["var_name"];
        var start_addr = parseInt(changed_var["addr"], 16);

        // Figure out the variable's group_id
        var group_id;
        if(start_addr_to_group_id[start_addr]) {
            // Find it in the tables
            group_id = start_addr_to_group_id[start_addr];
        } else {
            group_id = largest_group_id;
            largest_group_id++;
        }

        if(var_name_to_group_id[var_name] && is_new) {
            var_name_to_group_id[var_name] = group_id;
        }

        return group_id;
    }

    function get_var_array_id(group_id) {
        var existing_array_id = group_id_to_array_id[group_id];
        if(existing_array_id) {
            return existing_array_id;

        } else {
            var array_id = largest_array_id;
            largest_array_id++;

            return array_id;
        }
    }


    function create_stack_frame_table(stack_frame_number, stack_function, stack_level) {
        var table_title = stack_function + (stack_frame_number > 0 ? ": " + stack_frame_number : "");

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

        var c_tr1_th1 = document.createElement("th");
        c_tr1_th1.colSpan = "4";
        c_tr1_th1.className = "heading-height";
        c_tr1_th1.appendChild(create_minimizer());
        $(c_tr1_th1).append(table_title);

        var c_tr1_th2 = document.createElement("th");
        c_tr1_th2.innerHTML = stack_level;
        c_tr1_th2.className = "heading-height";
        $(c_tr1_th2).css("text-align", "center");

        var c_tr1 = document.createElement("tr");
        c_tr1.style.visibility = (hex_mode_on ? "" : "hidden");
        c_tr1.appendChild(c_tr1_th1);
        c_tr1.appendChild(c_tr1_th2);

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
        cells_table.className = " table table-bordered memory-map-cell-table"; //table-no-border
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

        var l_tr1_th1 = document.createElement("th");
        l_tr1_th1.colSpan = "4";
        l_tr1_th1.className = "heading-height";
        l_tr1_th1.appendChild(create_minimizer());
        $(l_tr1_th1).append(table_title);

        var l_tr1_th2 = document.createElement("th");
        l_tr1_th2.innerHTML = stack_level;
        l_tr1_th2.className = "heading-height";
        $(l_tr1_th2).css("text-align", "center");


        var l_tr1 = document.createElement("tr");
        l_tr1.appendChild(l_tr1_th1);
        l_tr1.appendChild(l_tr1_th2);

        //---

        var l_tr2_th1 = document.createElement("th");
        l_tr2_th1.className = "address-heading heading-height";
        l_tr2_th1.innerHTML = "Address";

        var l_tr2_th2 = document.createElement("th");
        l_tr2_th2.className = "values-heading heading-height";
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

    function create_minimizer() {
        var minimizer = document.createElement("a");
        minimizer.href = "#";
        minimizer.className = "small-minimizer";

        var minimizer_span = document.createElement("span");
        minimizer_span.className = "minimizer-span";
        minimizer_span.innerHTML = "[-]";
        minimizer_span.addEventListener('click', stack_table_minimize_function);

        minimizer.appendChild(minimizer_span)

        return minimizer;
    }

    function create_cell_cell(cell_addr, group_id, cell_value, clarity_classes, is_uninitialized, array_id) {
        var memory_map_cell = document.createElement("td");
        memory_map_cell.className = "memory-map-cell ";// + clarity_classes;
        if(is_uninitialized) {
            memory_map_cell.className += " uninitialized";
            memory_map_cell.setAttribute("uninitialized", true);
        }

        memory_map_cell.setAttribute("addr", toHexString(cell_addr));

        if(cell_value && cell_value != "&nbsp;") {
            memory_map_cell.setAttribute("group-id", group_id);
            cell_value = toHexString(cell_value, 2);

            if(array_id) {
                memory_map_cell.setAttribute("array-id", array_id);
            }
        } else {
            memory_map_cell.className += " uninitialized";
            memory_map_cell.setAttribute("uninitialized", true);
        }

        memory_map_cell.innerHTML = cell_value;
        memory_map_cell.setAttribute("title", cell_value);

        return memory_map_cell;
    }

    function add_hover_highlight_to_cells() {
        $("div.memory-map-section td.memory-map-cell").each(function () {
            var this_group_id = $(this).attr('group-id');
            var this_array_id = $(this).attr('array-id');

            var array_group_id = array_id_to_group_id[this_array_id];
            if(array_group_id) {
                this_group_id = array_group_id;
            }

            if(this_group_id) {
                $(this).hover(
                    create_hover_highlight_function(this_group_id),
                    create_hover_unhighlight_function(this_group_id)
                );
            }
        });
    }

    function create_label_cell(colspan, rowspan, group_id, cell_value, clarity_classes, is_uninitialized, array_id) {
        var memory_map_cell = document.createElement("td");
        memory_map_cell.className = "memory-map-cell " + clarity_classes;
        if(is_uninitialized) {
            memory_map_cell.className += " uninitialized";
        }

        if(array_id) {
            memory_map_cell.setAttribute("array-id", array_id);
        }

        memory_map_cell.colSpan = colspan;
        memory_map_cell.rowSpan = rowspan;

        if(cell_value != "&nbsp;") {
            memory_map_cell.setAttribute("group-id", group_id);
        }
        memory_map_cell.innerHTML = cell_value;
        memory_map_cell.setAttribute("title", cell_value);

        var array_group_id = array_id_to_group_id[array_id];
        var start_addr = group_id_to_start_addr[group_id];
        if(start_addr) start_addr = toHexString(start_addr);
        var is_ptr = value_list[start_addr] && value_list[start_addr]["is_ptr"]; // Check if it is a pointer

        if(array_group_id && !is_ptr) {
            group_id = array_group_id;
        }

        if(group_id) {
            var group_start_addr = group_id_to_start_addr[group_id];
            memory_map_cell.setAttribute("group-start-addr", toHexString(group_start_addr));

            $(memory_map_cell).hover(
                create_hover_highlight_function(group_id),
                create_hover_unhighlight_function(group_id)
                );
        }

        return memory_map_cell;
    }

    function create_cell_base_row(start_addr){
        var hex_start_addr = toHexString(start_addr);
        var memory_map_row = document.createElement("tr");
        memory_map_row.className =  (hex_mode_on ? "" : "hidden-row ")
        memory_map_row.setAttribute("start-addr", hex_start_addr);

        var td = document.createElement("td");
        td.className = "memory-map-address";
        td.innerHTML = hex_start_addr;
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
        if(hex_mode_on) {
            $("table.memory-map-cell-table tbody > tr").removeClass("hidden-row");
            $("div#stack-frame-tables table.memory-map-cell-table thead tr:nth-child(1)").css("visibility", "visible");
            var cell_table_z = parseInt($("table.memory-map-cell-table").css("z-index"));
            $("table.memory-map-cell-table").css("z-index", cell_table_z == 1000 ? 0 : 1000);

            $("table.memory-map-label-table tbody > tr").addClass("hidden-row");
            $("div#stack-frame-tables table.memory-map-label-table thead tr:nth-child(1)").css("visibility", "hidden");
            var label_table_z = parseInt($("table.memory-map-label-table").css("z-index"));
            $("table.memory-map-label-table").css("z-index", label_table_z == 1000 ? 0 : 1000);

        } else {
            $("table.memory-map-cell-table tbody > tr").addClass("hidden-row");
            $("div#stack-frame-tables table.memory-map-cell-table thead tr:nth-child(1)").css("visibility", "hidden");
            var cell_table_z = parseInt($("table.memory-map-cell-table").css("z-index"));
            $("table.memory-map-cell-table").css("z-index", cell_table_z == 1000 ? 0 : 1000);

            $("table.memory-map-label-table tbody > tr").removeClass("hidden-row");
            $("div#stack-frame-tables table.memory-map-label-table thead tr:nth-child(1)").css("visibility", "visible");
            var label_table_z = parseInt($("table.memory-map-label-table").css("z-index"));
            $("table.memory-map-label-table").css("z-index", label_table_z == 1000 ? 0 : 1000);
        }
    }

    function create_minimize_function(div_id) {
        return function() {
            if($(this).html() == "[-]") {
                $(this).parents("div.memory-map-table-wrapper").find("a span.minimizer-span").html("[+]");
            } else {
                $(this).parents("div.memory-map-table-wrapper").find("a span.minimizer-span").html("[-]");
            }

            $("#" + div_id + " tbody").fadeToggle("fast");
        }
    }

    function stack_table_minimize_function() {
        if($(this).html() == "[-]") {
            $(this).parents("div.memory-map-table-wrapper").find("a span.minimizer-span").html("[+]");
        } else {
            $(this).parents("div.memory-map-table-wrapper").find("a span.minimizer-span").html("[-]");
        }

        $(this).parents("div.memory-map-table-wrapper").find("tbody").fadeToggle("fast");
        $(this).parents("div.memory-map-table-wrapper").find("thead > tr:nth-child(2)").fadeToggle("fast");
    }

    function is_dot_row(td) {
        return $(td).hasClass("dot-line");
    }

    function create_hover_highlight_function(group_id) {
        return function() {
            highlight_all_related(group_id, true);
        }
    }

    function create_hover_unhighlight_function(group_id) {
        return function() {
            highlight_all_related(group_id, false);
        }
    }

    function create_hover_highlight_function_code() {
        return function() {
            // Find the group that this variable belongs to, if any, and highlight all related elements
            var var_name = $(this).html();
            var group_id = var_name_to_group_id[var_name];

            if(group_id) {
                highlight_all_related(group_id, true);
            }
        }
    }

    function create_hover_unhighlight_function_code() {
        return function() {
            // Find the group that this variable belongs to, if any, and highlight all related elements
            var_name = $(this).html();
            var group_id = var_name_to_group_id[var_name];

            if(group_id) {
                highlight_all_related(group_id, false);
            }
        }
    }

    function highlight_all_related(group_id, add_class) {
        var elements_to_highlight = find_elements_to_highlight(group_id);
        var main_elements = elements_to_highlight["main"];
        var extra_elements = elements_to_highlight["extra"];

        var num_elements = main_elements.length;
        for(var i = 0; i < num_elements; i++) {
            if(add_class) {
                main_elements[i].addClass("highlight main-highlight");
            } else {
                main_elements[i].removeClass("highlight main-highlight");
            }
        }

        num_elements = extra_elements.length;
        for(var i = 0; i < num_elements; i++) {
            if(add_class) {
                extra_elements[i].addClass("highlight");
            } else {
                extra_elements[i].removeClass("highlight");
            }
        }
    }


    function find_elements_to_highlight(group_id) {
        // The first pair has to be distinguished so it can be applied a different style
        var elements_to_highlight = {}
        var main_elements_to_highlight = [];
        var extra_elements_to_highlight = [];

        var array_id = group_id_to_array_id[group_id];
        var hex_group_start_addr = toHexString(group_id_to_start_addr[group_id]);

        var array_group_id = array_id_to_group_id[array_id];
        var hex_array_start_addr = group_id_to_start_addr[array_group_id];
        if(hex_array_start_addr) {
            hex_array_start_addr = toHexString(hex_array_start_addr);
        }

        var name_table_start_addr = hex_array_start_addr ? hex_array_start_addr : hex_group_start_addr;
        var name_table_row = $("div.name-type-section tr[data-address='" + name_table_start_addr + "']");
        main_elements_to_highlight.push(name_table_row);

        var group = $("div.memory-map-section td[group-id='" + group_id + "']");
        main_elements_to_highlight.push(group);
        var group_by_addr_cells = $("div.memory-map-section td[addr='" + hex_group_start_addr + "']");
        main_elements_to_highlight.push(group_by_addr_cells);
        var group_by_addr_labels = $("div.memory-map-section td[group-start-addr='" + hex_group_start_addr + "']");
        main_elements_to_highlight.push(group_by_addr_labels);

        var array_group = $("div.memory-map-section td[array-id='" + array_id + "']");
        main_elements_to_highlight.push(array_group);

        // Uncomment when a way is figured out to separate variables (instead of highlighting all with the same name)
        //var var_name = group_id_to_var_name[group_id];
        /*var var_name = name_table_row.find("td.var-name").attr('title');
        var code_span = $("div.code-window-section span.cm-variable").filter(function() {
            return $(this).html() == var_name;
        });
        extra_elements_to_highlight.push(code_span);
        */

        // If it's a pointer, find all things down the chain of pointers and add them to the array
        // Loop until we reach a non-pointer
        var elem_info = value_list[hex_group_start_addr];
        while(elem_info && elem_info['is_ptr']) {
            var ptr_val = elem_info['value'];
            var ptr_size = elem_info['ptr_size'];

            // Get the cell it's pointing to
            var pointed_cell = $("table.memory-map-cell-table td[addr='" + ptr_val + "']:first");

            // Add all the following cells up to ptr_size
            if(pointed_cell.length > 0) {
                // Get all following cells
                var parent_wrapper = pointed_cell.parents("div.memory-map-table-wrapper");
                var all_cells = parent_wrapper.find(".memory-map-cell-table td.memory-map-cell, .memory-map-cell-table td.dot-line");
                var current_cell_ind = find_index(all_cells.toArray(), function(cell) {
                    return $(cell).attr("addr") == ptr_val;
                });

                var following_cells = all_cells.slice(current_cell_ind);

                // Truncate to maximum size first, then remove all cells before the first dot row
                var cells_to_highlight = following_cells.slice(0, ptr_size);
                var sliceIndex = find_index(cells_to_highlight, is_dot_row);
                if(sliceIndex >= 0) {
                    cells_to_highlight = cells_to_highlight.slice(0, sliceIndex);
                }

                extra_elements_to_highlight.push(cells_to_highlight);

                // Highlight the groups this pointer points to, if it does point to any
                cells_to_highlight = cells_to_highlight.toArray();
                for(var i = 0; i < cells_to_highlight.length; i++) {
                    var this_cell = $(cells_to_highlight[i]);
                    var extra_group_id = start_addr_to_group_id[parseInt(this_cell.attr("addr"), 16)];
                    if(extra_group_id) {
                        extra_elements_to_highlight.push($("div.memory-map-section td[group-id='"+extra_group_id+"']"));
                    }
                }
            }

            // Attempt to follow the pointer chain
            elem_info = value_list[ptr_val];

        }


        elements_to_highlight["main"] = main_elements_to_highlight;
        elements_to_highlight["extra"] = extra_elements_to_highlight;
        return elements_to_highlight;
    }

    function find_index(array, is_true) {
        for (var i = 0; i < array.length; i++) {
            if(is_true(array[i])) {
                return i;
            }
        }
        return -1;
    }

    function add_return_name_table(json_step) {
        //Add the new id to return_to_clr variable, so that it gets removed from the table on next step
        //Will always be on the stack
        var return_data;
        var table_name = json_step['function'];
        var cur_frame;
        cur_frame = $('#names-'+table_name);

        //Check if there's a current frame up for this:
        if(cur_frame.length == 0) {
        //If not, create a whole new name table - could be possible for a function with no vars that then returns
            $('#name-type-section').prepend('<span id="name-table-'+table_name+'"> <h4>'+table_name+'</h4> <table id="names-' +table_name+
            '" class="table table-bordered" style="width: 100%; float:left;">'+
            '<thead>'+
                '<tr>'+
                '<th width="50%">Name</th>' +
                '<th width="50%">Type</th>' +
                '</tr>' +
            '</thead>' +
            '<tbody id="name-body-'+table_name+'">' +
            '</tbody>' +
            '</table></span>');
        }

        if(json_step.hasOwnProperty('returned_fn_call')) {
            var returned_function = json_step['returned_fn_call'];
            most_recently_returned = returned_function + '-' + stack_frame_levels[returned_function];
        }

        if(json_step.hasOwnProperty('return')) {
            return_val = json_step["return"];
            return_data = 'Return <'+return_val+'>';
        }
        else {
            //If this is the first time we're seeing this JSON step, the last value returned is stored in return_val and added to the JSON step
            if(!json_step.hasOwnProperty('return_val')) {
                json_step["return_val"] = return_val;
            }
            return_data = json_step["returned_fn_call"]+' <'+json_step['return_val']+'>';
        }

        return_to_clr = '#'+table_name+'-return';

        // Check if there's a current frame up for this:
        var stack_frame_level = stack_frame_level = stack_frame_levels[json_step['function']];
        if (!stack_frame_level){
            stack_frame_level = 1;
        }

        //Lookup this table's contents in our name table list
        var stack_func = name_table_vars[table_name+'-'+stack_frame_level]
        var stack_frame = stack_func[stack_func.length -1]
        // if (stack_frame){
        //     for (int i = 0; i<stack_frame.length; i++) {
        //         //Add a row to the existing name table
        //         $('#name-body-'+table_name).append('<tr id="'+table_name+'-'+  '"> <td colspan="2">' + return_data + '</td>' +
        //         '</tr>');
        //     }
        // }

        //Add a row to the existing name table
        $('#name-body-'+table_name).append('<tr id="'+table_name+'-return"> <td colspan="2">' + return_data + '</td>' +
        '</tr>');
    }

    function add_to_val_list(json_step) {
    //value_list will contain all variables currently allocated, will look like: { "0x123": { value": ["xyz", "mzy" ...], "is_ptr": "T/F" } }

        //Loop through all var changes in the step
        for(var i=0; i<json_step['changed_vars'].length; i++) {
            add_one_var_to_val_list(json_step['changed_vars'][i]);
        }
    }

    function add_one_var_to_val_list(changed_var) {
        var val_address = changed_var["addr"];
        var ptr_size = null;
        if(changed_var["new"]) {

            var val_as_obj = false;
            //Recurse through and add any of the val_lists value objects to the val_list
            for(var i = 0; i < changed_var["value"].length; i++) {
                val_object = changed_var["value"][i];
                if(val_object["value"] !== undefined){
                    val_as_obj = true;
                    add_value_array_to_val_list(val_object);
                }
            }

            //Only add the top level thing to the list if it doesn't contain an array as its value,
            //otherwise we'll have duplicate addresses
            if (val_as_obj == false) {
                var is_ptr_val = false;
                if(changed_var['is_ptr']) {
                    is_ptr_val = true;
                    ptr_size = changed_var['ptr_size'];
                }
                new_value = {
                    "value": changed_var["value"],
                    "hex_value": changed_var["hex_value"],
                    "history": [changed_var["value"]],
                    "is_ptr": is_ptr_val,
                    "ptr_size": ptr_size
                };
                value_list[val_address] = new_value;
            }
        }

        //Case where variable is not new, was on the heap and got freed - push "#Freed#" onto the list as a marker that it's been freed
        else if((changed_var['location']) == "Heap" && (changed_var.hasOwnProperty('free'))) {
            value_list[val_address]["history"].push("#Freed#");
        }

        //If the variable is not new and not freed, just push the new value onto its history array and update its current value
        else if(val_address in value_list) {
            value_list[val_address]["history"].push(changed_var["value"]);
            value_list[val_address]["value"] = changed_var["value"];
            value_list[val_address]["hex_value"] = changed_var["hex_value"];
        }
    }

    //Only executed on things that are part of an array of values, because they won't be "new"
    function add_value_array_to_val_list(value_var) {
        var val_address = value_var["addr"];
        var ptr_size = null;
        if(val_address in value_list) {
            value_list[val_address]["history"].push(value_var["value"]);
            value_list[val_address]["value"] = value_var["value"];
            value_list[val_address]["hex_value"] = value_var["hex_value"];
        }
        else {
            var is_ptr_val = false;
            if(value_var['is_ptr']) {
                is_ptr_val = true;
                ptr_size = value_var['ptr_size'];
            }
            new_value = {
                "value": value_var["value"],
                "hex_value": value_var["hex_value"],
                "history": [value_var["value"]],
                "is_ptr": is_ptr_val,
                "ptr_size": ptr_size
            };
            value_list[val_address] = new_value;
            //Recurse through and add any of the val_lists value objects to the val_list
            for(val_object in value_var["value"]) {
                if(val_object["value"] !== undefined){
                    add_value_array_to_val_list(val_object)
                }
            }
        }
    }

    function add_to_std_out(json_step) {
        //cur_stdout contains the full current stdout string that's been stepped to: will append to this and refresh the stdout window
        cur_stdout = cur_stdout.concat(json_step["std_out"]);
        $("#std-out-textbox").html(cur_stdout);
    }

    //Checks if we just returned from a function and then clicked prev, if so, just remove the return value from the function's
    //name_table_vars array
    function check_rm_return_nametable(json_step){
        if (json_step.hasOwnProperty('return')) {
            // Check if there's a current frame up for this:
            var stack_frame_level = stack_frame_level = stack_frame_levels[json_step['function']];
            if (!stack_frame_level){
                stack_frame_level = 1;
            }

            current_func = name_table_vars[json_step['function']+'-'+stack_frame_level];
            current_frame = current_func[current_func.length-1];
            if ((current_frame[current_frame.length-1]) && (current_frame[current_frame.length -1][0] === "return")){
                //Pop the last element of current_frame
                current_frame.pop();

                //If the current frame has no more in it, remove it from the dictionary
                if (current_frame.length == 0){
                    var index = current_func.indexOf(current_frame);
                    current_func.splice(index, 1);
                }
            }

        }
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
                        // Ignore heap variables because they don't have a name table
                        continue;
                    }
                    else {
                        table_name = 'data';
                    }

                    var to_remove = json_step['changed_vars'][i]['var_name'].toString();
                    $('#name-body-'+table_name+':first tr[id='+to_remove+']').remove();

                    // Check if there's a current frame up for this:
                    var stack_frame_level = stack_frame_level = stack_frame_levels[json_step['function']];
                    if (!stack_frame_level){
                        stack_frame_level = 1;
                    }

                    current_func = name_table_vars[json_step['function']+'-'+stack_frame_level];
                    current_frame = current_func[current_func.length-1];
                    //Find and remove the item from the current frame
                    item_removing = [to_remove, json_step['changed_vars'][i]['type']];
                    index = current_frame.indexOf(item_removing);
                    current_frame.splice(index, 1);

                    //If the current frame has no more in it, remove it from the dictionary
                    if (current_frame.length == 0){
                        var index = current_func.indexOf(current_frame);
                        current_func.splice(index, 1);
                    }


                    //Check if the table is now empty from this removal, remove if so
                    table_id = '#names-'+table_name;
                    check_rm_empty_table(table_id);
                }
            }
        }
        //Do collapsing/expanding of tables here, make sure the table of the last var change is expanded
    }

    function reset_memory_tables() {
        group_id_vals = {};
        group_id_to_type = {};
        group_id_to_start_addr = {};
        start_addr_to_group_id = {};
        var_name_to_group_id = {};
        group_id_to_var_name = {};
        group_id_to_array_id = {};
        stack_frame_levels = {};
        free_list = {};

        largest_group_id = 1; // Not 0 because it would fail a check for adding the highlight functions
        largest_array_id = 1; // Not 0, same reason as above

        $("#data-memory-map tbody").empty();
        $("#heap-memory-map tbody").empty();
        $("#stack-frame-tables").empty();
    }

    function remove_from_memory_table() {
        // Nuke all memory tables and rebuild them up to the previous step
        reset_memory_tables();

        // Re-add the global variables just to the memory map; the name table and value list are handled separately
        globals = debugger_data["global_vars"];
        global_amt = globals.length;
        for(var i = 0; i < global_amt; i++) {
            var var_group_id = get_var_group_id(globals[i]);
            add_one_var_to_memory_table(globals[i], "", var_group_id);
        }

        var last_step = json_index-1;
        json_index = 0;
        for(var i=0; i <= last_step; i++) {
            var json_step = debugger_data["steps"][i];

            if(json_step['on_entry_point']) {
                // Create the empty table even before any variables get assigned
                get_var_location('stack', json_step['function'], undefined, true);
            }

            if(json_step.hasOwnProperty('returned_fn_call')) {
                // Remove the previous stack frame of this function
                remove_stack_table(json_step['returned_fn_call']);
            }

            if(json_step.hasOwnProperty('changed_vars')) {
                add_to_memory_table_only(json_step);
            }
            json_index++;
        }

        // After we've inserted all the variables, we have to generate the corresponding label tables
        regenerate_all_label_tables();
    }

    function remove_stack_table(stack_function) {
        var stack_table = $("#stack-frame-tables div[stack-function='" + stack_function + "']:first");
        var group_ids = stack_table.find("table.memory-map-label-table td.memory-map-cell").map(function() {
            return $(this).attr("group-id");
        }).get();

        // Remove all the relevant elements in the maps
        var len = group_ids.length;
        for(var i = 0; i < len; i++) {
            var group_id = group_ids[i];
            var start_addr = group_id_to_start_addr[group_ids];
            var var_name = group_id_to_var_name[group_id];

            delete start_addr_to_group_id[start_addr];
            delete group_id_to_start_addr[group_id];

            delete var_name_to_group_id[var_name];
            delete group_id_to_var_name[group_id];
        }

        stack_frame_levels[stack_function]--;
        if(stack_frame_levels[stack_function] === 0) {
            delete stack_frame_levels[stack_function];
        }

        stack_table.remove();
    }

    function remove_from_val_list(json_step) {
    //value_list will contain all variables currently allocated, will look like: { "0x123": { value": "xyz", "is_ptr": "T/F" } }

        //Loop through all var changes in the step
        for(var i=0; i<json_step['changed_vars'].length; i++) {

            var val_address = toHexString(json_step['changed_vars'][i]["addr"]);

            if(json_step['changed_vars'][i]["new"]) {

                had_more_vals = false

                //Recurse through and delete any additional things in the val list that are in its value array
                for(var j=0; j < json_step['changed_vars'][i]["value"].length; j++) {
                    val_obj = json_step['changed_vars'][i]["value"][j];
                    if(val_obj["value"] !== undefined) {
                        had_more_vals = true;
                        remove_inner_val_from_val_list(val_obj);
                    }
                }
                //Pop it here it if didnt have any other values in it, otherwise leave it
                //since we'll delete it the for loop above
                value_list[val_address]["history"].pop();
                var history = value_list[val_address]["history"];

                if (had_more_vals == false) {
                    //If the val no longer exists, just set its value to null but keep in the list
                    if (history.length == 0) {
                        value_list[val_address]["value"] = null;
                    }
                    else {
                        value_list[val_address]["value"] = history[history.length-1];
                    }

                    //delete value_list[val_address];
                }
            }

            //Otherwise just pop the last value off the list
            else {
                value_list[val_address]["history"].pop();
                var history = value_list[val_address]["history"];
                value_list[val_address]["value"] = history[history.length-1];
            }
        }
    }

    function remove_inner_val_from_val_list(inner_val){
        if(inner_val["new"]) {
            for (var i=0; i < inner_val["value"].length; i++) {
                cur_val_obj = inner_val["value"][i]["value"];
                if (cur_val_obj !== undefined) {
                    remove_inner_val_from_val_list(cur_val_obj);
                }
            }

            var val_address = toHexString(inner_val["addr"]);
            value_list[val_address]["history"].pop();
            var history = value_list[val_address]["history"];

            //If the val no longer exists, just set its value to null but keep in the list
            if (history.length == 0) {
                value_list[val_address]["value"] = null;
            }
            else {
                value_list[val_address]["value"] = history[history.length-1];
            }
            // delete value_list[val_address];
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

    /**
     * Update dictionary initPostParams with additional parameters
     * that will be used to create a visualizer.
     */
    function getExecutionTraceParams(initPostParams) {
        initPostParams.add_params = JSON.stringify({test_case : initPostParams.test_case});
    }
}

