$(document).ready(function () {
    if ($(document).find('.searchable_content').length != 0){
        $('#searcher').keyup(find_item);
    }
    else{
        $('#searcher').hide();
    }
});


function find_item(){

    var searching_for = $('#searcher').val().toLowerCase()
    var problem_list = $('.item-list').children();
    for (var index = 0; index < problem_list.length; index ++){
        if (searching_for == ""){
            $(problem_list[index]).show();
        }
        else if ($(problem_list[index]).find('.searchable_content').text().toLowerCase().indexOf(searching_for) != -1){
            $(problem_list[index]).show();
        }
        else{
            $(problem_list[index]).hide();
        }
        var current_tags = $(problem_list[index]).find('.badge.tag');
        if (searching_for != ""){
            for (var tag_index = 0; tag_index < current_tags.length; tag_index++){
                if ($(current_tags[tag_index]).text().toLowerCase().indexOf(searching_for) != -1){
                    $(problem_list[index]).show();
                }
            }
        }
    }
}