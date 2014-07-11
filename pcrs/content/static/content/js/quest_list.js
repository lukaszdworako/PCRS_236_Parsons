var $save_button;
var selected_challenge;

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
                            { class: "close glyphicon glyphicon-remove pull-right",
                              title: "Remove this challenge form this quest"}));
            });
        },
        update: function (event, ui) {
            $save_button.removeClass('disabled');
            resize_challenge();
        }
    });

    $(document).on('click', '.close', function () {
        $challenge = $(this).parents('.challenge');
        $challenge.find('.close').remove();
        $('#challenges').append($challenge);
        // list has changed - provide visual clue that some changes are not saved
        $save_button.removeClass('disabled');
        resize_challenge();
    });

    resize_challenge();
});

function select_quest(challenge_pk){
    selected_challenge = challenge_pk;
    $("#quest_list").empty();
    var quest_list = $(document).find('.quest');
    $('#page_entry_ModalLabel').text('There are '+quest_list.length+' Quests. To which quests do you want to move the challenge?')
    for (var quest_index=0; quest_index < quest_list.length; quest_index++){
        var quest_pk = $(quest_list[quest_index]).attr('id');
        var quest_name = $(quest_list[quest_index]).find('.name').text().trim();
        $('#quest_list').append("<option value='"+quest_pk+"'>"+quest_name+"</option>");
    }
    $('#page-entry-modal').modal();
}

function move_challenge(){
    var quest_number = $('#quest_list').val().trim();
    var destination_location = $('#all-quests').find('.quest#'+quest_number).find('.quest-box');
    var moving_item = $(document).find('.challenge#'+selected_challenge);
    destination_location.append(moving_item.remove());
    $save_button.removeClass('disabled');
    resize_challenge();
}

function resize_challenge(){
    $('#challenges').height($('.set_challenges').height()-$('.challenge_title').height()*5);

}


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
