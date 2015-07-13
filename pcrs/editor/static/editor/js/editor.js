$(document).ready(function() {
    var code_wrapper = $('.code-mirror-wrapper')[0];
    var code_wrapper_id = code_wrapper.id;

    $(code_wrapper).children('#grade-code').hide();

    check_language(code_wrapper_id);
    if (language == "c") {
        myCodeMirrors[code_wrapper_id] = history_code_mirror(language, 'text/x-csrc', $(code_wrapper).find("#div_id_code_box"), '', false);

        preventDeleteLastLine(code_wrapper_id)
    }

    $(code_wrapper).find('#submit-id-trace').click(function(event) {
        event.preventDefault();
        var div_id = $(this).parents('.code-mirror-wrapper')[0].id;

        var user_code = myCodeMirrors[div_id].getValue();

        if (user_code == '') {
            alert('There is no code to submit.');
        } else{
            setTimeout(function() {
                start_editor_visualizer(user_code, code_wrapper_id);
            });
        }
    });
});

function start_editor_visualizer(user_code, code_wrapper_id) {
    newOrOld = "new"; // Will be removed later on

    var postParams = { 'language' : language, 'user_code' : user_code };

    executeGenericVisualizer("gen_execution_trace_params", postParams, newOrOld);

    visualizerDetailsTarget = '/new-visualizer-details-editor';
    $.post(root + '/editor' + visualizerDetailsTarget,
            postParams,
            function(data) {
                executeGenericVisualizer("create_visualizer", data, user_code, newOrOld);
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

