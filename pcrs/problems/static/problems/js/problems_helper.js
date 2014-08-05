function update_marks(div_id, score, max_score){
    /**
     * Update the side bar and problem mark
     */

    var side_bar = $('.nav.bs-docs-sidenav').find('#sb_'+div_id);
    var new_title = $('#'+div_id).find(".widget_title")[0].firstChild.data.trim();
    if (score == max_score){
        $('#'+div_id).find(".widget_mark").empty();
        $('#'+div_id).find(".widget_mark").append($('<i/>', {class:"glyphicon glyphicon-ok ok-icon-green"}));
        side_bar.removeClass();
        side_bar.addClass("glyphicon glyphicon-check problem-complete");
        new_title += " : Complete"
    }
    else{
        $('#'+div_id).find(".widget_mark").find('sup').text(score);
        $('#'+div_id).find(".widget_mark").find('sub').text(max_score);
        new_title += " : " + score + " / " + max_score;
        side_bar.removeClass("problem-idle")
        side_bar.addClass("problem-attempted");
    }
    side_bar.prop('title', new_title);
}