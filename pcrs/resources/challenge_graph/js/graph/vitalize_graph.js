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
    resetGraphView();
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
