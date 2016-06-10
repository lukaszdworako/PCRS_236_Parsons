/**
 * global variables
*/
var testcases = null;
var error_msg = null;
var myCodeMirrors = {};
var cmh_list = {};
var debugger_id = "";
var visPostComplete = true;
//root is a global variable from base.html


function bindDebugButton(buttonId) {
    /**
    * For coding problems bing a given New "Debug" button to start code visualizer
    */

    $('#'+buttonId).bind('click', function() {
        var testcaseCode = $('#tcase_' + buttonId).find(".expression_div").text();
        setTimeout(function(){
            $('#waitingModal').modal('show');
            prepareVisualizer("debug", testcaseCode, buttonId)
            $('#waitingModal').modal('hide');
        }, 250);
    });
}

function prepareVisualizer(option, testcaseCode, buttonId) {
    /**
     * Prepare Coding problem visualizer
     */

    var key = buttonId.split("_")[0];
    var problemId = key.split("-")[1];
    var newCode = myCodeMirrors[key].getValue() + "\n";

    if (language == 'python') {
        newCode += testcaseCode;
    } else if (language == 'c' || language == 'java') {
        newCode = addHashkey(myCodeMirrors[key], problemId);
    }
    getVisualizerComponents(newCode, testcaseCode, problemId);
}


