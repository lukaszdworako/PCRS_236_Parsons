//root is a global variable from base.html

$(document).ready(function() {
    var all_short_answer = $('div[id^="short_answer-"]');

    for (var x = 0; x < all_short_answer.length; x++){
        $(all_short_answer[x]).find('#submit-id-submit').click(function(event){
            event.preventDefault();
            var problem_pk = $(this)
                .parents('div[id^="short_answer-"]')
                .attr('id')
                .split("-")[1];
            var submission = $(this)
                .parents('#short_answer-'+problem_pk)
                .find('#id_submission').val();

            submit_short_answer(submission, problem_pk, $(this)
                .parents('div[id^="short_answer-"]')[0].id);
        });

        $(all_short_answer[x]).find("[name='history']").click(function(){
            var short_answer_id = $(this).parents('div[id^="short_answer-"]')[0].id;
            getSAHistory(short_answer_id);
        });
    }
});

function submit_short_answer(submission, problem_pk, div_id) {
    /**
     * Submits the solution to a short answer problem
     */

    var postParams = { csrftoken: csrftoken, submission: submission };

    $.post(root+'/problems/short_answer/'+problem_pk+'/run',
            postParams,
            function(data) {
                if (data['past_dead_line']){
                    alert('This submission is past the deadline!');
                    $('#'+div_id).find('#deadline_msg').remove();
                    $('#'+div_id)
                        .find('#alert')
                        .after('<div id="deadline_msg" class="red-alert">Submitted after the deadline!<div>');
                }
                var display_element = $('#short_answer-'+problem_pk)
                    .find('#alert');

                var score = data['score'];
                var max_score = data['max_score'];

                var is_correct = score >= max_score;
                $(display_element)
                    .toggleClass('red-alert', !is_correct);
                $(display_element)
                    .toggleClass('green-alert', is_correct);
                $(display_element)
                    .children('icon')
                    .toggleClass('remove-icon', !is_correct);
                $(display_element)
                    .children('icon')
                    .toggleClass('ok-icon', is_correct);
                if (is_correct){
                    var alert_msg = 'Your solution is complete.';
                }
                else{
                    var alert_msg = 'Your solution has not earned full credit. ' + data['message'];
                    if (data['error_msg']){
                        alert_msg = data['error_msg'];
                    }
                }
                $(display_element).children('span').text(alert_msg);
                $('#'+div_id).find('.screen-reader-text').prop('title', alert_msg);

                console.log(data['submission']);

                returnable = {
                    'sub_time': new Date(),
                    'submission': data['submission'],
                    'score': score,
                    'out_of': max_score,
                    'best': data['best'],
                    'past_dead_line': false,
                    'problem_pk': problem_pk,
                    'sub_pk': data['sub_pk']
                }
                if (data['best'] && !data['past_dead_line']){
                    update_marks(div_id, score, max_score);
                }

                var flag = ($('#'+div_id).find('#history_accordion').children().length != 0);
                add_short_answer_history_entry(returnable, div_id, flag)
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function getSAHistory(short_answer_id){
    /**
     * Get the previous submissions for the problem
     */

    var postParams = { csrftoken: csrftoken };

    $.post(root+'/problems/short_answer/'+short_answer_id.split("-")[1]+'/history',
    postParams,
    function(data){
        $('#'+short_answer_id).find('#history_accordion').html("");
        show_short_answer_history(data, short_answer_id);
        $('#history_window_' + short_answer_id).modal('show');
    },
    'json')
    .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function show_short_answer_history(data, div_id){
    /**
     * Add the previous submissions to the history one at a time
     */

    for (var x = 0; x < data.length; x++){
        add_short_answer_history_entry(data[x], div_id, 0);
    }
}

function create_short_answer_timestamp(datetime){
    /**
     * Convert Django time to PCRS display time for history
     */

    var month_names = ["January","February","March","April","May","June",
                       "July","August","September","October","November","December"];
    var day = datetime.getDate();
    var month = month_names[datetime.getMonth()];
    var year = datetime.getFullYear();
    var hour = datetime.getHours();
    var minute = datetime.getMinutes();
    var cycle = "";

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

function add_short_answer_history_entry(data, div_id, flag){
    /**
     * Add a given previous submission "data" to the history of a given "div_id"
     * "flag" 0 appends anf "flag" 1 prepends
     */

    var sub_time = new Date(data['sub_time']);
    sub_time = create_short_answer_timestamp(sub_time);

    var panel_class = "pcrs-panel-default";

    if (data['past_dead_line']){
        panel_class = "pcrs-panel-warning";
        sub_time = sub_time + " Submitted after the deadline";
    }

    star_text = "";

    if (data['best'] && !data['past_dead_line']){
        panel_class = "pcrs-panel-star";
        star_text = '<icon style="font-size:1.2em" class="star-icon"> </icon>';
        $('#'+div_id).find('#history_accordion').find(".star-icon").removeClass("star-icon");
        $('#'+div_id).find('#history_accordion').find(".pcrs-panel-star")
            .addClass("pcrs-panel-default").removeClass("pcrs-panel-star");
    }

    var entry = $('<div/>',{class:panel_class});
    var header1 = $('<div/>',{class:"pcrs-panel-heading"});
    var header2 = $('<h4/>', {class:"pcrs-panel-title"});
    var header4 = $('<td/>', {html:"<span style='float:right;'> " + star_text + " "
                                      + "<sup style='font-size:0.9em'>" + data['score'] + "</sup>"
                                      + " / "
                                      + "<sub style='font-size:0.9em'>"+ data['out_of']+" </sub>"
                                      + "</span>"});
    var header3 = $('<a/>', {'data-toggle':"collapse",
                             'data-parent':"#history_accordion",
                              href:"#collapse_"+data['sub_pk'],
                              html:sub_time + header4.html()});

    var cont1 = $('<div/>', {class:"pcrs-panel-collapse collapse",
                                  id:"collapse_" + data['sub_pk']});

    var cont2 = $('<div/>', {id:"SA_answer_"
                                      + data['problem_pk']
                                      + "_"
                                      + data['sub_pk'],
                                  html:data['submission']});

    header2.append(header3);
    header1.append(header2);

    entry.append(header1);
    cont1.append(cont2);
    entry.append(cont1);

    if (flag == 0){
        $('#'+div_id).find('#history_accordion').append(entry);
    }
    else{
        $('#'+div_id).find('#history_accordion').prepend(entry);
    }
}
