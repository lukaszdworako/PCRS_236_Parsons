var nodes = [];
var edges = [];
var zoom = 100;
var currentNode = null;
var videoLinkCounter = 0;
var svgWidth, svgHeight;
var graphViewWidth, graphViewHeight;

/*
 * Initializes the graph settings.
 */
function initializeGraphSettings() {
    $('#graph path').attr('data-active', 'inactive');
    $('#graph .node').attr('data-active', 'inactive');

    // var userData = getJSON();
    var userData = {
        // "node3" : [10, 10]
    }

    $.each(nodes, function (i, node) {
        window[node].updateStatus();
        window[node].updateSVG();
        $.each(window[node].outEdges, function (i, edge) {
            if (typeof edge !== "undefined") {
                 edge.updateStatus();
            }
        });
    });

    $.each(userData, function(i, val) {
        if (val[0] === val[1]) {
            window[i].turn();
            console.log(typeof i);
        }
    });
}

function getJSON() {
    $.ajax({
        url: "challenge_prerequisite_data_for_user",
        dataType: "text",
        async: false,
        success: function (data) {
            json = data;
        }
    });
    return json;
}

/*
 * Builds the interactive graph based on intersections between paths and poygons (with a large offset).
 */
function buildGraph() {
    $('#graph .node').each(function (i) {
        makeNode($(this).attr('id'));
    });
    
    $('#graph path').each(function (i) {
        var coords = $(this).attr('d').split(/[\s,HVL]/);
        var xStart = parseFloat(coords[0].substr(1));
        var yStart = parseFloat(coords[1]);
        var yEnd = parseFloat(coords.pop());
        var xEnd = parseFloat(coords.pop());
        var startNode = '';
        var endNode = '';

        $('#graph .node').each(function (index) {
            
            var r = $(this).children('rect');
            var xRect = parseFloat(r.attr('x'));
            var yRect = parseFloat(r.attr('y'));
            var width = parseFloat(r.attr('width'));
            var height = parseFloat(r.attr('height'));//childG.append(createRect(xRect, yRect, width, height));
            if (intersects(xStart, yStart, xRect, yRect, width, height, 1)) {
                startNode = $(this).attr('id');
            }

            if (intersects(xEnd, yEnd, xRect, yRect, width, height, 20)) {
                endNode = $(this).attr('id');
            }

            if (startNode !== '' && endNode !== '') {
                return false;
            }
        });

        if (typeof window[startNode] === "undefined") {
            console.log("Undefined start node for: " + $(this).attr("id"));
        }
        if (typeof window[endNode] === "undefined") {
            console.log("Undefined end node for: " + $(this).attr("id"));
        }

        makeEdge(window[startNode], window[endNode], $(this).attr('id'));
    });
}

/*
 * Pulses the takeable coures (opacity from 0.4 to 0.95). This is put in a setInterval function.
 */
function pulseTakeable() {
    $(nodes).each(function (i, node) {
        if (window[node].status === "doable") {
            if ($("#" + node).css("opacity") > 0.9) {
                $("#" + node).fadeTo("slow", 0.4);
            } else {
                $("#" + node).fadeTo("slow", 1);
            }
        } else if (window[node].status === "active") {
            $("#" + node).fadeTo("fast", 1);
        }
    });

    // if ($("#graph-view").css("opacity") > 0.9) {
    //     $("#graph-view").fadeTo("slow", 0.4);
    // } else {
    //     $("#graph-view").fadeTo("slow", 1);
    // }
}

/*
 * Sets the mouse callbacks for the nodes.
 */
function setMouseCallbacks() {
    $("#graph .node").click(function (event) {
        turnNode(event);
    });

    $("#graph .node").mouseenter(function (event) {
            updateParentCount($(this).children(".counter-text"), true);
            hoverFocus(event);
    });

    $("#graph .node").mouseleave(function (event) {
        updateParentCount($(this).children(".counter-text"), false);
        hoverUnfocus(event);
    });
}

/*
 * Builds the interactive prerequisite graph structure.
 * IMPORTANT: For map height, use #scroll-content height, for width use svgWidth!
 */
function vitalizeGraph() {
    setMainGraph();
    setMainGraphID();
    getAbsoluteWidths();
    setMapSize();
    $("#map svg").attr("id", "nav-graph").attr("height", svgHeight* 0.1).attr("width", svgWidth * 0.1);
    $("#map .node").attr("data-active", "display");
    $("#map path").attr("data-active", "inactive");
    $("#map").append("<div id='graph-view'></div>");
    $("#graph-view").css("width", $("#scroll-content").width() * 0.1)
                    .css("height", $("#scroll-content").height() * 0.1);
    setMapDragNavigation();
    addScrollBackgroundHeight();
    removeArrowHeadsFromMap();
    setMapClickNavigation();

    buildGraph();
    setMouseCallbacks();
    initializeGraphSettings();
    setInterval(pulseTakeable, 1000);

    $("text").attr("id", function(i) {return "text-" + i;});
    setKeydown();
}

function setMapDragNavigation() {
    $("#graph-view").draggable({containment: "#map"});
    $("#graph-view").on( "drag", function( event, ui ) {
        var axisArray = [(parseInt($(this).css("top"))/parseInt($("#nav-graph").css("height")) 
            * parseInt($("#graph").css("height"))), (parseInt($(this).css("left"))/parseInt($("#nav-graph").css("width")) 
            * parseInt($("#graph").css("width")))];
        $("#scroll-content").mCustomScrollbar("scrollTo", axisArray
            ,{
          callbacks:false,
          scrollInertia:250
        });
    });
}

