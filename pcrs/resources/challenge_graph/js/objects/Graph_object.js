/**
 *
 * @param id
 * @constructor
 */
function Graph (id) {
    this.name = id;
}


/**
 * Re-sizes this Graph.
 */
Graph.prototype.resetSize = function () {
    "use strict";
    $('#graph').attr('height', svgHeight * zoom / 100)
        .attr('width', svgWidth * zoom / 100);
    $('#mCSB_1_container').css('width', svgWidth * zoom / 100);
};

/**
 * Re-sizes the main graph.
 */
function resetGraphSize() {
}