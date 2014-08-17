/*global $ */


/**
 * Sets the map drag functionality (Users can control the graph by dragging
 * the graph-view div).
 * TODO: Known issue: #graph-view is contained inside of the map, and can't
 * make it close to the edges of the graph.
 */
function setMapDragNavigation() {
    "use strict";
    var graphViewObject = $("#graph-view");
    var graphObject = $("#graph");
    var mapObject = $("#map");

    graphViewObject.draggable({containment: '#map'});
    graphViewObject.on('drag', function () {

        var axisArray = [
            (parseFloat($(this).css('top')) / parseFloat(mapObject.height()) *
                parseFloat(graphObject.height())),
            (parseFloat($(this).css('left')) / parseFloat(mapObject.width()) *
                parseFloat(graphObject.width()))
        ];

        $('#scroll-content').mCustomScrollbar('scrollTo', axisArray, {
            callbacks: false,
            scrollInertia: 250
        });
    });
}
