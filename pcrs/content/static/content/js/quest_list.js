var $save_button;

$(document).ready(function () {

    // force the affixed element to keep the same width on scroll
    // update width on window resize
    affixWidth();
    $(window).resize(affixWidth);

    $save_button = $('#save');
    $save_button.click(saveQuests);

    // enable moving quests up and down the list,
    // bind to existing buttons and those created later
    $(document).on('click', '.up-button', moveUp);
    $(document).on('click', '.down-button', moveDown);


    // make challenges on the all challenges list draggable
    // allow to drag and drop challenges to quests
    $("#challenges").sortable({
        connectWith: ".quest-box"
    });

    $(".quest-box").sortable({
        connectWith: ".quest-box",
        receive: function (event, ui) {
            // list has changed - provide visual clue that some changes are not saved
            $save_button.removeClass('disabled');
            $(event.target).find(".challenge").each(function () {
                if ($(this).find(".close").length == 0)
                    $(this).prepend(
                        $('<icon/>',
                            { class: "close glyphicon glyphicon-remove pull-right"}));
            });
        },
        update: function (event, ui) {
            $save_button.removeClass('disabled');
        }
    });

    $(document).on('click', '.close', function () {
        $challenge = $(event.target).parents('.challenge');
        $challenge.find('.close').remove();
        $('#challenges').append($challenge);
        // list has changed - provide visual clue that some changes are not saved
        $save_button.removeClass('disabled');
    });

});


function moveUp() {
    // move quest container up in the list of quests
    var $move_up = $(this).parents('.quest');
    $move_up.insertBefore($move_up.prev('.quest'));
    $save_button.removeClass('disabled');
}

function moveDown() {
    // move quest container down in the list of quests
    var $move_down = $(this).parents('.quest');
    $move_down.insertAfter($move_down.next('.quest'));
    $save_button.removeClass('disabled');
}


function encodeData() {
    // encode the information from quest lists:
    // for every quest, record its order(from 0 to n), and the challenges in it
    var all = {};
    var count = 0;
    $('.quest').each(function () {
        var quest_id = $(this).attr('id');
        all[quest_id] = {
            'challenge_ids': $(this).find('.quest-box').sortable('toArray'),
            'order': count
        };
        count = count + 1;
    });
    return all;
}

function saveQuests() {
    // save the order of quests and quest to challenge association
    $.post(document.URL + '/save_challenges', {
        quests: JSON.stringify(encodeData()),
        csrftoken: csrftoken
    })
        .success(function () {
            $save_button.addClass('disabled');
        })
}


function affixWidth() {
    $('.affix-element').each(function () {
        var elem = $(this);
        var parentPanel = elem.parents('.affix-parent');
        var width = $(parentPanel).width() - parseInt(elem.css('paddingLeft')) - parseInt(elem.css('paddingRight')) - parseInt(elem.css('marginLeft')) - parseInt(elem.css('marginRight')) - parseInt(elem.css('borderLeftWidth')) - parseInt(elem.css('borderRightWidth'));
        elem.css('width', width);
    });
}
