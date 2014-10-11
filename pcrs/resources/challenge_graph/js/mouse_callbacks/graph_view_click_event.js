/*global $ */


/**
 * Sets the map's click navigation functionality (Users can point and click
 * to go where the want in the graph).
 */
function setMapClickNavigation() {
    'use strict';

    var graphView = $('#graph-view');
    var navGraph = $('#nav-graph');
    var map = $('#map');
    var graph = $('#graph');
    var scrollContent = $('#scroll-content');

    map.click(function (e) {
        var xCenter, yCenter;
        var offset = $(this).offset();
        var x = e.clientX - offset.left;
        var y = e.clientY - offset.top;

        // Checks if the newly calculated x position would be within the map
        // and if not, it sets it to the greatest possible value.
        if (x + parseFloat(graphView.width()) / 2 <
                parseFloat(navGraph.width())) {

            if ((x - parseFloat(graphView.width()) / 2) > 0) {
                xCenter = x - parseFloat(graphView.width()) / 2;
            } else {
                xCenter = 0;
            }

        } else {
            xCenter = parseFloat(parseFloat(navGraph.width())) -
                parseFloat(graphView.width());
        }

        // Checks if the newly calculated y position would be within the map
        // and if not, it sets it to the greatest possible value.
        if (y + parseFloat(graphView.height()) / 2 <
                parseFloat(map.height())) {

            if ((y - parseFloat(graphView.height()) / 2) > 0) {
                yCenter = y - parseFloat(graphView.height()) / 2;
            } else {
                yCenter = 0;
            }

        } else {
            yCenter = parseFloat(parseFloat(map.height())) -
                parseFloat(graphView.height());
        }

        graphView.animate({left: xCenter});
        graphView.css({top: yCenter});

        // Sets the location to scroll to.
        var axisArray = [(yCenter /
            parseFloat(navGraph.height()) *
            parseFloat(graph.height())), (xCenter /
            parseFloat(navGraph.css('width')) *
            parseFloat(graph.css('width')))];

        scrollContent.mCustomScrollbar('scrollTo', axisArray, {
            callbacks: false,
            scrollInertia: 250
        });
    });
}