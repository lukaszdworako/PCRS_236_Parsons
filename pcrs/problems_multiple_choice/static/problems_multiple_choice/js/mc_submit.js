$( document ).ready(function() {

    all_mc = $('div[id^="multiple_choice-"]').find('#submit-id-submit');

    for (var x = 0; x < all_mc.length; x++){
        $(all_mc[x]).click(function(event){
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
            submit_mc(submission, problem_pk);
        });
    }
});

    function submit_mc(submission, problem_pk) {
        var postParams = { csrftoken: csrftoken, options : submission  };
<<<<<<< HEAD
        $.post(root+'/problems/multiple_choice/'+problem_pk+'/run',
=======

        /* Hack to find the site prefix */
        var prefix = window.location.href.match(/\/[a-z0-9\/]*(?=\/problems\/)/);
        if (prefix == null) { prefix = ''; }

        $.post(prefix + '/problems/multiple_choice/'+problem_pk+'/run',
>>>>>>> 541ea94b0ac72c6f5710817b705ab31a416e1b3d
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
                },
            "json")
         .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
    }
