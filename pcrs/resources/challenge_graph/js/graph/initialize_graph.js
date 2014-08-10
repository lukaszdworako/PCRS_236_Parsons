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