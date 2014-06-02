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
        console.log(submission, problem_pk);
        var postParams = { csrftoken: csrftoken, options : submission  };
        $.post('/problems/multiple_choice/'+problem_pk+'/run',
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
