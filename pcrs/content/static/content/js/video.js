function video_watched(video_id) {
    if (!$("#sb_video-" + video_id).hasClass('video-watched')) {
        $.post(root + "/content/videos/" + video_id + "/watched",
            {csrftoken: csrftoken})
            .success(function (data) {
                $(document).find("#sb_video-" + video_id).addClass("video-watched");

                window.dispatchEvent(
                    new CustomEvent('statusUpdate', {
                        detail: {id: "video-" + video_id,
                            status: {completed: true}
                        }
                    })
                );
            });
    }
}