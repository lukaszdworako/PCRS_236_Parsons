$( document ).ready(function() {

    all_mc = $('div[id^="multiple_choice-"]');

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

        $(all_mc[x]).find("[name='history']").one("click", (function(){
            var mc_id = $(this).parents('div[id^="multiple_choice-"]')[0].id;
            getMCHistory(mc_id);
        }));
    }
});

    function getMCHistory(mc_id){
        var postParams = { csrftoken: csrftoken };
        $.post(root+'/problems/multiple_choice/'+mc_id.split("-")[1]+'/history',
        postParams,
        function(data){
            show_mc_history(data, mc_id);
        },
        'json')
        .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
    }

    function show_mc_history(data, div_id){
        for (var x = 0; x < data.length; x++){
            add_mc_history_entry(data[x], div_id, 0);
        }
    }

    function create_mc_timestamp(datetime){
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

    function add_mc_history_entry(data, div_id, flag){

        var sub_time = new Date(data['sub_time']);
        sub_time = create_mc_timestamp(sub_time);

        data['past_dead_line'] = false;

        var panel_class = "panel panel-default";

        if (data['past_dead_line']){
            panel_class = "panel panel-warning";
            sub_time = "Past dead line";
        }

        star_text = "";
        if (data['best']){
            panel_class = "panel panel-primary";
            star_text = '<icon style="font-size:1.2em" class="glyphicon glyphicon-star"> </icon>';
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
                                          + "<sub style='font-size:0.9em'>"+ data['out_of']+" </sub>"
                                          + "</span>"});

        var header3 = $('<a/>', {'data-toggle':"collapse",
                                 'data-parent':"#history_accordion",
                                  href:"#collapse_"+data['sub_pk'],
                                  html:sub_time + header4.html()});

        var cont1 = $('<div/>', {class:"panel-collapse collapse",
                                      id:"collapse_" + data['sub_pk']});

        var cont2 = $('<div/>', {id:"MC_answer_"
                                          + data['problem_pk']
                                          + "_"
                                          + data['sub_pk'],
                                      html:data['submission']});

        var cont3 = $('<ul/>', {class:"list-group"});

        for (var num = 0; num < data['options'].length; num++){

            var ic = "<icon class='glyphicon glyphicon-unchecked'> </icon>";
            var test_msg = "";
            if (data['options'][num]['selected']){
                ic = "<icon class='glyphicon glyphicon-check'> </icon>";
            }

            var cont4 = $('<li/>', {
                class: "list-group-item",
                html:ic + " " + data['options'][num]['option']
            });

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
    }

    function submit_mc(submission, problem_pk, div_id) {
        var postParams = { csrftoken: csrftoken, options : submission  };

        $.post(root+'/problems/multiple_choice/'+problem_pk+'/run',
                postParams,
                function(data) {
                    var display_element = $('#multiple_choice-'+problem_pk)
                        .find("#alert");

                    var score = data['score'];
                    var max_score = data['max_score'];

                    var desider = score == max_score;
                    $(display_element)
                        .toggleClass("alert-danger", !desider);
                    $(display_element)
                        .toggleClass("alert-success", desider);
                    $(display_element)
                        .children('icon')
                        .toggleClass("glyphicon-remove", !desider);
                    $(display_element)
                        .children('icon')
                        .toggleClass("glyphicon-ok", desider);
                    if (desider){
                        $(display_element)
                            .children('span')
                            .text("Your solution is correct!");
                    }
                    else{
                        $(display_element)
                            .children('span')
                            .text("Your solution is incorrect!");
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
                    if (data['best']){
                        var side_bar = $('.nav.bs-docs-sidenav').find('#sb_'+div_id);
                        var new_title = $('#'+div_id).find("h3")[0].firstChild.data.trim();
                        if (score == max_score){
                            $('#'+div_id).find('h3').find('span').empty();
                            $('#'+div_id).find('h3').find('span').append($('<i/>', {class:"glyphicon glyphicon-ok icon-ok-green"}));
                            side_bar.css("color","green");
                            side_bar.removeClass();
                            side_bar.addClass("glyphicon glyphicon-check");
                            new_title += " : Complete"
                        }
                        else{
                            $('#'+div_id).find('h3').find('sup').text(score);
                            $('#'+div_id).find('h3').find('sub').text(max_score);
                            new_title += " : " + score + " / " + max_score;
                            side_bar.css("color","DarkOrange");
                        }
                        side_bar.prop('title', new_title);
                    }

                    if ($('#'+div_id).find('#history_accordion').children().length != 0){
                        add_mc_history_entry(returnable, div_id, 1)
                    }
                },
            "json")
         .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
    }
