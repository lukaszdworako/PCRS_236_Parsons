/*global $ */
/*global document */
/*global appendGraph */
/*global processGraph */
/*global setScrollableContent */
/*global setMainGraphID */
/*global addNodeDecorations */
/*global appendCounterRect */
/*global window */
/*global getNonActiveParentNames */
/*global vitalizeGraph */


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
 *
 * @param suffix The suffix of the generated graph file. Either 'horizontal' or 'vertical'.
 * @returns {*}
 */
function getGraph(suffix) {
    "use strict";
    var graph = null;

    if (suffix === 'vertical' && verticalGraph !== null) {
        console.log('cache');
        return verticalGraph;
    } else if (suffix === 'horizontal' && horizontalGraph !== null) {
        console.log('cache');

        return horizontalGraph;
    }

    orientation = suffix;
    $.ajax({
        url: root + "/content/challenges/prereq_graph/generate_" + suffix,
        dataType: "text",
        async: false,
        success: function (data) {
            graph = data;
        }
    });

    if (suffix === 'vertical') {
        verticalGraph = graph;
    } else if (suffix === 'horizontal') {
        horizontalGraph = graph;
    }

    return graph;
}


/**
 * Finds the GraphViz svg output and appends it to the #scroll-content div.
 */
function appendGraph(suffix) {
    "use strict";
    orientation = suffix;
    var graph = getGraph(suffix);
    $(graph).insertBefore($("#scroll-background-bottom"));
    $("#map").append(graph);
    window['graph'] = new Graph('graph');
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
 * @param missingCounter TODO: Define.
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
                                       (parseInt(parentRect.children(".rect").attr("height")) + 10)/2,
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