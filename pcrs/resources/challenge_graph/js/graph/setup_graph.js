/*global $ */
var nodes = [];
var zoom = 100;
var svgWidth, svgHeight;
var graphViewWidth, graphViewHeight;
var scrollBackgroundHeight;


$(document).ready(function () {
    "use strict";
    appendGraph("horizontal"); // Appends the graph to both the #scroll-content div and the map div.
    setupGraph();
    setInterval(pulseTakeable, 1000);
    setChangeOrientationEvent();
    setZoomInButtonFunctions(); // Sets the click function of the zoom in and zoom out buttons.
});


/**
 *
 */
function setupGraph() {
    processGraph(); // Cleans up the svg. TODO: Put into Beautiful Soup as a pre-processor.
    setScrollableContent(); // Sets the custom scroll bars for the main graph.
    setMainGraphID(); // Sets the main graph id.
    vitalizeGraph(); // Builds the graph based on prerequisite structure.
    addNodeDecorations(); // Adds each node's inner rects.
    initializeUserData();
}