/**
 * global variables
*/
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

