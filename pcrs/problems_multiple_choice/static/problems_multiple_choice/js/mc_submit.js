$( document ).ready(function() {

    $("#correct"+problem_pk).hide();
    $("#incorrect"+problem_pk).hide();

    $('#submit-id-submit').click(function(event){
        event.preventDefault();
        $("#correct"+problem_pk).hide();
        $("#incorrect"+problem_pk).hide();

        var checkboxes = $($($($(this).parent().siblings('fieldset')[0]).children()[0]).children()[0]).children();
        var submission = [];

        for (var x = 0; x < checkboxes.length; x++){
            if ($(checkboxes[x]).children()[0].checked){
                submission.push($(checkboxes[x]).children()[0].value);
            }
        }
        submit_mc(submission);
    });

    function submit_mc(submission) {

        var postParams = { csrftoken: csrftoken, options: submission };
        $.post('/problems/multiple_choice/'+problem_pk+'/run',
                postParams,
                function(data) {
                    var score = data['score'];
                    var max_score = data['max_score'];
                    if (score == max_score){
                        $("#correct"+problem_pk).show();
                    }
                    else{
                        $("#incorrect"+problem_pk).show();
                    }
                },
            "json")
         .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
    }

});
