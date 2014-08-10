/*global $ */
/*global document */
/*global appendGraph */
/*global processGraph */
/*global setScrollableContent */
/*global setMainGraphID */
/*global addNodeDecorations */
/*global roundTo */
/*global appendCounterRect */
/*global window */
/*global getNonActiveParentNames */
/*global vitalizeGraph */
var orientation;

$(document).ready(function () {
    "use strict";
    appendGraph("horizontal"); // Appends the graph to both the #scroll-content div and the map div.
    setupGraph();
    setInterval(pulseTakeable, 1000);
    setChangeOrientationEvent();
    setZoomInButtonFunctions(); // Sets the click function of the zoom in and zoom out buttons.
});


function setupGraph() {
    processGraph(); // Cleans up the svg. TODO: Put into Beautiful Soup as a pre-processor.
    setScrollableContent(); // Sets the custom scroll bars for the main graph.
    setMainGraphID(); // Sets the main graph id.
    vitalizeGraph(); // Builds the graph based on prerequisite structure.
    addNodeDecorations(); // Adds each node's inner rects.
    initializeUserData();
}


/**
 * Sets the custom scroll bar of the graph.
 */
function setScrollableContent() {
    "use strict";
    $("#scroll-content").mCustomScrollbar({
        axis: "xy",
        theme: "dark",
        mouseWheel: { enable: true,
                     axis: "x",
                     scrollAmount: 500
                   },
        advanced: { updateOnContentResize: true },
        keyboard: { scrollAmount: 50 },
        callbacks: {

            // This allows for the graph-view to move while the main graph div is being scrolled.
            whileScrolling: function () {
                var graphViewObject = $("#graph-view");
                graphViewObject.css("left",
                    2 + roundTo(($("#nav-graph").width() * this.mcs.leftPct) / 100 -
                        (graphViewObject.width() * this.mcs.leftPct) / 100));

                graphViewObject.css("top",
                    roundTo(($("#map").height() * this.mcs.topPct) / 100 -
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
function roundTo(val) {
    "use strict";
    // TODO: Take out parseFloat.
    // TODO: Change name, it's not really rounding!
    if ((parseFloat(val) % 2) !== 0) {
        val = val - (val % 2);
    }
    return val;
}


/**
 * Adds additional attributes to the svg output.
 */
function processGraph() {
    "use strict";
    $("polygon[fill*=white]").attr("fill", "none");

    $("path").css("fill", "none")
           .attr("id", function (i) { return "p" + i; });
}

/**
 * Sets the #change-orientation button click event.
 */
function setChangeOrientationEvent() {
    $("#change-orientation").click(function () {
        zoom = 100;
        orientation = orientation === "horizontal" ? "vertical" : "horizontal";
        var graph = getGraph(orientation);
        var index  = graph.indexOf("viewbox");
        var substr = graph.substring(index + 9);
        index = substr.indexOf("\"");
        var viewBox = substr.substring(0, index);
        document.getElementsByTagName("svg")[0].setAttribute("viewBox", viewBox);
        document.getElementsByTagName("svg")[1].setAttribute("viewBox", viewBox);

        svgWidth = parseFloat($(graph).attr("width")) * 4/3;
        $("#map").width(parseFloat($(graph).attr("width")) * 0.1);
        svgHeight = parseFloat($(graph).attr("height")) * 4/3;
        $.each($(graph).find(".edge"), function () {
            d3.select("#" + $(this).attr("id")).select("path").transition().duration(5000)
                .attr("d", $(this).find("path").attr("d"));

            d3.select("#" + $(this).attr("id")).selectAll("polygon").transition().duration(5000)
                .attr("points", $(this).find("polygon").attr("points"));
        });
        d3.selectAll(".edge").transition().duration(5000).style("opacity", 1);
//        d3.select("svg").attr("viewbox", viewBox);
        $("svg:first").attr("width", $(graph).attr("width"));
        $("svg:first").attr("height", $(graph).attr("height"));
        $("#nav-graph").attr("width", parseFloat($(graph).attr("width")) * 0.1);
        $("#nav-graph").attr("height", parseFloat($(graph).attr("height")) * 0.1);

        $("#nav-graph").find("#graph0").attr("transform", $(graph).find("#graph0").attr("transform"));
        $("#graph0").attr("transform", $(graph).find("#graph0").attr("transform"));
        $.each($(graph).find(".node"), function (i, node) {
            console.log($(this).find('rect').attr("x"));
            d3.select("#graph").select("#" + $(this).attr("id"))
                .select("rect").transition().duration(5000).attr({x: $(node).find('rect').attr("x"),
            y: $(node).find('rect').attr("y")});
            var texts = $("#graph")
                .find("#" + $(this)
                    .attr("id")).find("text");
            console.log("Length : " + texts.length);
            var graphNode = $("#" + $(node).attr("id"));
            $(texts).each(function (j) {
                var text = $(node).find('text').get(j);
                var graphText = $(graphNode).find('text').get(j);
                console.log("hey #" + $(graphText).attr("id"));
                d3.select("#" + $(node)
                    .attr("id"))
                    .select("#" + $(graphText).attr("id"))
                    .transition()
                    .duration(5000)
                    .attr({x: $(text).attr("x"),
                    y: $(text).attr("y")});
            })
        });

        $.each($(graph).find(".node"), function (i, node) {
            d3.select("#nav-graph").select("#" + $(this).attr("id") + "-map-node")
                .select("rect").transition().duration(5000).attr({x: $(node).find('rect').attr("x"),
            y: $(node).find('rect').attr("y")});
        });

        if (orientation === "vertical") {
            $("#scroll-content").css("display", "inline").animate({width: "80%"}, 2000);
            d3.select("#scroll-content").transition().duration(2000).style("float", "right");
            $("#HUD")
                .animate({width: "15%",
                          height: "100%"}, 2000);
        } else {
            $("#scroll-content").css("display", "block").animate({width: "100%"}, 2000);
            d3.select("#scroll-content").transition().duration(2000).style("float", "");
           $("#HUD")
                .animate({width: "100%",
                          height: "15%"}, 2000);
        }

        $('#scroll-content').mCustomScrollbar('update');

        resetGraphSize();
        resetMapGraph();
        setMapSize();
    });
}

/**
 *
 * @param suffix The suffix of the generated graph file. Either 'horizontal' or 'vertical'.
 * @returns {*}
 */
function getGraph(suffix) {
    "use strict";
    var graph = null;
    orientation = suffix;
    $.ajax({
        url: root + "/content/challenges/prereq_graph/generate_" + suffix,
        dataType: "text",
        async: false,
        success: function (data) {
            graph = data;
        }
    });
    return graph;
}


/**
 * Finds the GraphViz svg output and appends it to the #scroll-content div.
 */
function appendGraph(suffix) {
    "use strict";
    var graph = null;
    orientation = suffix;
    $.ajax({
        url: root + "/content/challenges/prereq_graph/generate_" + suffix,
        dataType: "text",
        async: false,
        success: function (data) {
            graph = data;
        }
    });
    if (graph !== null) {
        $(graph).insertBefore($("#scroll-background-bottom"));
        $("#map").append(graph);
    }
}


/**
 * Adds node decorations: the parent counting circle.
 */
function addNodeDecorations() {
    "use strict";
    $("#graph").find(".node").each(function (i) {
        appendCounterRect($(this), i);
    });
}


/**
 * Updates the number of non-active parent nodes for each node.
 * @param rectNode The svg rect that contains the parent count number.
 * @param {Boolean} show Determines whether graph should display parent count or not.
 */
function updateParentCount(rectNode, show) {
    "use strict";
    var node = window[rectNode.parent().attr("id")];
    rectNode.empty();

    if (show && node !== undefined) {
        $(rectNode).parent().children(".missing-counter").css("visibility", "visible");
        var textNode = document.createTextNode(getNonActiveParentNames(node).length.toString());
        rectNode.append(textNode);
    } else {
        $(rectNode).parent().children(".missing-counter").css("visibility", "hidden");
    }
}


/**
 * Gets node's non-active parent names.
 * @param {Node} node The node that is being evaluated.
 * @returns {Array} An array of the names of non-active/overridden parents of node.
 */
function getNonActiveParentNames(node) {
    "use strict";
    var parentNames = [];
    var parentArray;

    if (node.parents.length === 0) {
        return [];
    }

    for (var i = 0; i < node.parents.length; i++) {
        if (node.parents[i].status !== "active" &&
            node.parents[i].status !== "overridden" ) {
            parentNames.push(node.parents[i].name);
            parentArray = getNonActiveParentNames(node.parents[i]);

            for (var j = 0; j < parentArray.length; j++) {
                if ($.inArray(parentArray[j], parentNames) === -1) {
                  parentNames.push(parentArray[j]);
                }
            }
        }
    }

    return parentNames;
}


/**
 * Creates small icon on the Node rectangle.
 * @param parentRect The parent of the newly created svg rect/text/
 */
function appendCounterRect(parentRect, missingCounter) {
    "use strict";
    var counterRect = createOptionRect("counter-rect-",
                                       missingCounter,
                                       parseInt(parentRect.children(".rect").attr("x")) +
                                       parseInt(parentRect.children(".rect").attr("width")) - 25,
                                       parseInt(parentRect.children(".rect").attr("y")) +
                                       parseInt(parentRect.children(".rect").attr("height") - 20)/2,
                                       "none",
                                       "#3399FF",
                                       "missing-counter");

    var counterText = createOptionText("counter-text-",
                                       missingCounter,
                                       parseInt(parentRect.children(".rect").attr("x")) +
                                       parseInt(parentRect.children(".rect").attr("width")) - 15,
                                       parseInt(parentRect.children(".rect").attr("y")) +
                                       parseInt(parentRect.children(".rect").attr("height") - (-10))/2,
                                       "counter-text");
    
    counterRect.insertBefore(parentRect.children("text").first());
    counterText.insertAfter(parentRect.children("text").first()); 
}


/**
 * Creates an svg rect (displayed as a circle) that can be used to display information on a Node.
 * @param idPrefix The prefix for the created svg rect id.
 * @param idCounter The counter (suffix) for the created svg rect id.
 * @param posX The x position (attribute) of the svg rect.
 * @param posY The y position (attribute) of the svg rect.
 * @param rectFill The 'fill' style of the svg rect.
 * @param rectStroke The 'stroke' style of the svg rect.
 * @param rectClass The css class of the svg rect.
 * @returns {*|jQuery} The jQuery object of the svg rect.
 */
function createOptionRect(idPrefix, idCounter, posX, posY, rectFill, rectStroke, rectClass) {
    "use strict";
    return $(document.createElementNS("http://www.w3.org/2000/svg", "rect")).attr({
        id: idPrefix + idCounter,
        x: posX,
        y: posY,
        rx: 10,
        ry: 10,
        fill: rectFill,
        stroke: rectStroke,
        width: 20,
        height: 20,
        class: rectClass
    });
}


/**
 * Creates svg text to display within an svg rect (an 'option rect').
 * @param idPrefix The prefix for the created svg text id.
 * @param idCounter The counter (suffix) for the created svg text id.
 * @param posX The x position (attribute) of the svg text.
 * @param posY The y position (attribute) of the svg text.
 * @param textClass The css class of the svg text.
 * @returns {*|jQuery} The jQuery object of the created svg text.
 */
function createOptionText(idPrefix, idCounter, posX, posY, textClass) {
    "use strict";
    return $(document.createElementNS("http://www.w3.org/2000/svg", "text")).attr({
        id: idPrefix + idCounter,
        x: posX,
        y: posY,
        rx: 10,
        ry: 10,
        width: 20,
        height: 20,
        "text-anchor": "middle",
        "font-family": "Times,serif",
        class: textClass
    });
}