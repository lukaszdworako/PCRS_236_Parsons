function dispatchVideoWatches(video_id) {
    window.dispatchEvent(
        new CustomEvent('statusUpdate', {
            detail: {id: "video-" + video_id,
                status: {completed: true}
            }
        })
    );
}

$(function () {
    $('a[id^="video-download"]').click(function (event) {
        var video_id = event.target.id.split('_')[1];
        dispatchVideoWatches(video_id);
    });
});


function video_watched(video_id) {
    $.post(root + "/content/videos/" + video_id + "/watched",
        {csrftoken: csrftoken})
        .success(function (data) {
            dispatchVideoWatches(video_id);
        });
}
