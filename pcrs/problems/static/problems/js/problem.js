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

