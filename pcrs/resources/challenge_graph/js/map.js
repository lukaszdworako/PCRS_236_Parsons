/*global $*/
/*global zoom*/

/**
 * Sets up the svg graph map, including setting up map dragging, map clicking,
 * and size setting / resizing.
 */
function setupMap() {
    "use strict";
    var scrollContentObject = $('#scroll-content');

    resetMapSize();

    $('#graph-view').css('width', scrollContentObject.width() * 0.1)
        .css('height', scrollContentObject.height() * 0.1);

    modifyNavGraphIDs();
    setMapDragNavigation();
    addScrollBackgroundHeight();
    removeArrowHeadsFromMap();
    setMapClickNavigation();
}

function resetMapSize() {
    var mapObject = $('#map');

    setMapSize();

    mapObject.find('svg').attr('id', 'nav-graph').attr('height', svgHeight *
        0.1).attr('width', svgWidth * 0.1);
    mapObject.find('.node').attr('data-active', 'display');
    mapObject.find('path').attr('data-active', 'inactive');
    mapObject.append('<div id="graph-view"></div>');
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


/**
 * Sets the map's click navigation functionality (Users can point and click
 * to go where the want in the graph).
 */
function setMapClickNavigation() {
    "use strict";

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

        if (x + parseFloat(graphView.width()) / 2 < parseFloat(
            parseFloat(navGraph.width())
            )) {

            if ((x - parseFloat(graphView.width()) / 2) > 0) {
                xCenter = x - parseFloat(graphView.width()) / 2;
            } else {
                xCenter = 0;
            }

        } else {
            xCenter = parseFloat(parseFloat(navGraph.width())) -
                parseFloat(graphView.width());
        }

        if (y + parseFloat(graphView.height()) / 2 < parseFloat(
            parseFloat(map.height())
            )) {

            if ((y - parseFloat(graphView.height()) / 2) > 0) {
                yCenter = y - parseFloat(graphView.height()) / 2;
            } else {
                yCenter = 0;
            }

        } else {
            yCenter = parseFloat(parseFloat(map.height())) -
                parseFloat(graphView.height());
        }

        createRect(x, y, 10, 10, 'blue');
        graphView.animate({left: xCenter});
        graphView.css({top: yCenter});

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


/**
 * Re-sizes the main graph.
 */
function resetGraphSize() {
    "use strict";

    $('#graph').css('height', svgHeight * zoom / 100)
        .css('width', svgWidth * zoom / 100);
    $('#mCSB_1_container').css('width', svgWidth * zoom / 100);
}


/**
 * Re-sizes the map and the graph-view.
 */
function resetMapGraph() {
    "use strict";

    $('#scroll-background-top').css('height', 0);// scrollBackgroundHeight / 2 *
        //zoom / 100);
    $('#scroll-background-bottom').css('height', scrollBackgroundHeight *
        zoom / 100);
    
    resetGraphViewXPosition();
    resetGraphViewYPosition();
    resetGraphViewHeight();
    resetGraphViewWidth();
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
        graphViewObject.animate({width: scrollContentObject.width() * 0.1 * 100 /
            zoom});
    } else {
        graphViewObject.animate({width: $('#map').css('width')});
    }
}


/**
 * Resets the graph-view's height.
 */
function resetGraphViewHeight() {
    "use strict";
    var graphViewObject = $('#graph-view');
    var mapObject = $('#map');
    var scrollContainerObject = $('#mCSB_1_container_wrapper');

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