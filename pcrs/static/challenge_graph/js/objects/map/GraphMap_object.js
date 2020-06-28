/*global $ */

/**
 * Creates a GraphMap object that allows the user to view an overview of
 * the main graph.
 *
 * @class GraphMap
 * @param id The id of the HTML map element.
 * @constructor
 */
function GraphMap(id) {
    'use strict';

    this.name = id;
    this.obj = $('#' + id);
}


/**
 * Sets up the svg graph map, including setting up map dragging, map clicking,
 * and size setting / resizing.
 */
GraphMap.prototype.initialize = function () {
    'use strict';

    this.obj.find('svg')
        .attr('id', 'nav-graph')
        .attr('height', svgHeight * 0.1)
        .attr('width', svgWidth * 0.1);
    this.obj.find('.node')
        .attr('data-active', 'display');
    this.obj.find('path')
        .attr('data-active', 'inactive');
    this.obj.append('<div id="graph-view"></div>');
    window['graph-view'] = new GraphView('graph-view');

    this.setSize();

    window['graph-view'].setSizes();
    window['graph-view'].setDrag();
    window['graph-view'].setClick();
    window['nav-graph'].setupIDs();
    window['nav-graph'].removeArrowHeads();
    window['nav-graph'].removeText();
    addScrollBackgroundHeight();
};


/**
 * Sets this Map's size.
 */
GraphMap.prototype.setSize = function () {
    'use strict';

    this.obj.css('height', Math.max($('#scroll-content').height(),
        $('#graph').height()) * 0.1)
        .css('width', svgWidth * 0.1);

    $('#button-container').attr('left', this.obj.width() + this.obj
        .attr('left'));
};

