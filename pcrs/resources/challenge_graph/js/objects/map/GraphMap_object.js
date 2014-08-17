/*global $ */

/**
 * Creates a GraphMap object that allows the user to view an overview of
 * the main graph.
 * @param id The id of the HTML map element.
 * @constructor
 */
function GraphMap(id) {
    'use strict';

    this.name = id;
}


/**
 * Sets up the svg graph map, including setting up map dragging, map clicking,
 * and size setting / resizing.
 */
GraphMap.prototype.initialize = function () {
    'use strict';

    var mapObject = $('#map');

    // TODO: Move all ID setting into processGraph().
    mapObject.find('svg').attr('id', 'nav-graph').attr('height', svgHeight *
        0.1).attr('width', svgWidth * 0.1);
    mapObject.find('.node').attr('data-active', 'display');
    mapObject.find('path').attr('data-active', 'inactive');
    mapObject.append('<div id="graph-view"></div>');

    this.setSize();
    window['graph-view'].setSizes();
    window['graph-view'].setDrag();
    window['graph-view'].setClick();
    window['nav-graph'].setupIDs();
    addScrollBackgroundHeight();
    window['nav-graph'].removeArrowHeads();
    window['nav-graph'].removeText();
};


/**
 * Sets this Map's size.
 */
GraphMap.prototype.setSize = function () {
    "use strict";
    var mapObject = $('#map');

    mapObject.css('height', Math.max($('#scroll-content').height(),
        $('#graph').height()) * 0.1)
             .css('width', svgWidth * 0.1);

    $('#button-container').attr('left', mapObject.width() + mapObject
                          .attr('left'));
};

