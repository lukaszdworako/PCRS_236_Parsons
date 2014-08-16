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
    mapObject.find('svg')
             .attr('id', 'nav-graph')
             .attr('height', svgHeight * 0.1)
             .attr('width', svgWidth * 0.1);
    mapObject.find('.node').attr('data-active', 'display');
    mapObject.find('path').attr('data-active', 'inactive');
    mapObject.append('<div id="graph-view"></div>');
    setMapSize();
    window['graph-view'].setSizes();
    modifyNavGraphIDs();
    setMapDragNavigation();
    addScrollBackgroundHeight();
    removeArrowHeadsFromMap();
    setMapClickNavigation();
    removeTextFromMap();
}

function removeTextFromMap() {
    "use strict";
    $('#nav-graph').find('text').remove();
}


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
    $('#button-container').attr('left', $('#map').width() + $('#map').attr('left'));
}