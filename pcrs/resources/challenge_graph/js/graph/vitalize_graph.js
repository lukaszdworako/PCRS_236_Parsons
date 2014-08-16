/**
 * Builds the interactive prerequisite graph structure.
 */
function vitalizeGraph() {
    "use strict";

    window['graph-view'] = new GraphView('graph-view');
    window['map'] = new GraphMap('map');
    window['nav-graph'] = new NavGraph('nav-graph');

    getAbsoluteSizes(); // Gets the absolute sizes for zoom/resizing
                        // functionality.
    window['map'].initialize();

    window['graph'].build();
    setMouseCallbacks();
    window['graph'].initializeSettings();

    $('text').attr('id', function (i) {return 'text-' + i; });
    window['graph-view'].reset();
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


