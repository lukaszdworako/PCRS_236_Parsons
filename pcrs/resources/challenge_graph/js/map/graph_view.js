/**
 * Resets the graph-view's width.
 */
function resetGraphViewWidth() {
    "use strict";
    var graphViewObject = $('#graph-view');
    var scrollContentObject = $("#scroll-content");

    if ((scrollContentObject.width() * 0.1 * 100 / zoom) < parseFloat(
        $('#nav-graph').css('width')
    )) {
        graphViewObject.css("width", scrollContentObject.width() * 0.1 * 100 /
            zoom);
    } else {
        graphViewObject.css("width", $('#map').css('width'));
    }
}


/**
 * Resets the graph-view's height.
 */
function resetGraphViewHeight() {
    "use strict";
    var graphViewObject = $('#graph-view');
    var mapObject = $('#map');
    var scrollContainerObject = $('.mCSB_container_wrapper');

    if (scrollContainerObject.height() * 0.1 * 100 / zoom <
        parseFloat(mapObject.css('height'))) {
        graphViewObject.animate({height: scrollContainerObject.height() *
            0.1 * 100 / zoom});
    } else {
        graphViewObject.animate({height: mapObject.css('height')});
    }
}


/**
 * Resets the graph-view's y (top attribute) position.
 */
function resetGraphViewYPosition() {
    "use strict";
    var graphViewObject = $('#graph-view');
    var scrollContentObject = $('#scroll-content');
    graphViewObject.css("top", ($('#nav-graph').height() *
        scrollContentObject.scrollTop()) / 100 -
        (graphViewObject.height() * scrollContentObject.scrollTop()) / 100);
}


/**
 * Resets the graph-view's x (left attribute) position.
 */
function resetGraphViewXPosition() {
    "use strict";
    var graphViewObject = $('#graph-view');
    var scrollContentObject = $('#scroll-content');
    graphViewObject.css("left", ($('#nav-graph').width() *
        scrollContentObject.scrollLeft()) / 10 -
        (graphViewObject.width() * scrollContentObject.scrollLeft()) / 100);
}

/**
 * Re-sizes the map and the graph-view.
 */
function resetGraphView() {
    "use strict";

    $('#scroll-background-top').css('height', 0);// scrollBackgroundHeight / 2 *
    //zoom / 100);
    $('#scroll-background-bottom').css('height', scrollBackgroundHeight *
        zoom / 100);
    resetGraphViewHeight();
    resetGraphViewWidth();

    resetGraphViewXPosition();
    resetGraphViewYPosition();
}

function setGraphViewSizes() {
    "use strict";
    var scrollContentObject = $('#scroll-content');
    $('#graph-view').css('width', scrollContentObject.width() * 0.1)
        .css('height', scrollContentObject.height() * 0.1);
}