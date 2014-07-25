var nodeCounter = -1;
var pathCounter = -1;
var missingCounter = 0;
var missingTextCounter = 0;

$(document).ready(function() {
    appendGraph();
    processGraph();
    vitalizeGraph(); 
    addNodeDecorations();
    setScrollableContent();
    $("#view-graph").draggable();
});

function setScrollableContent() {
    $("#scroll-content").mCustomScrollbar({
        axis:"xy",
        theme: "dark",
        // scrollButtons:{
        //   enable:true
        // },
        mouseWheel:{ enable: true,
                     axis: "x",
                     scrollAmount: 500 
                   },
        advanced:{ updateOnContentResize: true },
        keyboard:{ scrollAmount: 50 }, 
        callbacks:{
            whileScrolling: function() {
                $("#graph-view").css("left", 
                    2 + roundTo(($("#nav-graph").width() * this.mcs.leftPct)/100 
                        - ($("#graph-view").width()*this.mcs.leftPct)/100));
                $("#graph-view").css("top", 
                    ($("#map").height() * this.mcs.topPct)/100 
                        - ($("#graph-view").height()*this.mcs.topPct)/100);
            }
        }
    });
}

function roundTo(val) {
    if ((parseFloat(val) % 2) !== 0) {
        val = val - (val % 2);
    }
    return val;
}

/**
 * Adds additional attributes to the svg output.
 */
function processGraph() {
    $("polygon[fill*=white]").attr("fill", "none");

    $("path").css("fill", "none")
           .attr("id", function() { pathCounter++; return "p" + pathCounter; } );
}

/**
 * Finds the GraphViz svg output and appends it to the #scroll-content div.
 */
function appendGraph() {
    $.ajax({
        url: "graph_gen.svg",
        dataType: "text",
        async: false,
        success: function (data) {
            graph = data;
        }
    });
    $(graph).insertBefore($("#scroll-background"));
    $("#map").append(graph);
}

/**
 * Creates an svg rect.
 * @param
 * @param
 * @param
 * @param
 */
function createRect(posX, posY, width, height) {
    return $(document.createElementNS("http://www.w3.org/2000/svg", "rect")).attr({
        x: posX,
        y: posY,
        rx: 20,
        ry: 20,
        fill:"black",
        stroke: "blue",
        width: width,
        height: height
    });
}

/**
 * Adds node decorations: the video circle.
 */
function addNodeDecorations() {
    $("#graph .node").each(function() {
        appendCounterRect($(this));
    });
}

/**
 * Updates the number of non-active parent nodes for each node.
 */
function updateParentCount(rectNode, show) {
    var node = window[rectNode.parent().attr("id")];
    rectNode.empty();
    if (show) {
        $(rectNode).parent().children(".missing-counter").css("visibility", "visible");
        var textNode = document.createTextNode(getNonActiveParentNames(node).length);
        rectNode.append(textNode);
    } else {
        $(rectNode).parent().children(".missing-counter").css("visibility", "hidden");
    }
}

/**
 * Gets node's non-active parent names.
 */
function getNonActiveParentNames(node) {
    var parents = [];
    var parentNames = [];
    var parentArray;
    
    if (node.parents.length == 0) {
        return [];
    }

    for (var i = 0; i < node.parents.length; i++) {
        if (node.parents[i].status !== "active") { 
            parentNames.push(node.parents[i].name);
            parentArray = getNonActiveParentNames(node.parents[i]);
            for (var j = 0; j < parentArray.length; j++) {
                if ($.inArray(parentArray[j], parentNames) == -1) {
                  parentNames.push(parentArray[j]);
                }
            }
        }
    }

    return parentNames;
}

/**
 * Creates small video icon on the Node rectangle.
 * @param
 */
function appendCounterRect(parentRect) {
    var counterRect = createOptionRect("counter-rect-",
                                     missingCounter,
                                     parseInt(parentRect.children(".rect").attr("x")) 
                                     + parseInt(parentRect.children(".rect").attr("width")) - 25,
                                     parseInt(parentRect.children(".rect").attr("y")) 
                                     + parseInt(parentRect.children(".rect").attr("height") - 20)/2,
                                     "none",
                                     "#3399FF", 
                                     "missing-counter");
    var counterText = createOptionText("counter-text-",
                                       missingTextCounter,
                                       parseInt(parentRect.children(".rect").attr("x")) 
                                       + parseInt(parentRect.children(".rect").attr("width")) - 15,
                                       parseInt(parentRect.children(".rect").attr("y")) 
                                       + parseInt(parentRect.children(".rect").attr("height") - (-10))/2,
                                       "counter-text");
    
    counterRect.insertBefore(parentRect.children("text").first());
    counterText.insertAfter(parentRect.children("text").first()); 
    missingCounter++;
    missingTextCounter++;
}

function createOptionRect(idPrefix, idCounter, posX, posY, rectFill, rectStroke, rectClass) {
    return childRect = $(document.createElementNS("http://www.w3.org/2000/svg", "rect")).attr({
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

function createOptionText(idPrefix, idCounter, posX, posY, textClass) {
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