/*global $*/
/*global zoom*/

/**
 * Sets up the svg graph map, including setting up map dragging, map clicking,
 * and size setting / resizing.
 */
function setupMap() {
    "use strict";
    var mapObject = $('#map');

    // TODO: Move all ID setting into processGraph().
    mapObject.find('svg').attr('id', 'nav-graph').attr('height', svgHeight *
        0.1).attr('width', svgWidth * 0.1);
    mapObject.find('.node').attr('data-active', 'display');
    mapObject.find('path').attr('data-active', 'inactive');
    mapObject.append('<div id="graph-view"></div>');
    setMapSize();

    setGraphViewSizes();

    modifyNavGraphIDs();
    setMapDragNavigation();
    addScrollBackgroundHeight();
    removeArrowHeadsFromMap();
    setMapClickNavigation();
    removeTextFromMap();
}

function setGraphViewSizes() {
    "use strict";
    var scrollContentObject = $('#scroll-content');
    $('#graph-view').css('width', scrollContentObject.width() * 0.1)
        .css('height', scrollContentObject.height() * 0.1);
}


function removeTextFromMap() {
    "use strict";
    $('#nav-graph').find('text').remove();
}

/**
 * Updates the nav-graphs nodes to reflect active nodes in the main graph.
 * @param node The selected node in the graph. This node is updated in the
 * nav-graph.
 */
function updateNavGraph(node) {
    "use strict";
    var newId = '#' + node.attr('id') + '-map-node';
    $(newId).attr('data-active', 'display-selected');
}


/**
 * Modifies the nav-graph ids. Since the main graph and the map graph are
 * the same graph, the ids need to be changed.
 */
function modifyNavGraphIDs() {
    "use strict";
    $('#nav-graph').find('.node').each(function () {
        $(this).attr('id', $(this).attr('id') + '-map-node');
    });
}


/**
 * Re-sizes the main graph.
 */
function resetGraphSize() {
    "use strict";
    $('#graph').attr('height', svgHeight * zoom / 100)
        .attr('width', svgWidth * zoom / 100);
    $('#mCSB_1_container').css('width', svgWidth * zoom / 100);
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
 * Removes the arrow heads from the map. (These are unnecessary polygons).
 */
function removeArrowHeadsFromMap() {
    "use strict";
    $('#nav-graph').find('polygon').remove();
}


/**
 * Sets the maps size.
 */
function setMapSize() {
    "use strict";
    $('#map').css('height', Math.max($('#scroll-content').height(),
                            $('#graph').height()) * 0.1)
             .css('width', svgWidth * 0.1);
}