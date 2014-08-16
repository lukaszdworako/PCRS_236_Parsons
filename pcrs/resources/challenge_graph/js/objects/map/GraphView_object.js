/**
 *
 * @param id
 * @constructor
 */
function GraphView(id) {
    this.id = id;
    this.obj = $('#' + id);
}


/**
 * Resets this GraphView's height, width, x position and y position.
 */
GraphView.prototype.reset = function() {
    "use strict";

    $('#scroll-background-top').css('height', 0);// scrollBackgroundHeight / 2 *
    //zoom / 100);
    $('#scroll-background-bottom').css('height', scrollBackgroundHeight *
        zoom / 100);
    this.resetHeight();
    this.resetWidth();

    this.resetXPosition();
    this.resetYPostition();
};


/**
 * Resets this GraphView's width.
 */
GraphView.prototype.resetWidth = function () {
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
};


/**
 * Resets this GraphView's height.
 */
GraphView.prototype.resetHeight = function () {
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
};


/**
 * Resets the GraphView's y (top attribute) position.
 */
GraphView.prototype.resetYPostition = function () {
    "use strict";
    var graphViewObject = $('#graph-view');
    var scrollContentObject = $('#scroll-content');
    graphViewObject.css("top", ($('#nav-graph').height() *
        scrollContentObject.scrollTop()) / 100 -
        (graphViewObject.height() * scrollContentObject.scrollTop()) / 100);
};


/**
 * Resets this GraphViews's x (left attribute) position.
 */
GraphView.prototype.resetXPosition = function () {
    "use strict";
    var graphViewObject = $('#graph-view');
    var scrollContentObject = $('#scroll-content');
    graphViewObject.css("left", ($('#nav-graph').width() *
        scrollContentObject.scrollLeft()) / 10 -
        (graphViewObject.width() * scrollContentObject.scrollLeft()) / 100);
};


/**
 *
 */
GraphView.prototype.setSizes = function () {
    "use strict";
    var scrollContentObject = $('#scroll-content');
    $('#graph-view').css('width', scrollContentObject.width() * 0.1)
        .css('height', scrollContentObject.height() * 0.1);
};


/**
 *
 */
GraphView.prototype.setDrag = function () {
    setMapDragNavigation();
};


/**
 *
 */
GraphView.prototype.setClick = function () {
    setMapClickNavigation();
};
