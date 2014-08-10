/**
 * When the window is re-sized, the map needs to be re-sized to reflect what
 * the user is currently viewing.
 * TODO: When the user has a browser zoomed in, the map will not resize
 * properly when the browser is re-sized.
 */
$(window).resize(function() {
    "use strict";
    resetGraphSize();
    resetMapGraph();
    setMapSize();
});


/**
 * Gets the absolute sizes of graph divs, meant for calculating zoom and
 * resizing later on.
 */
function getAbsoluteSizes() {
    "use strict";
    var svgObject = $('svg');
    var graphViewObject = $('#graph-view');
    svgWidth = svgObject.width();
    svgHeight = svgObject.height();
    graphViewWidth = graphViewObject.width();
    graphViewHeight = graphViewObject.height();
}

/**
 * Adds the scroll-background height. This is necessary for consistency with
 * the map when the main graph is zoomed.
 */
function addScrollBackgroundHeight() {
    "use strict";
    scrollBackgroundHeight = ($('#mCSB_1_container_wrapper').height() -
                              $('#graph').height());
    $('#scroll-background-top').css('height', scrollBackgroundHeight/2 *
                                              zoom/100);
    $('#scroll-background-bottom').css('height', scrollBackgroundHeight/2 *
                                                 zoom/100);
}