function getAbsoluteWidths() {
    svgWidth = parseInt($("svg").css("width"));
    svgHeight = parseInt($("svg").css("height"));
    graphViewHeight = parseInt($("#graph-view").css("width"));
    graphViewHeight = parseInt($("#graph-view").css("height"));
}

function setMapSize() {
    $("#map").css("height", $("#scroll-content").height() * 0.1)
             .css("width", svgWidth * 0.1);
}

function setMainGraph() {
    mainGraph = $("svg");
}

function setMainGraphID() {
    $("svg:first").attr("id", "graph");
}

function addScrollBackgroundHeight() {

    // It is a relative height, meant for the overflow of #scroll-content
    $("#scroll-background").css("height", 550 - $("#graph").height());
}

function removeArrowHeadsFromMap() {
    $("#nav-graph polygon").remove();
}

function setMapClickNavigation() {
    $("#map").click(function(e) {
        var xCenter, yCenter;
        var offset = $(this).offset();
        var x = e.clientX - offset.left;
        var y = e.clientY - offset.top;
        if (x + parseFloat($("#graph-view").css("width")) < parseFloat(parseFloat($("#nav-graph").css("width")))) {
            if ((x - parseFloat($("#graph-view").css("width"))) > 0) {
                xCenter = x - parseFloat($("#graph-view").css("width"))/2;
            } else {
                xCenter = 0;
            }
        } else {
            xCenter = parseFloat(parseFloat($("#nav-graph").css("width"))) - parseFloat($("#graph-view").css("width"));
        }
        if (y + parseFloat($("#graph-view").css("height"))/2 < parseFloat(parseFloat($("#map").css("height")))) {
            console.log("Case 1");
            if ((y - parseFloat($("#graph-view").css("height")))/2 > 0) {
                yCenter = y - parseFloat($("#graph-view").css("height"))/2;
            } else {
                yCenter = 0;
            }
        } else {
            yCenter = parseFloat(parseFloat($("#map").css("height"))) - parseFloat($("#graph-view").css("height"));
        }

        $("#graph-view").css("left", xCenter);
        $("#graph-view").css("top", yCenter);
        var axisArray = [(parseInt($("#graph-view").css("top"))/parseInt($("#nav-graph").css("height")) 
            * parseInt($("#graph").css("height"))), (parseInt($("#graph-view").css("left"))/parseInt($("#nav-graph").css("width")) 
            * parseInt($("#graph").css("width")))];
        $("#scroll-content").mCustomScrollbar("scrollTo", axisArray
            ,{
          callbacks:false,
          scrollInertia:250
        });
    });
}

$(window).resize(function() {
    resetMapGraph();
    // $("#graph").css("height", svgHeight * zoom/100);
    // $("#graph").css("width", svgWidth * zoom/100);
    // $("#graph-view").css("width", $("#scroll-content").width() * 0.1 * 100/zoom);
    // $("#graph-view").css("height", $("#scroll-content").height() * 0.1 * 100/zoom);
    // $("#graph-view").css("top", ($("#nav-graph").height() * $("#scroll-content").scrollTop())/100 
    //     - ($("#graph-view").height()*$("#scroll-content").scrollTop())/100);
    // $("#graph-view").css("left", ($("#nav-graph").width() * $("#scroll-content").scrollLeft())/100 
    //     - ($("#graph-view").width()*$("#scroll-content").scrollLeft())/100);
});

function zoomOut() {
    if (zoom > 10) {
        zoom = zoom - 10;
    }
    $("#graph").css("height", svgHeight * zoom/100);
    $("#graph").css("width", svgWidth * zoom/100);
    resetMapGraph();
}

function zoomIn() {
    if (zoom < 200) {
        zoom = zoom + 10;
    }
    $("#graph").css("height", svgHeight * zoom/100);
    $("#graph").css("width", svgWidth * zoom/100);
    resetMapGraph();
}

function resetMapGraph() {
    if (($("#scroll-content").width() * 0.1 * 100/zoom) < parseFloat($("#nav-graph").css("width"))) { 
        $("#graph-view").css("width", $("#scroll-content").width() * 0.1 * 100/zoom);
    } else {
        $("#graph-view").css("width", $("#map").css("width"));
    }
    if ((svgHeight * 0.1 * 100/zoom) < parseFloat($("#nav-graph").css("height"))) { 
        $("#graph-view").css("height", $("#scroll-content").height() * 0.1 * 100/zoom);
    } else {
        $("#graph-view").css("height", $("#map").css("height"));
    }
    $("#graph-view").css("top", ($("#nav-graph").height() * $("#scroll-content").scrollTop())/100 
        - ($("#graph-view").height()*$("#scroll-content").scrollTop())/100);
    $("#graph-view").css("left", ($("#nav-graph").width() * $("#scroll-content").scrollLeft())/100 
        - ($("#graph-view").width()*$("#scroll-content").scrollLeft())/100);

    $("#scroll-background").css("height", 550 * zoom/100 - $("#graph").height());
}

/*
 * Sets the keydown events for zoom and scrolling.
 */
function setKeydown() {
    $(document).keydown(function(e){
        switch (e.keyCode) {
            case 187: // + Key
                zoomIn();
                break;
            case 189: // - Key
                zoomOut();
                break;
        }
        $("#scroll-content").mCustomScrollbar("update");
    });
}
