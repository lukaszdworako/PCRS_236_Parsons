/**
 * global variables 
 * note: global variables language, problem_id are declared in problem-view.html 
*/

var testcases = null;
var code_problem_id = -1;

function changeView(mode) {

    if (mode == "edit-code") {
    $(".testcase").hide();
    $(".visualizer-options").hide();
    // ShowHide();
    }

    // display only current mode
    $('#' + mode).siblings().hide();
    $('#' + mode).show();

    // disable button leading to current mode
    $('.' + mode).siblings().removeAttr('disabled');
    $('.' + mode).attr('disabled','disabled');
}

function bindDebugButton(buttonId) {

    $('#'+ buttonId).bind('click', function() {
        var testcaseCode = $('#tcase_' + buttonId + ' td.testInputCell').html();
        setTimeout(function(){
            prepareVisualizer("debug", testcaseCode, buttonId)},250
        );
    });
}

function prepareVisualizer(option, data, buttonId) {

    key = buttonId.split("_")[0];
    var newCode = myCodeMirrors[key].getValue() + "\n";

    var addCode = (option == "viz") ? myCodeMirrors[key].getValue() : data;
    newCode += addCode;
    getVisualizerComponents(newCode);
}

function getVisualizerComponents(newCode) {

    var postParams = { language : 'python', user_script : newCode};
    executeGenericVisualizer("gen_execution_trace_params", postParams);
    $.post('/problems/code/visualizer-details',
            postParams,
            function(data) {
                executeGenericVisualizer("create_visualizer", data);
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function getTestcases(div_id) {

    var postParams = { csrftoken: csrftoken, submission: myCodeMirrors[div_id].getValue() };
    $.post('/problems/code/'+div_id.split("-")[1]+'/run',
            postParams,
            function(data) {
                console.log(data);
                testcases = data['results'][0];
                $("#"+div_id).find("#grade-code").show();

                var score = data['score'];
                var max_score = data['max_score'];

                var desider = score == max_score;
                $('#'+div_id).find('#alert')
                    .toggleClass("alert-danger", !desider);
                $('#'+div_id).find('#alert')
                    .toggleClass("alert-success", desider);
                $('#'+div_id).find('#alert')
                    .children('icon')
                    .toggleClass("glyphicon-remove", !desider);
                $('#'+div_id).find('#alert')
                    .children('icon')
                    .toggleClass("glyphicon-ok", desider);
                if (desider){
                    $('#'+div_id).find('#alert')
                        .children('span')
                        .text("Your solution is correct!");
                }
                else{
                    $('#'+div_id).find('#alert')
                        .children('span')
                        .text("Your solution passed " + score + " out of " + max_score + " cases!");
                }

                prepareGradingTable(div_id);
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function prepareGradingTable(div_id) {

    var gradingTable = $("#"+div_id).find("#gradeMatrix");
    var score = 0;

    for (var i = 0; i < testcases.length; i++) {
        var current_testcase = testcases[i];

        var description = current_testcase.test_desc;
        if (description == ""){
            description = "No Description Provided"
        }
        var passed = current_testcase.passed_test;
        var testcaseInput = current_testcase.test_input;
        var testcaseOutput = current_testcase.expected_output;
        var result = current_testcase.test_val[2];

        var cleaner = $(gradingTable).find('#tcase_'+div_id+'_'+ i);
        if (cleaner){
            cleaner.remove();
        }

        var newRow = $('<tr class="gradeMatrixRow" id="tcase_'+div_id+'_'+i + '"></tr>');
        gradingTable.append(newRow);
        if ("exception" in current_testcase){
            newRow.append('<th class="alert alert-danger" colspan="6">' + current_testcase.exception + '<th>');
        }
        else{
            if (testcaseInput != null) {
                newRow.append('<td class="testInputCell">' + testcaseInput + '</td>');
                newRow.append('<td class="expectedCell">' + testcaseOutput + '</td>');
            }
            else {
                newRow.append('<td >' + "Hidden Test" +'</td>');
                newRow.append('<td >' + "Hidden Result" +'</td>');
            }

            newRow.append('<td class="testDescription">' + description + '</td>');
            newRow.append('<td class="testOutputCell">' + result +'</td>');

            newRow.append('<td class="statusCell"></td>');
            if (passed){
                var smFace = happyFace;
                score += 1;
            }
            else{
                var smFace = sadFace;
            }

            $("#"+div_id).find('#tcase_'+div_id+'_'+ i + ' td.statusCell').html(smFace.clone());
            if (testcaseInput != null){
                newRow.append('<td class="debugCell"><button id="' + div_id +"_"+i + '" class="debugBtn btn btn-info btn-mini" type="button" data-toggle="modal" data-target="#myModal">Trace</button></td>');
                bindDebugButton(div_id+"_"+i);
            }
            else{
                newRow.append('<td></td>')
            }
        }
    }
    add_to_history(score, div_id);
}

function create_timestamp(datetime){
    month_names = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    day = datetime.getDate();
    month = month_names[datetime.getMonth()];
    year = datetime.getFullYear();
    hour = datetime.getHours();
    minute = datetime.getMinutes();
    if (hour > 12){
        hour -= 12;
        cycle = "p.m.";
    }
    else{
        cycle = "a.m.";
    }

    formated_datetime = month + " " + day + ", "+year + ", " + hour+":"+minute+" "+cycle
    return formated_datetime;
}

function add_to_history(score, div_id){
    var sub_history_window = $("#"+div_id).find('#accordion');
    var datetime = new Date();
    datetime = create_timestamp(datetime);

    var new_entry = '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">';
    var local_name = "'history_mirror_999_"+code_problem_id+"'";

    new_entry += '<a data-toggle="collapse" data-parent="#accordion" href="#collapse_' + code_problem_id + '" onclick="delay_refresh_cm('+local_name+')">';
    new_entry += datetime + '<td> Score : ' + score +' / '+ testcases.length + '</td></a></h4></div>';
    new_entry += '<div id="collapse_'+ code_problem_id + '" class="panel-collapse collapse">';
    new_entry += '<div id="history_mirror_999_'+code_problem_id+'">' + myCodeMirrors[div_id].getValue() + '</div>';
    new_entry += '<ul class="list-group">';

    for (var i = 0; i < testcases.length; i++) {
        var test_case = testcases[i];
        var test_case_info = $("#"+div_id).find('#tcase_'+div_id+'_'+ i).children();

        var visible = ("Hidden Test" != test_case_info[0].innerHTML);

        var passed = test_case.passed_test;

        if (passed){
            new_entry += '<li class="list-group-item list-group-item-success">';
            new_entry += '<icon class="glyphicon glyphicon-ok"></icon>';
        }
        else{
            new_entry += '<li class="list-group-item list-group-item-danger">';
            new_entry += '<icon class="glyphicon glyphicon-remove"></icon>';
        }

        if (visible){
            new_entry += '&nbsp;&nbsp;' + test_case_info[0].innerHTML + ' -> ' + test_case_info[1].innerHTML +'</li>';
        }
        else{
            new_entry += '&nbsp;&nbsp;' + 'Hidden Test </li>'
        }
    }
    new_entry += '</ul></div></div>';

    sub_history_window.prepend(new_entry);
    create_history_code_mirror ('python', 3, 'history_mirror_999_'+code_problem_id);
    code_problem_id -= 1;
}

var code_problem_id = -1;
var myCodeMirrors = {};
var cmh_list = {};

$( document).ready(function() {

    var all_wrappers = $('.code-mirror-wrapper');

    for (var x = 0; x < all_wrappers.length; x++){
        $(all_wrappers[x]).children('#grade-code').hide();

//      SASHA! only for python; variable language is gone
        myCodeMirrors[all_wrappers[x].id] =
                history_code_mirror("python", 3, $(all_wrappers[x]).find("#div_id_submission"),
                        $(all_wrappers[x]).find('#div_id_submission').text(), false);

        $(all_wrappers[x]).find('#submit-id-submit').click(function(event){
            event.preventDefault();

            var div_id = $(this).parents('.code-mirror-wrapper')[0].id;

            if (myCodeMirrors[div_id].getValue() == ''){
                alert('There is no code to submit.');
            }
            else{
                getTestcases(div_id);
            }
        });
    }
});


