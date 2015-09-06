function get_problem_type_and_id(div_id) {
    return {type: div_id.split("-")[0], pk: div_id.split("-")[1]};
}

function update_marks(div_id, score, max_score){
    /**
     * Update the side bar and problem mark
     */

    var side_bar = $('.pcrs-sidenav').find('#sb_'+div_id);
    var new_title = 'Progress so far: '

    var problem = get_problem_type_and_id(div_id);

    if (score >= max_score){
        new_title += 'complete';

        var problem_score = $('#'+div_id).find('.incomplete_problem');
        problem_score.removeClass();
        problem_score.addClass("green-checkmark-icon");
        problem_score.prop('title', new_title);

        /* For nonreactive pages */
        var nonreactive_span = $('#'+div_id).find('.nonreactive_score');
        nonreactive_span.empty();

        side_bar.removeClass();
        side_bar.addClass("problem-complete");

    }
    else{
        new_title += score + ' of ' + max_score;

        var problem_score = $('#'+div_id).find('.incomplete_problem');
        problem_score.find('sup').text(score);
        problem_score.find('sub').text(max_score);
        problem_score.prop('title', new_title);

        side_bar.removeClass();
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
