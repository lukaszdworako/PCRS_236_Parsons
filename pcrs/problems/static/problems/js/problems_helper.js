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
                    status: { attempted: true, completed: score>=max_score },
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

/**
 * Convert django "datetime" to PCRS style for history
 */
function jsDateTimeToPCRSDatetime(datetime) {
    var month_names = ["January","February","March","April","May","June","July",
                   "August","September","October","November","December"];

    var day = datetime.getDate();
    var month = month_names[datetime.getMonth()];
    var year = datetime.getFullYear();
    var hour = datetime.getHours();
    var minute = datetime.getMinutes();

    if (String(minute).length == 1){
        minute = "0" + minute
    }
    if (hour > 12){
        hour -= 12;
        cycle = "p.m.";
    } else {
        cycle = "a.m.";
    }

    var formated_datetime = month + " " + day + ", "+year + ", " + hour+":"+minute+" "+cycle
    return formated_datetime;
}

/**
 * Replaces a div with code inside with a TabbedCodeMirror
 *
 * @param $codeDiv The code div to replace.
 * @return The TabbedCodeMirror object.
 */
function setTabbedCodeMirrorFilesFromTagText(tcm, codeText) {
    while (tcm.getFileCount() > 0) {
        tcm.removeFileAtIndex(0);
    }

    var files = TagManager.parseCodeIntoFiles(codeText);

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var codeObj = TagManager.stripTagsForStudent(file.code);
        tcm.addFile({
            'name': file.name,
            'code': codeObj.code,
            'mode': 'text/x-java',
            'theme': user_theme,
            'block_ranges': codeObj.block_ranges,
            'hash_ranges': codeObj.hash_ranges,
        });
    }

    tcm.setActiveTabIndex(0);
}

