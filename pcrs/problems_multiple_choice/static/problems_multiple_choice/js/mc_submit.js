//root is a global variable from base.html

$( document ).ready(function() {

    var all_mc = $('div[id^="multiple_choice-"]');

    for (var x = 0; x < all_mc.length; x++){
        $(all_mc[x]).find('#submit-id-submit').click(function(event){
            event.preventDefault();
            var problem_pk = $(this)
                .parents('div[id^="multiple_choice-"]')
                .attr('id')
                .split("-")[1];

            var checkboxes = $(this)
                .parents('#multiple_choice-'+problem_pk)
                .find('.controls')
                .children();

            var submission = [];
            for (var x = 0; x < checkboxes.length; x++){
                if ($(checkboxes[x]).children('input').is(':checked')){
                    submission.push($(checkboxes[x]).children('input').val());
                }
            }
            submit_mc(submission, problem_pk, $(this)
                .parents('div[id^="multiple_choice-"]')[0].id);
        });

        $(all_mc[x]).find("[name='history']").click(function(){
            var mc_id = $(this).parents('div[id^="multiple_choice-"]')[0].id;
            getMCHistory(mc_id);
        });
    }
});

function getMCHistory(mc_id){
    /**
     * get all previous submissions for the problem given its main div id field "mc_id"
     */

    var postParams = { csrftoken: csrftoken };

    $.post(root+'/problems/multiple_choice/'+mc_id.split("-")[1]+'/history',
    postParams,
    function(data){
        $('#'+mc_id).find('#history_accordion').html("");
        show_mc_history(data, mc_id);
        $('#history_window_' + mc_id).modal('show');
    },
    'json')
    .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}

function show_mc_history(data, div_id){
    /**
     * add all the previous submissions one at a time to the history inside the given div "div_id"
     */

    for (var x = 0; x < data.length; x++){
        add_mc_history_entry(data[x], div_id, 0);
    }
}

function create_mc_timestamp(datetime){
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

function add_mc_history_entry(data, div_id, flag){
    /**
     * Add a given previous submission "data" to the history of a given "div_id"
     * "flag" 0 appends anf "flag" 1 prepends
     */

    var sub_time = new Date(data['sub_time']);
    sub_time = create_mc_timestamp(sub_time);

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
    var header2 = $('<h4/>', {class:"pcrs-panel-title", 'style':"padding:0"});
    var header4 = $('<td/>', {html:"<span style='float:right;'> " + star_text + " "
                                      + "<sup style='font-size:0.9em'>" + data['score'] + "</sup>"
                                      + " / "
                                      + "<sub style='font-size:0.9em'>"+ data['out_of']+" </sub>"
                                      + "</span>"});

    var header3 = $('<a/>', {'data-toggle':"collapse",
                             'data-parent':"#history_accordion",
                             'style':"display: block; border-radius: 4px; min-height: 40px",
                             'class':"pcrs-panel-heading pcrs-panel-title collapsed",
                              href:"#collapse_"+data['sub_pk'],
                              html:sub_time + header4.html()});

    var cont1 = $('<div/>', {class:"pcrs-panel-collapse collapse",
                                  id:"collapse_" + data['sub_pk']});

    var cont2 = $('<div/>', {id:"MC_answer_"
                                      + data['problem_pk']
                                      + "_"
                                      + data['sub_pk'],
                                  html:data['submission']});

    var cont3 = $('<ul/>', {class:"pcrs-list-group"});

    for (var num = 0; num < data['options'].length; num++){

        var ic = "<icon class='unchecked-icon'> </icon>";
        var test_msg = "";
        if (data['options'][num]['selected']){
            ic = "<icon class='checked-icon'> </icon>";
        }

        var cont4 = $('<div/>', {
            class: "pcrs-list-group-item",
            html:ic + " " + data['options'][num]['option']
        });

        cont3.append(cont4);
    }

    header2.append(header3);

    entry.append(header2);
    cont1.append(cont2);
    cont1.append(cont3);
    entry.append(cont1);

    if (flag == 0){
        $('#'+div_id).find('#history_accordion').append(entry);
    }
    else{
        $('#'+div_id).find('#history_accordion').prepend(entry);
    }
}

function submit_mc(submission, problem_pk, div_id) {
    /**
     * Submits the students solution to a MC problem
     */

    var postParams = { csrftoken: csrftoken, submission : submission  };

    $.post(root+'/problems/multiple_choice/'+problem_pk+'/run',
            postParams,
            function(data) {
                if (data['past_dead_line']){
                    alert('This submission is past the deadline!');
                    $('#'+div_id).find('#deadline_msg').remove();
                    $('#'+div_id)
                        .find('#alert')
                        .after('<div id="deadline_msg" class="red-alert">Submitted after the deadline!<div>');
                }
                var display_element = $('#multiple_choice-'+problem_pk)
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
                    $(display_element)
                        .children('span')
                        .text('Your solution is complete.');
                    $('#'+div_id).find('.screen-reader-text').prop('title', 'Your solution is complete.');
                }
                else{
                    var alert_msg = 'Your solution is either incorrect or incomplete!';
                    if (data['error_msg']){
                        alert_msg = data['error_msg'];
                    }
                    $(display_element).children('span').text(alert_msg);
                    $('#'+div_id).find('.screen-reader-text').prop('title', alert_msg);
                }

                mc_options = $('#'+div_id).find('[id^="id_options_"]');

                options_list = []

                for (var opt = 0; opt < mc_options.length; opt++){
                    options_list.push({
                        'selected': $(mc_options[opt]).is(':checked'),
                        'option': $(mc_options[opt]).parents('.checkbox').text()
                    });
                }

                returnable = {
                    'sub_time': new Date(),
                    'score': score,
                    'out_of': max_score,
                    'best': data['best'],
                    'past_dead_line': false,
                    'problem_pk': problem_pk,
                    'sub_pk': data['sub_pk'],
                    'options': options_list
                }
                if (data['best'] && !data['past_dead_line']){
                    update_marks(div_id, score, max_score);
                }

                var flag = ($('#'+div_id).find('#history_accordion').children().length != 0);
                add_mc_history_entry(returnable, div_id, flag)
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}
