function get_problem_type_and_id(div_id) {
    return {type: div_id.split("-")[0], pk: div_id.split("-")[1]};
}

function update_marks(div_id, score, max_score){
    /**
     * Update the side bar and problem mark
     */

    var side_bar = $('.pcrs-sidenav').find('#sb_'+div_id);
    var new_title = $('#'+div_id).find(".widget_title")[0].firstChild.data.trim();

    var problem = get_problem_type_and_id(div_id);

    if (score == max_score){
        $('#'+div_id).find(".widget_mark").empty();
        $('#'+div_id).find(".widget_mark").append($('<i/>', {class:"green-checkmark-icon"}));
        side_bar.removeClass();
        side_bar.addClass("problem-complete");
        new_title += " : Complete";

    }
    else{
        $('#'+div_id).find(".widget_mark").find('sup').text(score);
        $('#'+div_id).find(".widget_mark").find('sub').text(max_score);
        new_title += " : " + score + " / " + max_score;
        side_bar.removeClass("problem-not-attempted")
        side_bar.addClass("problem-attempted");
    }

    window.dispatchEvent(
        new CustomEvent('statusUpdate',
            {
                detail: {
                    id: problem.type + "-" + problem.pk,
                    problem: {problem_type: problem.type, pk: problem.pk},
                    status: { attempted: true, completed: score==max_score },
                    score: score
                 }
            })
    );

// Socket updates. Turned off for now.
            // send message that this user attempted the problem
//         socket.emit('statusUpdate',
//            {id: problem.type + "-" + problem.pk,
//             problem: {problem_type: problem.type, pk: problem.pk},
//             status:{ attempted: true, completed: score==max_score },
//             score: score,
//             userhash: userhash
//            });

    side_bar.prop('title', new_title);
}