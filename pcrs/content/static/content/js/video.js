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

        // Can't just use video_watched because the download
        // that occurs due to the click may fail. (In particular,
        // it fails for mymedia because there is a redirect 302.)
        // This makes any asynchronous call fail.
        // video_watched(video_id, true);
        $.ajax({
          url : root + "/content/videos/" + video_id + "/watched",
          type: "POST",
          async: false,
          data: {csrftoken: csrftoken, download: true},
          success: function(data, textStatus, jqXHR) {
              dispatchVideoWatches(video_id);
          }
        });
    });
});


function video_watched(video_id, is_download = false) {
    $.post(root + "/content/videos/" + video_id + "/watched",
        {csrftoken: csrftoken, download: is_download})
        .done(function(data, status, jqXHR) {
            dispatchVideoWatches(video_id);
        });
}
