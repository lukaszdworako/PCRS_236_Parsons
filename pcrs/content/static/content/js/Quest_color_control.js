$(document).ready(function () {
    var quest_list = $('[id*=quest_accordion_]');
    for (var quest_index = 0; quest_index < quest_list.length; quest_index++){
        if ($(quest_list[quest_index]).find('.panel-challenge-not-attempted').length==0
            &&
            $(quest_list[quest_index]).find('.panel-challenge-attempted').length==0
            &&
            $(quest_list[quest_index]).find('.panel-challenge-completed').length!=0
            ){

            $(quest_list[quest_index]).find('.panel-heading').addClass('panel-challenge-completed');
        }
    }
});