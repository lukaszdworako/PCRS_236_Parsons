function get_problem_type_and_id(div_id) {
    return {type: div_id.split("-")[0], pk: div_id.split("-")[1]};
}

function update_marks(div_id, score, max_score){
    /**
     * Update the side bar and problem mark
     */

    var side_bar = $('.nav.bs-docs-sidenav').find('#sb_'+div_id);
    var new_title = $('#'+div_id).find(".widget_title")[0].firstChild.data.trim();

    problem = get_problem_type_and_id(div_id);

    if (score == max_score){
        $('#'+div_id).find(".widget_mark").empty();
        $('#'+div_id).find(".widget_mark").append($('<i/>', {class:"glyphicon glyphicon-ok ok-icon-green"}));
        side_bar.removeClass();
        side_bar.addClass("glyphicon glyphicon-check problem-complete");
        new_title += " : Complete"

        // send message that this user completed the problem

        socket.emit('user-problems',
            {problem: {problem_type: problem.type, pk: problem.pk},
             status:{ attempted: true, completed: true},
             userhash: userhash
            });
    }
    else{
        $('#'+div_id).find(".widget_mark").find('sup').text(score);
        $('#'+div_id).find(".widget_mark").find('sub').text(max_score);
        new_title += " : " + score + " / " + max_score;
        side_bar.removeClass("problem-idle")
        side_bar.addClass("problem-attempted");

        // send message that this user attempted the problem
         socket.emit('user-problems',
            {problem: {problem_type: problem.type, pk: problem.pk},
             status:{ attempted: true },
             userhash: userhash
            });
    }
    side_bar.prop('title', new_title);
}