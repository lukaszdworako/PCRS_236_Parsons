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
    'use strict';

    // Appends the graph to both the #scroll-content div and the map div.
    appendGraph('horizontal');

    // Graph object is created in appendGraph.
    window['graph'].setup();
    setInterval(pulseTakeable, 1000);
    setZoomInButtonFunctions();
});