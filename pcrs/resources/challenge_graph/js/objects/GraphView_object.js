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