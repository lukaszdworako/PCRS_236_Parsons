/**
 * Sets the button click events for zoom and scrolling.
 */
function setZoomInButtonFunctions() {
    $("#zoomIn").click(function () {
        zoomIn();
        $('#scroll-content').mCustomScrollbar('update');
    });
    $("#zoomOut").click(function () {
        zoomIn();
        $('#scroll-content').mCustomScrollbar('update');
    });
}


/**
 * Zooms the main graph out (changes the height and width) and makes the
 * graph-view appear to zoom out (get bigger).
 */
function zoomOut() {
    "use strict";
    if (zoom > 10) {
        zoom = zoom - 10;
    }
    resetGraphSize();
    resetGraphView();
}


/**
 * Zooms the main graph in (changes the height and width) and makes the
 * graph-view appear to zoom in (get smaller).
 */
function zoomIn() {
    "use strict";
    if (zoom < 200) {
        zoom = zoom + 10;
    }
    resetGraphSize();
    resetGraphView();
}