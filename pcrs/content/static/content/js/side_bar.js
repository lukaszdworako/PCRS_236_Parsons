$(document).ready(function () {

    var widgets = $(".bs-docs-sidebar").siblings('div');
    var side_bar = $(".nav.bs-docs-sidenav");

    // fill up the side bar with information
    for (var w_ind = widgets.length - 1; w_ind > -1; w_ind--){

        var entry = $('<div/>',{style:"margin-left:25%;"});
        var entry2 = $('<a/>',{href:"#"+widgets[w_ind].id});

        var w_icon = "glyphicon glyphicon-edit";
        var title_text = $(widgets[w_ind]).find(".widget_title")[0].firstChild.data.trim();
        var w_color = "DarkOrange";

        // if there is a checkmark on the page the question is complete
        if ($(widgets[w_ind]).find(".widget_complete").length != 0){
            w_icon = "glyphicon glyphicon-check";
            w_color = "green";
            title_text += " : Complete";
        }
        //grab the score from the question on the page
        else if ($(widgets[w_ind]).find(".widget_down").length != 0){
            w_icon = "glyphicon glyphicon-unchecked";
            title_text += " : Down for maintenance";
            w_color = "grey";
        }
        else{
            var current_mark = $(widgets[w_ind]).find("sup").text();
            var max_mark =  $(widgets[w_ind]).find("sub").text();
            if (current_mark != " - "){
                title_text += " : " + current_mark + "/" + max_mark;
            }
            else{
                title_text += " : not attempted";
                w_color = "red";
            }
        }

        if ((widgets[w_ind].id).split("-")[0] == "video"){
            w_icon = "glyphicon glyphicon-film";
            w_color = "black";
            title_text = $(widgets[w_ind]).find("h3")[0].firstChild.data.trim();
        }

        var entry3 = $('<span/>',{
            id:"sb_"+widgets[w_ind].id,
            class:w_icon,
            style:"color:"+w_color+";",
            title:title_text
        });

        entry2.append(entry3);
        entry.append(entry2);
        side_bar.prepend(entry);
    }

    $(document).on("scroll", onScroll);

    //Smooth scrolling for the screen
    $('.nav.bs-docs-sidenav a[href^="#"]').on('click', function (e) {
        e.preventDefault();
        $(document).off("scroll");

        $('a').each(function () {
            $(this).removeClass('active_sb');
        })
        $(this).addClass('active_sb');

        var target = this.hash;
        $target = $(target);
        $('html, body').stop().animate({
            'scrollTop': $target.offset().top+2
        }, 500, 'swing', function () {
            window.location.hash = target;
            $(document).on("scroll", onScroll);
        });
    });
});

//scroll event to keep track of current problem
function onScroll(){
    var scrollPos = $(document).scrollTop();
    $('.nav.bs-docs-sidenav a').each(function () {
        var currLink = $(this);
        var refElement = $(currLink.attr("href"));
        if (refElement.position().top <= scrollPos && refElement.position().top + refElement.height() > scrollPos) {
            $('.nav.bs-docs-sidenav div a').removeClass("active_sb");
            currLink.addClass("active_sb");
        }
        else{
            currLink.removeClass("active_sb");
        }
    });
}

function video_watched(video_id){
    $(document).find("#sb_video-"+video_id).css("color","green");
}