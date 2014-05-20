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
            prepareVisualizer("debug", testcaseCode)},250
        );
    });
}

function prepareVisualizer(option, data) {
    var newCode = myCodeMirror.getValue() + "\n";

    var addCode = (option == "viz") ? myCodeMirror.getValue() : data;
    newCode += addCode;
    getVisualizerComponents(newCode);
}

function getVisualizerComponents(newCode) {
    var postParams = { language : language, user_script : newCode};
    executeGenericVisualizer("gen_execution_trace_params", postParams);
    $.post('visualizer-details',
            postParams,
            function(data) {
                executeGenericVisualizer("create_visualizer", data);
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function getTestcases() {

    var postParams = { csrftoken: csrftoken, submission: myCodeMirror.getValue() };

    $.post('/problems/coding/'+problem_id+'/run',
            postParams,
            function(data) {
                testcases = data;
                $("#grade-code").show();
                prepareGradingTable();
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function prepareGradingTable() {

    var gradingTable = $("#gradeMatrix");
    var score = 0;
    console.log(testcases[0]);

    for (var i = 0; i < testcases.length; i++) {
        var current_testcase = testcases[i];
        var passed = current_testcase.passed_test;
        var testcaseInput = current_testcase.test_input;
        var testcaseOutput = current_testcase.expected_output;
        var result = current_testcase.test_val[2];

        var cleaner = $("#tcase_"+i);
        if (cleaner){
            cleaner.remove();
        }

        var newRow = $('<tr class="gradeMatrixRow" id="tcase_' + i + '"></tr>');
        gradingTable.append(newRow);

        if (testcaseInput != null) {
            newRow.append('<td class="testInputCell">' + testcaseInput + '</td>');
            newRow.append('<td class="expectedCell">' + testcaseOutput + '</td>');
        }
        else {
            newRow.append('<td colspan=1>' + "Hidden Test" +'</td>');
            newRow.append('<td colspan=1>' + "Hidden Result" +'</td>');
        }

        newRow.append('<td class="testDescription">' + 'GET DESCRIPTION!' + '</td>');
        newRow.append('<td class="testOutputCell">' + result +'</td>');

        newRow.append('<td class="statusCell"></td>');
        if (passed){
            var smFace = happyFace;
            score += 1;
        }
        else{
            var smFace = sadFace;
        }

        $('#tcase_' + i + ' td.statusCell').html(smFace.clone());
        if (testcaseInput != null){
            newRow.append('<td class="debugCell"><button id="' + i + '" class="debugBtn btn btn-info btn-mini" type="button" data-toggle="modal" data-target="#myModal">Trace</button></td>');
            bindDebugButton(i);
        }
        else{
            newRow.append('<td></td>')
        }
    }
    add_to_history(score);
}

function create_timestamp(datetime){
    month_names = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    day = datetime.getDate();
    month = month_names[datetime.getMonth()];
    year = datetime.getYear();
    hour = datetime.getHours();
    minute = datetime.getMinutes();
    if (hour > 12){
        hour -= 12;
        cycle = "p.m.";
    }
    else{
        cycle = "a.m.";
    }

    formated_datetime = month + " " + day + ","+year + ", " + hour+":"+minute+" "+cycle
    return formated_datetime;
}

function add_to_history(score){
    var sub_history_window = $('#accordion');
    var datetime = new Date();
    datetime = create_timestamp(datetime);

    var new_entry = '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">'
    new_entry += '<a data-toggle="collapse" data-parent="#accordion" href="#collapse_' + code_problem_id + '" onclick="delay_refresh_cm()">'
    new_entry += datetime + '<td> Score :' + score +'/'+ testcases.length + '</td></a></h4></div>'
    new_entry += '<div id="collapse_'+ code_problem_id + '" class="panel-collapse collapse">'
    new_entry += '<div id="history_mirror_999_'+code_problem_id+'">' + myCodeMirror.getValue() + '</div>'
    new_entry += '<ul class="list-group">'
    for (var i = 0; i < testcases.length; i++) {
        var test_case = testcases[i];
        var test_case_info = $('#tcase_'+ i).children();
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

$( document).ready(function() {

    $("#grade-code").hide();

    $('#submit').click(function(){
        if (myCodeMirror.getValue() == ''){
            alert('There is no code to submit.');
        }
        else{
            getTestcases();
        }
    });

});


