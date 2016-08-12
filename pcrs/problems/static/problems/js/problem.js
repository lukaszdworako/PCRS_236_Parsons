$(document).ready(function() {
    var all_wrappers = $('.code-mirror-wrapper');

    for (var x = 0; x < all_wrappers.length; x++) {
        var wrapperDivId = all_wrappers[x].id;
        var wrapper = SubmissionWrapper.createWrapperFromDivId(wrapperDivId);
        wrapper.pageLoad();
    }

    $(window).bind("load", function() {
        $('.CodeMirror').each(function(i, el){
            el.CodeMirror.refresh();
        });
    });
});