function getVisualizerComponents(newCode, testcaseCode, problemId) {
    /**
     * Get Components for coding problem visualization
     */

    var postParams = { language : language, user_script : newCode, test_case: testcaseCode, problemId: problemId};
    executeGenericVisualizer("gen_execution_trace_params", postParams, '');
    visPostComplete = false;

    $.post(root + '/problems/' + language + '/visualizer-details',
            postParams,
            function(data) {
                executeGenericVisualizer("create_visualizer", data, newCode);
                visPostComplete = true;
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}


function getHistory(div_id){
    /**
     * Get submission history for a coding problem based on 'div_id' of the problem
     */

    var postParams = { csrftoken: csrftoken };
    var problem_path = "";

    // Empty the accordion, in case any manual insertions were performed.

    var language = check_language(div_id);
    problem_path = root + '/problems/' + language + '/' + div_id.split("-")[1]+'/history';
    $.post(problem_path,
        postParams,
        function(data){
            window[div_id+'_history_init'] = 1;
            show_history(data, div_id);
        },
        'json')
        .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}


function add_history_entry(data, div_id, flag){
    /**
     * Add "data" to the history inside the given "div_id"
     * "flag" 0 appends anf "flag" 1 prepends
     */

    // Exit if the history window has fbeen requested by the user
    if (!window[div_id+'_history_init']) {
        return;
    }

    var sub_time = new Date(data['sub_time']);
    var panel_class = "pcrs-panel-default";
    var star_text = "";

    sub_time = create_timestamp(sub_time);

    if (data['past_dead_line']){
        panel_class = "pcrs-panel-warning";
        sub_time = sub_time + " Submitted after the deadline";
    }

    if (data['best'] && !data['past_dead_line']){
        panel_class = "pcrs-panel-star";
        star_text = '<icon style="font-size:1.2em" class="star-icon" title="Latest Best Submission"> </icon>';

        $('#'+div_id).find('#history_accordion').find(".star-icon").remove();
        $('#'+div_id).find('#history_accordion').find(".pcrs-panel-star")
            .addClass("pcrs-panel-default").removeClass("pcrs-panel-star");
    }

    var entry = $('<div/>',{class:panel_class});
    var header1 = $('<div/>',{class:"pcrs-panel-heading"});
    var header2 = $('<h4/>', {class:"pcrs-panel-title"});
    var header4 = $('<td/>', {html:"<span class='pull-right'> " + star_text + " "
                                      + "<sup class='h_score'>" + data['score'] + "</sup>"
                                      + " / "
                                      + "<sub class='h_score'>" + data['out_of'] + "</sub>"
                                      + "</span>"});

    var header3 = $('<a/>', {'data-toggle':"collapse",
                             'data-parent':"#history_accordion",
                              href:"#collapse_"+data['sub_pk'],
                              onclick:"delay_refresh_cm('history_mirror_"
                                + data['problem_pk']
                                + "_"
                                + data['sub_pk']
                                + "')",
                              html:sub_time + header4.html()});

    var cont1 = $('<div/>', {class:"pcrs-panel-collapse collapse",
                                  id:"collapse_" + data['sub_pk']});

    var cont2 = $('<div/>', {id:"history_mirror_"
                                      + data['problem_pk']
                                      + "_"
                                      + data['sub_pk'],
                                  html:data['submission']});
    cont2.html = cont2.text(data['submission']).html();

    var cont3 = $('<ul/>', {class:"pcrs-list-group"});


    for (var num = 0; num < data['tests'].length; num++){

        var lc = "";
        var ic = "";
        var test_msg = "";
        if (data['tests'][num]['passed']){
            lc = "testcase-success";
            ic = "<icon class='ok-icon'> </icon>";
        }
        else{
            lc = "testcase-fail";
            ic = "<icon class='remove-icon'> </icon>";
        }

        if (data['tests'][num]['visible']){
            test_msg = " " + data['tests'][num]['input'] + " -> " + data['tests'][num]['output'];
        }
        else{
            if (data['tests'][num]['description'] == ""){
                test_msg = " Hidden Test";
            }
            else{
                test_msg = " " + data['tests'][num]['description'];
            }
        }

        var cont4 = $('<li/>', {class:lc,
                                   html:ic + test_msg});
        cont3.append(cont4);
    }


    header2.append(header3);
    header1.append(header2);

    entry.append(header1);
    cont1.append(cont2);
    cont1.append(cont3);
    entry.append(cont1);

    if (flag == 0){
        $('#'+div_id).find('#history_accordion').append(entry);
    }
    else{
        $('#'+div_id).find('#history_accordion').prepend(entry);
    }

    var language = check_language(div_id);
    if (language == "python"){
        create_to_code_mirror("python", 3, "history_mirror_"
                                                + data['problem_pk']
                                                + "_"
                                                + data['sub_pk']);
    }
    else{
        create_to_code_mirror(language, false, "history_mirror_"
                                                + data['problem_pk']
                                                + "_"
                                                + data['sub_pk']);
    }
}


function show_history(data, div_id){
    /**
     * Given all the previous submissions "data" add it to the "div_id"
     */

    for (var x = 0; x < data.length; x++){
        add_history_entry(data[x], div_id, 0);
    }
}

/**
 * Generate a Hashkey based on the problem_id to identify
 * where the student code starts and ends.
 */
function addHashkey(codeMirror, problemId) {
    var line_count = codeMirror.lineCount();
    var hash_code = CryptoJS.SHA1(problemId);
    var code = "";
    var wrapClass;
    var i;
    var inside_student_code = false;

    for (i = 0; i < line_count; i++){
        wrapClass = codeMirror.lineInfo(i).wrapClass;

        if (wrapClass == 'CodeMirror-activeline-background') {
            if(inside_student_code) {
                code += hash_code + '\n';
                inside_student_code = false;
            }

        } else {
            if(!inside_student_code) {
                code += hash_code + '\n';
                inside_student_code = true;
            }
        }

        code += codeMirror.getLine(i);
        code += '\n';
    }
    code += hash_code;
    return code;
}

function handleCompileMessages(div_id, testcases) {
    /**
     * Handle C error and warning
     * messages - divs with different
     * colors and font style
     */
    // Handle C warnings and exceptions
    $('#' + div_id).find('#c_warning').remove();
    $('#' + div_id).find('#c_error').remove();

    // Find testcase with warning/error
    var bad_testcase = null;
    for (var i = 0; i < testcases.length; i++) {
        if ("exception_type" in testcases[i]) {
            bad_testcase = testcases[i];
            break;
        }
    }

    var dont_visualize = false;

    if (bad_testcase != null) {
        var class_type;
        if (bad_testcase.exception_type == "warning") {
            class_type = 'alert alert-warning';
        } else if (bad_testcase.exception_type == "error") {
            class_type = 'alert alert-danger';
            dont_visualize = true;
        }

        var bad_testcase_message = "";
        if ("exception" in bad_testcase) {
            bad_testcase_message = bad_testcase.exception;
        } else if ("runtime_error" in bad_testcase) {
            bad_testcase_message = "Runtime error for input '" +
                bad_testcase.test_input +
                "':<br/>" + bad_testcase.runtime_error;
        }

        $('#'+div_id)
            .find('#alert')
            .after('<div id="c_warning" class="' +
                class_type + '" style="font-weight: bold">' +
                bad_testcase_message + '</div>');
    }

    // The grade table clutters up the interface when we have compile errors
    if (dont_visualize) {
        $('#gradeMatrix').hide();
    } else {
        $('#gradeMatrix').show();
    }

    return dont_visualize;
}

function prepareSqlGradingTableLegacy(div_id, best, past_dead_line, sub_pk, max_score, is_editor) {
    /**
     * Display the results of the SQL and RA test cases.
     * "div_id" the main div of the problem
     * "best" bool which indicates if this is the best submission so far
     * "past_dead_line" bool which indicates of the submission is on time
     * "sub_pk" submission id
     * "max_score" maximum score for this problem
     * "is_editor" is True if we are preparing results for the editor view
     */

    var score = 0;
    var tests = [];
    var table_location = $('#'+div_id).find('#table_location');
    table_location.empty();

    //error ra
    if (error_msg != null){
        table_location.append("<div class='red-alert'>"+error_msg+"</div>");

        var test = {'visible': false,
                    'input': null,
                    'output': null,
                    'passed': false,
                    'description': error_msg};
        tests.push(test);
        error_msg = null;
    }
    else{
        for (var i = 0; i < testcases.length; i++) {
            var current_testcase = testcases[i];
            var main_table = $('<table/>', {id:"gradeMatrix"+current_testcase['testcase'],
                                            class:"pcrs-table"});

            var expected_td = $('<td/>', {class:"table-left"}).append("Expected");
            if (!is_editor) {
                var actual_td = $('<td/>', {class:"table-right"}).append("Actual");
            }
            else {
                var actual_td = $('<td/>', {class:"table-right"});
            }

            var left_wrapper = $('<div/>', {class:"sql_table_control"});
            var right_wrapper;
            if (current_testcase['visible'])
                right_wrapper = $('<div/>',{class:"sql_table_control"});
            else {
                right_wrapper = $('<div/>',{class:"sql_table_control_full"});
            }

            var expected_table = $('<table/>', {class:"pcrs-table"});
            var actual_table = $('<table/>', {class:"pcrs-table"});

            var expected_entry = $('<tr/>', {class:"pcrs-table-head-row"});
            var actual_entry = $('<tr/>', {class:"pcrs-table-head-row"});

            if (!is_editor) {
                if (current_testcase['passed']){
                    table_location.append("<div class='green-alert'><icon class='ok-icon'>" +
                                          "</icon><span> Test Case Passed</span></div>");
                    score++;
                }
                else {
                    table_location.append("<div class='red-alert'><icon class='remove-icon'>" +
                                          "</icon><span> Test Case Failed</span></div>");
                }
            }

            if (current_testcase['error'] != null){
                table_location.append("<div class='red-alert'>"+current_testcase['error']+"</div>");
            }
            else {
                if (current_testcase['visible'] && !is_editor){
                    for (var header = 0; header < current_testcase['expected_attrs'].length; header++){
                        expected_entry.append("<td><b>"+ current_testcase['expected_attrs'][header] +"</b></td>");
                    }
                }
                else if (!is_editor) {
                    table_location.append("<div class='blue-alert'>" +
                                      "</icon><span> Expected Result is Hidden </span></div>");
                }

                for (var header = 0; header < current_testcase['actual_attrs'].length; header++){
                    actual_entry.append("<td><b>"+ current_testcase['actual_attrs'][header] +"</b></td>");
                }

                expected_table.append(expected_entry);
                actual_table.append(actual_entry);
                expected_table.removeClass("pcrs-table-head-row").addClass("pcrs-table-row");
                actual_table.removeClass("pcrs-table-head-row").addClass("pcrs-table-row");

                if (current_testcase['visible'] && !is_editor){
                    for (var entry = 0; entry < current_testcase['expected'].length; entry++){
                        var entry_class = 'pcrs-table-row';
                        var test_entry = current_testcase['expected'][entry];
                        if (test_entry['missing']){
                            entry_class = "pcrs-table-row-missing";
                        }
                        var expected_entry = $('<tr/>', {class:entry_class});
                        for (var header = 0; header < current_testcase['expected_attrs'].length; header++){
                            expected_entry.append("<td>" +
                                                 test_entry[current_testcase['expected_attrs'][header]] +
                                                 "</td>");
                        }
                        expected_table.append(expected_entry);
                    }
                }

                for (var entry = 0; entry < current_testcase['actual'].length; entry++){
                    var entry_class = 'pcrs-table-row';
                    var test_entry = current_testcase['actual'][entry];
                    if (test_entry['extra']){
                        entry_class = 'pcrs-table-row-extra';
                    }
                    else if (test_entry['out_of_order']){
                        entry_class = 'pcrs-table-row-order';
                    }
                    var actual_entry = $('<tr/>', {class:entry_class});
                    for (var header = 0; header < current_testcase['actual_attrs'].length; header++){

                       actual_entry.append("<td>" +
                                           test_entry[current_testcase['actual_attrs'][header]] +
                                           "</td>");
                    }
                    actual_table.append(actual_entry);
                }

                if (current_testcase['visible'] && !is_editor){
                    left_wrapper.append(expected_table);
                    expected_td.append(left_wrapper);
                    main_table.append(expected_td);
                }

                right_wrapper.append(actual_table);
                actual_td.append(right_wrapper);
                main_table.append(actual_td);

                table_location.append(main_table);
            }

	    var test = {'visible':current_testcase['visible'],
	                'input': null,
	                'output': null,
	                'passed': current_testcase['passed'],
	                'description': current_testcase['test_desc']};

	    tests.push(test);
        }
    }
    var data = {'sub_time':new Date(),
            'submission':myCodeMirrors[div_id].getValue(),
            'score':score,
            'best':best,
            'past_dead_line':past_dead_line,
            'problem_pk':div_id.split("-")[1],
            'sub_pk':sub_pk,
            'out_of':max_score,
            'tests': tests};
    if (best && !data['past_dead_line']){
        update_marks(div_id, score, max_score);
    }

    var flag = ($('#'+div_id).find('#history_accordion').children().length != 0);
    add_history_entry(data, div_id, flag);
}


function prepareGradingTableLegacy(div_id, best, past_dead_line, sub_pk, max_score) {
    /**
     * Display the results of the python-like (C, Java) test cases.
     * "div_id" the main div of the problem
     * "best" bool which indicates if this is the best submission so far
     * "past_dead_line" bool which indicates of the submission is on time
     * "sub_pk" submission id
     * "max_score" maximum score for this problem
     */

    var gradingTable = $("#"+div_id).find("#gradeMatrix");
    gradingTable.find(".red-alert").remove();
    var score = 0;
    var tests = [];

    if (error_msg != null){
        var tableRow = $(gradingTable).find('.pcrs-table-row');
        while (tableRow.length) {
            tableRow.remove();
            tableRow = $(gradingTable).find('.pcrs-table-row');
        }
        gradingTable.append("<th class='red-alert' colspan='12' style='width:100%;'>"+error_msg+"</th>");
        error_msg = null;
    }
    else{
	    for (var i = 0; i < testcases.length; i++) {
	        var current_testcase = testcases[i];
	        var description = current_testcase.test_desc;
	        var passed = current_testcase.passed_test;
	        var testcaseInput = current_testcase.test_input;
                var testcaseOutput = null;
                if (current_testcase.expected_output) {
	            var testcaseOutput = create_output(current_testcase.expected_output);
                }
            var debug = current_testcase.debug;

            var result;
            if (language == 'python') {
	            result = create_output(current_testcase.test_val);
            } else {
                result = current_testcase.test_val;
            }

	        var cleaner = $(gradingTable).find('#tcase_'+div_id+'_'+ i);

	        if (description == ""){
	            description = "No Description Provided"
	        }

	        if (cleaner){
	            cleaner.remove();
	        }

	        var newRow = $('<tr class="pcrs-table-row" id="tcase_'+div_id+'_'+i + '"></tr>');
	        gradingTable.append(newRow);

	        if ("exception" in current_testcase){

	            newRow.append('<th class="red-alert" colspan="12" style="width:100%;">' +
	                          current_testcase.exception + '</th>');
	        }
            else {
                if (language == 'java') {
                    newRow.append('<td>' + description + '</td>');
                    newRow.append('<td>' +
                       '<div>' +
                       '<span class="stringObj">' +
                       current_testcase.test_val +
                       '</span>' +
                       '</div></td>');
                } else {
                    newRow.append('<td class="description">' + description + '</td>');

                    if (testcaseInput != null) {
                        newRow.append('<td class="expression"><div class="expression_div">' +
                                testcaseInput + '</div></td>');
                    } else {
                        newRow.append('<td class="expression">' +
                                "Hidden Test" +'</td>');
                    }
                    newRow.append('<td class="expected"><div class="ptd">' +
                        '<div id="exp_test_val'+i+'" class="ExecutionVisualizer">' +
                        '</div></div></td>');
                    newRow.append('<td class="result"><div class="ptd">' +
                        '<div id="current_testcase' + i + '" class="ExecutionVisualizer">' +
                        '</div></div></td>');
                }

                if (language == 'python') {
                    renderData_ignoreID(current_testcase.test_val, $('#current_testcase'+i));
                } else if (language == 'c') {
                    $('#current_testcase'+i).append('<span class="stringObj">' + current_testcase.test_val + '</span>')
                }

                if (language != 'java') {
                    document.getElementById("current_testcase"+i).removeAttribute('id');
                }

                if (language == 'python') {
                    renderData_ignoreID(current_testcase.expected_output, $('#exp_test_val'+i));
                } else if (language == 'c') {
                    $('#exp_test_val'+i).append('<span class="stringObj">' + current_testcase.expected_output + '</span>')
                }

                if (language != 'java') {
                    document.getElementById("exp_test_val"+i).removeAttribute('id');
                }

                newRow.append('<td class="passed"></td>');

                var pass_status = "";

                if (passed){
                    var smFace = happyFace;
                    score += 1;
                    pass_status = "passed";
                }
                else{
                    var smFace = sadFace;
                    pass_status = "failed";
                }

                $("#"+div_id).find('#tcase_'+div_id+'_'+ i + ' td.passed').html(smFace.clone());

                if (debug){
                    newRow.append('<td class="debug"><button id="'
                            + div_id +"_"+i + '" class="debugBtn" type="button"' +
                            ' data-toggle="modal" data-target="#visualizerModal">Trace</button></td>');
                    bindDebugButton(div_id+"_"+i);
                }
                else{
                    newRow.append('<td class="debug">-</td>')
                }
                newRow.append('<a class="at" href="">This testcase has '+ pass_status +'. Expected: '+
                        testcaseOutput+'. Result: '+result+'</a>');
            }
	        var test = {'visible':testcaseInput != null,
	                    'input': testcaseInput,
	                    'output': testcaseOutput,
	                    'passed': passed,
	                    'description': description};

	        tests.push(test);
	    }
    }
    var data = {'sub_time':new Date(),
            // Now that we have multiple code mirrors, this should change a bit.
            //'submission':myCodeMirrors[div_id].getValue(), // FIXME
            'submission': '',
            'score':score,
            'best':best,
            'past_dead_line':past_dead_line,
            'problem_pk':div_id.split("-")[1],
            'sub_pk':sub_pk,
            'out_of':max_score,
            'tests': tests};

    if (best && !data['past_dead_line']){
        update_marks(div_id, score, max_score);
    }
    var flag = ($('#'+div_id).find('#history_accordion').children().length != 0);
    add_history_entry(data, div_id, flag);
}


function create_timestamp(datetime){
    /**
     * Convert django "datetime" to PCRS style for history
     */

    var month_names = ["January","February","March","April","May","June","July",
                   "August","September","October","November","December"];

    var day = datetime.getDate();
    var month = month_names[datetime.getMonth()];
    var year = datetime.getFullYear();
    var hour = datetime.getHours();
    var minute = datetime.getMinutes();

    if (String(minute).length == 1){
        minute = "0" + minute
    }
    if (hour > 12){
        hour -= 12;
        cycle = "p.m.";
    }
    else{
        cycle = "a.m.";
    }

    var formated_datetime = month + " " + day + ", "+year + ", " + hour+":"+minute+" "+cycle
    return formated_datetime;
}

/**
 * Convert the given "input" in to a string representing the students python solution
 */
function create_output(input) {
    var brakets_o = {"list":"[","tuple":"(","dict":"{"};
    var brakets_c = {"list":"]","tuple":")","dict":"}"};

    if (input.length == 2) {
        return create_output(input[0])+":"+create_output(input[1]);
    } else if (input[0] == "list" || input[0] == "tuple" || input[0] == "dict") {
        var output = brakets_o[input[0]];
        for (var o_index = 2; o_index < input.length; o_index++){
            output += create_output(input[o_index]);
            if (o_index != input.length - 1){
                output += ", "
            }
        }
        output += brakets_c[input[0]];
        return output
    } else if (input[0] == "string") {
        return "'"+input[2]+"'";
    } else if(input[0] == "float") {
        if (String(input[2]).indexOf(".") > -1) {
            return input[2]
        } else {
            return input[2]+".0"
        }
    } else{
        return input[2]
    }
}

// FIXME rip this guy out! It is super smelly.
function check_language(container) {
    /**
     * Check the language of a problem
     * "container" is the id of the main_div
     */
    if (container.indexOf("c") > -1){
        language = 'c';
    }
    else if (container.indexOf("python") > -1){
        language = 'python';
    }
    else if (container.indexOf("java") > -1){
        language = 'java';
    }
    else if (container.indexOf("sql") > -1){
        language = 'sql';
    }
    else if (container.indexOf("ra") > -1){
        language = 'ra';
    }
    else{
        language = '';
    }
    return language;
}

function escapeRegExp(string) {
    /**
     * Escape Regex Expressions
     */
    return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function replaceAll(find, replace, string) {
    /**
     * Replace an specific
     * substring within a string
     */
  return string.replace(new RegExp(escapeRegExp(find), 'g'), replace);
}

$(document).ready(function() {
    var all_wrappers = $('.code-mirror-wrapper');

    for (var x = 0; x < all_wrappers.length; x++) {
        var wrapperDivId = all_wrappers[x].id;
        var wrapper = SubmissionWrapper.createWrapperFromDivId(wrapperDivId);
        wrapper.pageLoad();
    }

    $(window).bind("load", function() {
        $('.CodeMirror').each(function(i, el){
            el.CodeMirror.refresh();
        });
    });
});

