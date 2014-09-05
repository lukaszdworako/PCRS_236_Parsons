$(document).ready(function () {

    var widgets = $(".pcrs-sidebar").siblings('div');
    var side_bar = $(".pcrs-sidenav");
//    var side_bar = widgets;

    if (widgets.length == 0){
        $(".pcrs-sidebar").remove();
    }
    else{
        // fill up the side bar with information
        for (var w_ind = widgets.length - 1; w_ind > -1; w_ind--){

            var entry = $('<div/>',{class:"side-bar-el"});
            var entry2 = $('<a/>',{href:"#"+widgets[w_ind].id});

            var w_icon = "problem-not-attempted";
            var title_text = $(widgets[w_ind]).find(".widget_title")[0].innerHTML.trim();
    //        var w_color = " problem-attempted";
            var w_color = "";

            // if there is a checkmark on the page the question is complete
            if ($(widgets[w_ind]).find(".widget_complete").length != 0){
                w_icon = "problem-complete";
                w_color = "";
                title_text += " : Complete";
            }
            //grab the score from the question on the page
            else if ($(widgets[w_ind]).find(".widget_down").length != 0){
                w_icon = "problem-closed";
                title_text += " : Down for maintenance";
                w_color = "";
            }
            else{
                var current_mark = $(widgets[w_ind]).find("sup").text();
                var max_mark =  $(widgets[w_ind]).find("sub").text();
                if (current_mark != " - "){
                    title_text += " : " + current_mark + "/" + max_mark;
                    w_icon = "problem-attempted";
                }
                else{
                    title_text += " : not attempted";
                    w_color = "";
                }
            }

            if ((widgets[w_ind].id).split("-")[0] == "video"){
                w_icon = "video-not-watched";
                w_color = "";
                if ($(widgets[w_ind]).find('.green-checkmark-icon').length > 0){
                    w_icon = "video-watched";
                    w_color = "";
                }
                title_text = $(widgets[w_ind]).find("h3")[0].firstChild.data.trim();
            }

            var entry3 = $('<span/>',{
                id:"sb_"+widgets[w_ind].id,
                class:w_icon + w_color
            });

            entry2.append(entry3);
            entry2.attr('title',title_text);
            entry.append(entry2);
            side_bar.prepend(entry);
        }

        $(document).on("scroll", onScroll);

        //Smooth scrolling for the screen
        $('.pcrs-sidenav a[href^="#"]').on('click', function (e) {
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
    }
});

//scroll event to keep track of current problem
function onScroll(){
    var scrollPos = $(document).scrollTop();
    $('.pcrs-sidenav .side-bar-el a').each(function () {
        var currLink = $(this);
        var refElement = $(currLink.attr("href"));
        if (refElement.position().top <= scrollPos && refElement.position().top + refElement.height() > scrollPos) {
            $('.pcrs-sidenav div a').removeClass("active_sb");
            currLink.addClass("active_sb");
        }
        else{
            currLink.removeClass("active_sb");
        }
    });
}

function video_watched(video_id){
    if (!$("#sb_video-"+video_id).hasClass('video-watched')){
        $.post(root+"/content/videos/"+video_id+"/watched",
            {csrftoken:csrftoken})
            .success(function (data) {
                $(document).find("#sb_video-"+video_id).addClass("video-watched");

                socket.emit('statusUpdate',
                    {
                        id: "video-" + video_id,
                        status: {completed: true},
                        userhash: userhash
                    });
            });
    }
}