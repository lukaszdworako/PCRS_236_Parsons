/*global svgHeight, svgWidth*/

/**
 * Sets the custom scroll bar of the graph.
 * @param mousewheelAxis The axis that the mouse wheel acts on.
 */
function setScrollableContent(mousewheelAxis) {
    "use strict";
    $("#scroll-content").mCustomScrollbar({
        axis: "xy",
        theme: "dark",
        mouseWheel: { enable: true,
                     axis: mousewheelAxis,
                     scrollAmount: 500
                   },
        advanced: { updateOnContentResize: true },
        keyboard: { scrollAmount: 50 },
        callbacks: {

            // This allows for the graph-view to move while the main graph div is being scrolled.
            whileScrolling: function () {
                var graphViewObject = $("#graph-view");
                graphViewObject.css("left",
                    2 + fixVal(($("#nav-graph").width() * this.mcs.leftPct) / 100 -
                        (graphViewObject.width() * this.mcs.leftPct) / 100));

                graphViewObject.css("top",
                    fixVal(($("#map").height() * this.mcs.topPct) / 100 -
                        (graphViewObject.height() * this.mcs.topPct) / 100));
            }
        }
    });
}


/**
 * Subtracts 1 from val if val is odd. The purpose of this function within this context is to improve the
 * smoothness of the graph map.
 * @param {int} val The minuend.
 * @returns {*}
 */
function fixVal(val) {
    "use strict";
    if ((parseFloat(val) % 2) !== 0) {
        val = val - (val % 2);
    }
    return val;
}