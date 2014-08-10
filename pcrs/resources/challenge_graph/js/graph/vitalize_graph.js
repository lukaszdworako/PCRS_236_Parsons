/*global $ */
var nodes = [];
var zoom = 100;
var svgWidth, svgHeight;
var graphViewWidth, graphViewHeight;
var scrollBackgroundHeight;


/**
 * Initializes the graph settings.
 */
function initializeGraphSettings() {
    "use strict";
    var graphObject = $('#graph');
    graphObject.find('path').attr('data-active', 'inactive');
    graphObject.find('.node').attr('data-active', 'inactive');

    $.each(nodes, function (i, node) {
        window[node].updateStatus();
        window[node].updateSVG();
        $.each(window[node].outEdges, function (i, edge) {
            if (edge !== undefined) {
                edge.updateStatus();
            }
        });
    });
}


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


/**
 * Fades in/out the graphs doable nodes (opacity from 0.4 to 1,
 * or from 0.4 to 1).
 */
function pulseTakeable() {
    "use strict";
    $(nodes).each(function (i, node) {
        var nodeObject = '#' + node;
        if (window[node].status === 'doable') {
            if ($(nodeObject).css('opacity') > 0.9) {
                $(nodeObject).fadeTo('slow', 0.4);
            } else {
                $(nodeObject).fadeTo('slow', 1);
            }
        } else if (window[node].status === 'active') {
            $(nodeObject).fadeTo('fast', 1);
        }
    });
}


/**
 * Sets the mouse callbacks for the nodes.
 */
function setMouseCallbacks() {
    "use strict";
    var nodeObjects = $('#graph').find('.node');
    nodeObjects.click(function (event) {
        turnNode(event);
    })
        .mouseenter(function (event) {
            updateParentCount($(this).children('.counter-text'), true);
            hoverFocus(event);
        })
        .mouseleave(function (event) {
            updateParentCount($(this).children('.counter-text'), false);
            hoverUnfocus(event);
        });
}


/**
 * Builds the interactive prerequisite graph structure.
 */
function vitalizeGraph() {
    "use strict";
    getAbsoluteSizes(); // Gets the absolute sizes for zoom/resizing
                        // functionality.
    setupMap(); // Sets up all of the map functions, including map sizing,
                // dragging and clicking.
    buildGraph();
    setMouseCallbacks();
    initializeGraphSettings();

    $('text').attr('id', function (i) {return 'text-' + i; });
    setKeydown();
    resetMapGraph();
}


/**
 * Creates an svg rect and appends it to #graph0.
 * @param posX The x position of the rect.
 * @param posY The y position of the rect.
 * @param width The width of the rect.
 * @param height The height of the rect.
 * @param color The fill and stroke color of the rect.
 */
function createRect(posX, posY, width, height, color) {
    "use strict";
    $('#graph0').append($(document.createElementNS(
      'http://www.w3.org/2000/svg', 'rect')).attr({
      x: posX,
      y: posY,
      rx: 20,
      ry: 20,
      fill: color,
      stroke: color,
      width: width,
      height: height
    }));
}


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


/**
 * Creates a div.
 * @param posX The x position of the div ('left' attribute).
 * @param posY The y position of the div ('top' attribute).
 * @param width The width of the div.
 * @param height The height of the div.
 * @param color The background-color of the div.
*/
function createDiv(posX, posY, width, height, color) {
    "use strict";
    var div = $('<div></div>');
    div.css('position', 'absolute')
       .css('left', posX)
       .css('top', posY)
       .css('width', width)
       .css('height', height)
       .css('background-color', color);
    $('#graph').append(div);
}


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
 * Zooms the main graph out (changes the height and width) and makes the
 * graph-view appear to zoom out (get bigger).
 */
function zoomOut() {
    "use strict";
    if (zoom > 10) {
        zoom = zoom - 10;
    }
    resetGraphSize();
    resetMapGraph();
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
    resetMapGraph();
}


/**
 * Sets the keydown events for zoom and scrolling.
 */
function setKeydown() {
    "use strict";
    $(document).keydown(function(e){
        switch (e.keyCode) {
            case 187: // + Key
                zoomIn();
                break;
            case 189: // - Key
                zoomOut();
                break;
        }
        $('#scroll-content').mCustomScrollbar('update');
    });
}

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