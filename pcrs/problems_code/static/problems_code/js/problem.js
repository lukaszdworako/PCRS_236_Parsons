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

    var postParams = { language : language, user_script : newCode};
    executeGenericVisualizer("gen_execution_trace_params", postParams);

    $.post(root + '/problems/code/visualizer-details',
            postParams,
            function(data) {
                executeGenericVisualizer("create_visualizer", data);
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function getHistory(div_id){
    var postParams = { csrftoken: csrftoken };
    var problem_path = "";
    check_language(div_id);
    if (language == 'python'){
        problem_path = root+'/problems/code/'+div_id.split("-")[1]+'/history';
    }
    else if (language == 'sql'){
        problem_path = root+'/problems/sql/'+div_id.split("-")[1]+'/history';
    }
    else if (language == 'ra'){
        problem_path = root+'/problems/ra/'+div_id.split("-")[1]+'/history';
    }
    $.post(problem_path,
        postParams,
        function(data){
            show_history(data, div_id);
        },
        'json')
        .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function add_history_entry(data, div_id, flag){

    var sub_time = new Date(data['sub_time']);
    sub_time = create_timestamp(sub_time);

    data['past_dead_line'] = false;

    var panel_class = "panel panel-default";

    if (data['past_dead_line']){
        panel_class = "panel panel-warning";
        sub_time = "Past dead line";
    }

    star_text = "";
    if (data['best']){
        panel_class = "panel panel-primary";
        star_text = '<icon style="font-size:1.2em" class="glyphicon glyphicon-star" title="Latest Best Submission"> </icon>';
        $('#'+div_id).find('#history_accordion').find(".glyphicon-star").remove();
        $('#'+div_id).find('#history_accordion').find(".panel-primary")
            .addClass("panel-default").removeClass("panel-primary");
    }

    var entry = $('<div/>',{class:panel_class});
    var header1 = $('<div/>',{class:"panel-heading"});
    var header2 = $('<h4/>', {class:"panel-title"});
    var header4 = $('<td/>', {html:"<span style='float:right;'> " + star_text + " "
                                      + "<sup style='font-size:0.9em'>" + data['score'] + "</sup>"
                                      + " / "
                                      + "<sub style='font-size:0.9em'>" + data['out_of'] + "</sub>"
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

    var cont1 = $('<div/>', {class:"panel-collapse collapse",
                                  id:"collapse_" + data['sub_pk']});

    var cont2 = $('<div/>', {id:"history_mirror_"
                                      + data['problem_pk']
                                      + "_"
                                      + data['sub_pk'],
                                  html:data['submission']});

    var cont3 = $('<ul/>', {class:"list-group"});


    for (var num = 0; num < data['tests'].length; num++){

        var lc = "";
        var ic = "";
        var test_msg = "";
        if (data['tests'][num]['passed']){
            lc = "list-group-item list-group-item-success";
            ic = "<icon class='glyphicon glyphicon-ok'> </icon>";
        }
        else{
            lc = "list-group-item list-group-item-danger";
            ic = "<icon class='glyphicon glyphicon-remove'> </icon>";
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
    check_language(div_id);
    if (language == "python"){
        create_history_code_mirror("python", 3, "history_mirror_"
                                                + data['problem_pk']
                                                + "_"
                                                + data['sub_pk']);
    }
    else{
        create_history_code_mirror(language, false, "history_mirror_"
                                                + data['problem_pk']
                                                + "_"
                                                + data['sub_pk']);
    }
}

function show_history(data, div_id){

    for (var x = 0; x < data.length; x++){
        add_history_entry(data[x], div_id, 0);
    }
}

function getTestcases(div_id) {
    var postParams = { csrftoken: csrftoken, submission: myCodeMirrors[div_id].getValue() };
    var call_path = "";
    check_language(div_id);
    if (language == 'python'){
        call_path = root + '/problems/code/'+div_id.split("-")[1]+'/run'
    }
    else if (language == 'sql'){
        call_path = root + '/problems/sql/'+div_id.split("-")[1]+'/run';
    }
    else if (language == 'ra'){
        call_path = root + '/problems/ra/'+div_id.split("-")[1]+'/run';
    }
    $.post(call_path,
            postParams,
            function(data) {
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
                if (language == 'python'){
                    prepareGradingTable(div_id, data['best'], data['past_dead_line'], data['sub_pk'], max_score);
                }
                else if (language=='sql'){
                    prepareSqlGradingTable(div_id, data['best'], data['past_dead_line'], data['sub_pk'], max_score);
                }
                else if (language=='ra'){
                    prepareSqlGradingTable(div_id, data['best'], data['past_dead_line'], data['sub_pk'], max_score);
                }
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function prepareSqlGradingTable(div_id, best, past_dead_line, sub_pk, max_score) {

    var score = 0;
    var tests = [];
    var table_location = $('#'+div_id).find('#table_location');
    table_location.empty();

    for (var i = 0; i < testcases.length; i++) {
        var current_testcase = testcases[i];
        var main_table = $('<table/>', {id:"gradeMatrix"+current_testcase['testcase'],
                                        class:"table span12"});

        var expected_td = $('<td/>', {class:"gradeMatrixRow table-left"}).append("Expected");
        var actual_td = $('<td/>', {class:"gradeMatrixRow table-right "}).append("Actual");

        var expected_table = $('<table/>', {class:"table span6"});
        var actual_table = $('<table/>', {class:"table span6"});

        var expected_entry = $('<tr/>', {class:"gradeMatrixRow"});
        var actual_entry = $('<tr/>', {class:"gradeMatrixRow"});

        if (current_testcase['passed']){
            table_location.append("<div class='alert alert-success'><icon class='glyphicon glyphicon-ok'></icon><span> Test Case Passed</span></div>");
            score++;
        }
        else{
            table_location.append("<div class='alert alert-danger'><icon class='glyphicon glyphicon-remove'></icon><span> Test Case Failed</span></div>");
        }

        for (var header = 0; header < current_testcase['expected_attrs'].length; header++){
            expected_entry.append("<td colspan='"+ 6/current_testcase['expected_attrs'].length +"'><b>"+ current_testcase['expected_attrs'][header] +"</b></td>");
        }

        for (var header = 0; header < current_testcase['actual_attrs'].length; header++){
            actual_entry.append("<td colspan='"+ 6/current_testcase['expected_attrs'].length +"'><b>"+ current_testcase['actual_attrs'][header] +"</b></td>");
        }

        expected_table.append(expected_entry);
        actual_table.append(actual_entry);

        for (var entry = 0; entry < current_testcase['expected'].length; entry++){
            var entry_class = 'gradeMatrixRow';
            var test_entry = current_testcase['expected'][entry];
            if (test_entry['missing']){
                entry_class = "gradeMatrixRow sql-missing";
            }
            var expected_entry = $('<tr/>', {class:entry_class});
            for (var header = 0; header < current_testcase['expected_attrs'].length; header++){
                expected_entry.append("<td colspan='" +
                                     6/current_testcase['expected_attrs'].length +
                                     "'>" +
                                     test_entry[current_testcase['expected_attrs'][header]] +
                                     "</td>");
            }
            expected_table.append(expected_entry);
        }

        for (var entry = 0; entry < current_testcase['actual'].length; entry++){
            var entry_class = 'gradeMatrixRow';
            var test_entry = current_testcase['actual'][entry];
            if (test_entry['extra']){
                entry_class = 'gradeMatrixRow sql-extra';
            }
            else if (test_entry['out_of_order']){
                entry_class = 'gradeMatrixRow sql-order';
            }
            var actual_entry = $('<tr/>', {class:entry_class});
            for (var header = 0; header < current_testcase['actual_attrs'].length; header++){

               actual_entry.append("<td colspan='" +
                                   6/current_testcase['actual_attrs'].length +
                                   "'>" +
                                   test_entry[current_testcase['actual_attrs'][header]] +
                                   "</td>");
            }
            actual_table.append(actual_entry);
        }

        expected_td.append(expected_table);
        actual_td.append(actual_table);

        main_table.append(expected_td);
        main_table.append(actual_td);
        table_location.append(main_table);
    }
    var data = {'sub_time':new Date(),
            'submission':myCodeMirrors[div_id].getValue(),
            'score':score,
            'best':best,
            'past_dead_line':past_dead_line,
            'problem_pk':div_id.split("-")[1],
            'sub_pk':sub_pk,
            'out_of':max_score,
            'tests': table_location};
    if (best){
        var side_bar = $('.nav.bs-docs-sidenav').find('#sb_'+div_id);
        var new_title = $('#'+div_id).find(".widget_title")[0].firstChild.data.trim();
        if (score == max_score){
            $('#'+div_id).find(".widget_title").find('span').empty();
            $('#'+div_id).find(".widget_title").find('span').append($('<i/>', {class:"glyphicon glyphicon-ok icon-ok-green"}));
            new_title += " : Complete"
            side_bar.css("color","green");
            side_bar.removeClass();
            side_bar.addClass("glyphicon glyphicon-check");
        }
        else{
            $('#'+div_id).find(".widget_title").find('sup').text(score);
            $('#'+div_id).find(".widget_title").find('sub').text(max_score);
            new_title += " : " + score + " / " + max_score;
            side_bar.css("color","DarkOrange");
        }
        side_bar.prop('title', new_title);
    }
    if ($('#'+div_id).find('#history_accordion').children().length != 0){
        add_history_entry(data, div_id, 1);
    }
}


function prepareGradingTable(div_id, best, past_dead_line, sub_pk, max_score) {

    var gradingTable = $("#"+div_id).find("#gradeMatrix");
    var score = 0;
    var tests = [];
    for (var i = 0; i < testcases.length; i++) {
        var current_testcase = testcases[i];

        var description = current_testcase.test_desc;
        if (description == ""){
            description = "No Description Provided"
        }
        var passed = current_testcase.passed_test;
        var testcaseInput = current_testcase.test_input;
        var testcaseOutput = current_testcase.expected_output;

        var result = create_output(current_testcase.test_val);

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
        var test = {'visible':testcaseInput != null,
                    'input': testcaseInput,
                    'output': testcaseOutput,
                    'passed': passed,
                    'description': description};
        tests.push(test);
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
    if (best){
        var side_bar = $('.nav.bs-docs-sidenav').find('#sb_'+div_id);
        var new_title = $('#'+div_id).find(".widget_title")[0].firstChild.data.trim();
        if (score == max_score){
            $('#'+div_id).find(".widget_title").find('span').empty();
            $('#'+div_id).find(".widget_title").find('span').append($('<i/>', {class:"glyphicon glyphicon-ok icon-ok-green"}));
            new_title += " : Complete"
            side_bar.css("color","green");
            side_bar.removeClass();
            side_bar.addClass("glyphicon glyphicon-check");
        }
        else{
            $('#'+div_id).find(".widget_title").find('sup').text(score);
            $('#'+div_id).find(".widget_title").find('sub').text(max_score);
            new_title += " : " + score + " / " + max_score;
            side_bar.css("color","DarkOrange");
        }
        side_bar.prop('title', new_title);
    }
    if ($('#'+div_id).find('#history_accordion').children().length != 0){
        add_history_entry(data, div_id, 1);
    }
}

function create_timestamp(datetime){
    month_names = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    day = datetime.getDate();
    month = month_names[datetime.getMonth()];
    year = datetime.getFullYear();
    hour = datetime.getHours();
    minute = datetime.getMinutes();
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

    formated_datetime = month + " " + day + ", "+year + ", " + hour+":"+minute+" "+cycle
    return formated_datetime;
}

function create_output(input){
    brakets_o = {"list":"[","tuple":"(","dict":"{"};
    brakets_c = {"list":"]","tuple":")","dict":"}"};
    if (input.length == 2){
        return create_output(input[0])+":"+create_output(input[1]);
    }
    else if (input[0] == "list" || input[0] == "tuple" || input[0] == "dict"){
        var output = brakets_o[input[0]];
        for (var o_index = 2; o_index < input.length; o_index++){
            output += create_output(input[o_index]);
            if (o_index != input.length - 1){
                output += ", "
            }
        }
        output += brakets_c[input[0]];
        return output
    }
    else if(input[0] == "string"){
        return "'"+input[2]+"'";
    }
    else if(input[0] == "float"){
        if (String(input[2]).indexOf(".")>-1){
            return input[2]
        }
        else{
            return input[2]+".0"
        }
    }
    else{
        return input[2]
    }
}

function check_language(container){
    if (container.indexOf("code") > -1){
        language = 'python';
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
}

var code_problem_id = -1;
var myCodeMirrors = {};
var cmh_list = {};

$( document).ready(function() {

    var all_wrappers = $('.code-mirror-wrapper');

    for (var x = 0; x < all_wrappers.length; x++){
        $(all_wrappers[x]).children('#grade-code').hide();
        check_language(all_wrappers[x].id);
        if (language == "python"){
            myCodeMirrors[all_wrappers[x].id] =
                    history_code_mirror("python", 3, $(all_wrappers[x]).find("#div_id_submission"),
                            $(all_wrappers[x]).find('#div_id_submission').text(), false);
        }
        else if (language == "sql"){
            myCodeMirrors[all_wrappers[x].id] =
                    history_code_mirror(language, 'text/x-sql', $(all_wrappers[x]).find("#div_id_submission"),
                            $(all_wrappers[x]).find('#div_id_submission').text(), false);
        }
        else if (language == "ra"){
            myCodeMirrors[all_wrappers[x].id] =
                    history_code_mirror(language, 'text/x-sql', $(all_wrappers[x]).find("#div_id_submission"),
                            $(all_wrappers[x]).find('#div_id_submission').text(), false);
        }

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
        $(all_wrappers[x]).find("[name='history']").one("click", (function(){
            var div_id = $(this).parents('.code-mirror-wrapper')[0].id;
            getHistory(div_id);
        }));
    }
    for (var key in myCodeMirrors){
        myCodeMirrors[key].refresh();
    }
});


