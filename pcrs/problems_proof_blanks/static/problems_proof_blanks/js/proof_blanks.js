//root is a global variable from base.html
$(document).ready(function() {
    var all_proof_blanks = $('div[id^="proof_blanks-"]');

    for (var x = 0; x < proof_blanks.length; x++){
        $(all_proof_blanks[x]).find('#submit-id-submit').click(function(event){
            event.preventDefault();
            var problem_pk = $(this)
                .parents('div[id^="proof_blanks-"]')
                .attr('id')
                .split("-")[1];
            var submission = $(this)
                .parents('#proof_blanks-'+problem_pk)
                .find('#id_submission').val();

            submit_short_answer(submission, problem_pk, $(this)
                .parents('div[id^="proof_blanks-"]')[0].id);
        });

        $(all_short_answer[x]).find("[name='history']").one("click", (function(){
            var short_answer_id = $(this).parents('div[id^="short_answer-"]')[0].id;
            getSAHistory(short_answer_id);
        }));
    }
});
