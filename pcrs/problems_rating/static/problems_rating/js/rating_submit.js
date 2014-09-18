//root is a global variable from base.html

$( document ).ready(function() {

    var all_rating = $('div[id^="rating-"]');

    for (var x = 0; x < all_rating.length; x++){
        $(all_rating[x]).find('#submit-id-submit').click(function(event){
            event.preventDefault();
            var problem_pk = $(this)
                .parents('div[id^="rating-"]')
                .attr('id')
                .split("-")[1];

            // Hard coded for likert
            var checkboxes = $(this)
                .parents('#rating-'+problem_pk)
                .find('.controls')
                .children().children();

            for (var x = 0; x < checkboxes.length; x++){
                if ($(checkboxes[x]).find('input')[0].checked) {
                    var rating = $(checkboxes[x]).find('input')[0].value;
                    break;
                }
            }
            submit_rating(rating, problem_pk, $(this).parents('div[id^="rating-"]')[0].id);
        });
    }
});

function submit_rating(rating, problem_pk, div_id) {
    var postParams = { csrftoken: csrftoken, rating: rating };

    $.post(root+'/problems/rating/'+problem_pk+'/run',
            postParams,
            function(data) {
                if (data['past_dead_line']) {
                    alert('This submission is past the deadline!');
                    $('#'+div_id).find('#deadline_msg').remove();
                    $('#'+div_id)
                        .find('#alert')
                        .after('<div id="deadline_msg" class="red-alert">Submitted after the deadline!<div>');
                    $('#'+div_id).find('.screen-reader-text').prop('title',"Submitted after the deadline!");    
                }

                var display_element = $('#rating-'+problem_pk)
                    .find("#alert");
                $(display_element)
                    .toggleClass("green-alert", !data['past_dead_line']);
                $(display_element)
                    .children('icon')
                    .toggleClass("ok-icon", !data['past_dead_line']);
                $(display_element)
                    .children('span')
                    .text("Rating entered!");
                $('#'+div_id).find('.screen-reader-text').prop('title', "Rating entered!");  


                returnable = {
                    'sub_time': new Date(),
                    'past_dead_line': false,
                    'problem_pk': problem_pk,
                    'sub_pk': data['sub_pk'],
                }
            },
        "json")
     .fail(function(jqXHR, textStatus, errorThrown) { console.log(textStatus); });
}
