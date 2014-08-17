/*global $ */

var nodes = [];
var zoom = 100;
var svgWidth, svgHeight;
var graphViewWidth, graphViewHeight;
var scrollBackgroundHeight;
var orientation;
var horizontalGraph = null;
var verticalGraph = null;


$(document).ready(function () {
    "use strict";

    // Appends the graph to both the #scroll-content div and the map div.
    appendGraph("horizontal");
    window['graph'].setup();
    setInterval(pulseTakeable, 1000);

    // Sets the click function of the zoom in and zoom out buttons.
    setZoomInButtonFunctions();
});