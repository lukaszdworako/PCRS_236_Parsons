/*global $ */


/**
 * A Graph object. This represents the main SVG graph.
 *
 * @class Graph
 * @param id
 * @param orientation
 * @constructor
 */
function Graph(id, orientation) {
    'use strict';

    this.name = id;
    this.orientation = orientation;
    this.horizontalGraph = null;
    this.verticalGraph = null;
    $('svg:first').attr('id', id);
}


Graph.prototype.setup = function () {
    'use strict';

    // Cleans up the svg. TODO: Put into Beautiful Soup as a pre-processor.
    processGraph();
    setScrollableContent("x");
    window['graph'].vitalize();

    // Adds each node's inner rects.
    addNodeDecorations();
    window['graph'].initializeUserData();
};


/**
 * Builds the interactive prerequisite graph structure.
 */
Graph.prototype.vitalize = function () {
    "use strict";

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
};


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
 * Builds the interactive graph.
 */
Graph.prototype.build = function () {
    "use strict";
    var graphObject = $('#graph');
    graphObject.find('.node').each(function () {
        makeNode($(this).attr('id'));
    });

    graphObject.find('path').each(function () {
        var coordinates = $(this).attr('d').split(/[\s,HVL]/);
        var xStart = parseFloat(coordinates[0].substr(1));
        var yStart = parseFloat(coordinates[1]);
        var yEnd = parseFloat(coordinates.pop());
        var xEnd = parseFloat(coordinates.pop());
        var startNode = '';
        var endNode = '';
        // createDiv(xStart, yStart, 10, 10, 'red');
        // createDiv(xEnd, yEnd, 10, 10, 'red');

        $('#graph').find('.node').each(function () {

            var r = $(this).children('rect');
            var xRect = parseFloat(r.attr('x'));
            var yRect = parseFloat(r.attr('y'));
            var width = parseFloat(r.attr('width'));
            var height = parseFloat(r.attr('height'));
            // createDiv(xRect, yRect, width, height, 'red');
            if (intersects(xStart,
                yStart,
                xRect,
                yRect,
                width,
                height,
                20)) {
                startNode = $(this).attr('id');
            }

            if (intersects(xEnd,
                yEnd,
                xRect,
                yRect,
                width,
                height,
                20)) {
                endNode = $(this).attr('id');
            }

            if (startNode !== '' && endNode !== '') {
                return false;
            }
        });

        makeEdge(window[startNode], window[endNode], $(this).attr('id'));
    });
};


/**
 * Initializes this Graph's settings.
 */
Graph.prototype.initializeSettings = function () {
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
};


/**
 * Initializes user data so that the nodes of the graph represent the
 * completed challenges.
 */
Graph.prototype.initializeUserData = function () {
    "use strict";
    var userData = getJSON();
    $.each(userData, function (i, val) {
        if (val[0] === val[1]) {
            window["node-" + i].turn();
        }
    });
};

Graph.prototype.changeOrientation = function () {
    'use strict';

    var graphObject = $("#graph");
    var scrollObject = $("#scroll-content");
    var navGraphObject = $("#nav-graph");

    var transitionDuration = 5000;
    var animationDuration = 2000;
    var ease = 'elastic';

    this.orientation = switchOrientation();
    var newGraph = getGraph(this.orientation);
    resetScrollPosition();
    resetZoom();
    setViewBoxOfGraphs(newGraph);
    $("#map").width(parseFloat($(newGraph).attr("width")) * 0.1);
    updateAbsoluteSizes(newGraph);
    animateGraphEdges(newGraph, ease, transitionDuration);

    graphObject.attr("width", $(newGraph).attr("width"))
        .attr("height", $(newGraph).attr("height"));

    navGraphObject
        .attr("width", parseFloat($(newGraph).attr("width")) * 0.1)
        .attr("height", parseFloat($(newGraph).attr("height")) * 0.1);

    navGraphObject
        .find("#graph0")
        .attr("transform", $(newGraph).find("#graph0").attr("transform"));

    d3.select("#graph0")
        .transition()
        .duration(transitionDuration)
        .attr("transform", $(newGraph).find("#graph0").attr("transform"));


    setNewGraphCoordinates(newGraph, ease, transitionDuration);
    animateNavGraphNodes(newGraph, ease, transitionDuration);

    removeScrollbar();

    if (this.orientation === "vertical") {
        scrollObject.css("display", "inline")
            .animate({width: "80%"}, animationDuration);

        $('#button-container').css('float', 'left').css('left', 15);
        d3.select("#scroll-content").style("float", "right");

        $("#HUD").animate({width: "15%"}, animationDuration)
            .animate({height: "100%"}, animationDuration);

        // Set the mousewheel to scroll vertically
        setScrollableContent("y");

    } else {
        scrollObject.css("display", "block")
            .animate({width: "100%"}, animationDuration);
        $('#button-container').css('float', 'right').css('left', 0);

        d3.select("#scroll-content")
            .transition()
            .duration(animationDuration)
            .style("float", "");

        $("#HUD")
            .animate({height: "15%"}, animationDuration)
            .animate({width: "100%"}, animationDuration);

        // Set the mousewheel to scroll horizontally
        setScrollableContent("x");
    }

    setTimeout(function () { window['graph-view'].reset(); }, transitionDuration);
    window['map'].setSize();
};