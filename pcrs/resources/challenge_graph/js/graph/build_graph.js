/**
 * Builds the interactive graph based on intersections between paths and
 * rects (with a large offset).
 */
function buildGraph() {
    "use strict";
    var graphObject = $('#graph');
    graphObject.find('.node').each(function () {
        makeNode($(this).attr('id'));
    });

    graphObject.find('path').each(function () {
        var coordinates = $(this).attr('d').split(/[\s,HVL]/);
        var xStart = parseFloat(coordinates[0].substr(1));
        var yStart = parseFloat(coordinates[1]);
        var yEnd = parseFloat(coordinates.pop());
        var xEnd = parseFloat(coordinates.pop());
        var startNode = '';
        var endNode = '';
        // createDiv(xStart, yStart, 10, 10, 'red');
        // createDiv(xEnd, yEnd, 10, 10, 'red');

        $('#graph').find('.node').each(function () {

            var r = $(this).children('rect');
            var xRect = parseFloat(r.attr('x'));
            var yRect = parseFloat(r.attr('y'));
            var width = parseFloat(r.attr('width'));
            var height = parseFloat(r.attr('height'));
            // createDiv(xRect, yRect, width, height, 'red');
            if (intersects(xStart,
                           yStart,
                           xRect,
                           yRect,
                           width,
                           height,
                           20)) {
                startNode = $(this).attr('id');
            }

            if (intersects(xEnd,
                           yEnd,
                           xRect,
                           yRect,
                           width,
                           height,
                           20)) {
                endNode = $(this).attr('id');
            }

            if (startNode !== '' && endNode !== '') {
                return false;
            }
        });

        makeEdge(window[startNode], window[endNode], $(this).attr('id'));
    });
}