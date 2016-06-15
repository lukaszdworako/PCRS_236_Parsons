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

/**
 * Add "data" to the history inside the given "div_id"
 */
// FIXME Bite the proverbial bullet and start using mustache!
function add_history_entry(data, div_id) {
    var $accordion = $('#' + div_id).find('#history_accordion');

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

        $accordion.find(".star-icon").remove();
        $accordion.find(".pcrs-panel-star")
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

    if ($accordion.children().length == 0) {
        $accordion.append(entry);
    } else {
        $accordion.prepend(entry);
    }

    var historyMirrorId = "history_mirror_" +
        data['problem_pk'] + "_" + data['sub_pk'];
    // A bit of a hack for now - The only possibly version is "3" for Python
    // Soon, this will be polymorphized so we can check the class version instead
    // TODO replace this with a TabbedCodeMirror on PCRS-Java!!!
    var language_version = 3;
    create_to_code_mirror(language, language_version, historyMirrorId);
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

