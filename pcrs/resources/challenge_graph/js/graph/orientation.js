/*global $, d3*/


/**
 * Sets the #change-orientation button click event.
 */
function setChangeOrientationEvent() {
    "use strict";
    var orientation = 'horizontal';
    $("#change-orientation").click(function () {
        var graphObject = $("#graph");
        var scrollObject = $("#scroll-content");
        var navGraphObject = $("#nav-graph");
        scrollObject.mCustomScrollbar("scrollTo", "0");
        resetZoom();
        orientation = orientation === "horizontal" ? "vertical" : "horizontal";
        var newGraph = getGraph(orientation);
        setViewBoxOfGraphs(newGraph);
        $("#map").width(parseFloat($(newGraph).attr("width")) * 0.1);
        updateAbsoluteHeights(newGraph);
        animateGraphEdges(newGraph);
        d3.selectAll(".edge").transition().duration(5000).style("opacity", 1);
        graphObject.attr("width", $(newGraph).attr("width"))
                   .attr("height", $(newGraph).attr("height"));

        navGraphObject.attr("width", parseFloat($(newGraph).attr("width")) * 0.1)
                      .attr("height", parseFloat($(newGraph).attr("height")) * 0.1);
        navGraphObject.find("#graph0").attr("transform", $(newGraph).find("#graph0").attr("transform"));
        d3.select("#graph0").transition().duration(5000).attr("transform", $(newGraph).find("#graph0").attr("transform"));

        $.each($(newGraph).find(".node"), function (i, node) {

            d3.select("#graph")
              .select("#" + $(this).attr("id"))
              .select("rect")
              .transition()
              .duration(5000).
              attr({x: $(node).find('rect').attr("x"),
                    y: $(node).find('rect').attr("y")});

            var texts = $("#graph")
                .find("#" + $(this)
                    .attr("id")).find("text");

            var graphNode = $("#" + $(node).attr("id"));

            $(texts).each(function (j) {
                var text = $(node).find('text').get(j);
                var graphText = $(graphNode).find('text').get(j);
                d3.select("#" + $(node).attr("id"))
                  .select("#" + $(graphText).attr("id"))
                  .transition()
                  .duration(5000)
                  .attr({x: $(text).attr("x"),
                         y: $(text).attr("y")});
            });

            d3.select("#graph")
              .select("#" + $(this).attr("id"))
              .select(".missing-counter")
              .transition()
              .duration(5000)
              .attr({x: parseFloat($(node).find('.rect').attr("x")) +
                        parseFloat($(node).find('.rect').attr('width'))  - 25,
                     y: parseFloat($(node).find('.rect').attr("y")) +
                       (parseFloat($(node).find('.rect').attr("height")) - 20) / 2});

            d3.select("#graph")
                .select("#" + $(this).attr("id"))
                .select(".counter-text")
                .transition()
                .duration(5000)
                .attr({x: parseFloat($(node).find('.rect').attr("x")) +
                          parseFloat($(node).find('.rect').attr('width'))  - 15,
                       y: parseFloat($(node).find('.rect').attr("y")) +
                         (parseFloat($(node).find('.rect').attr("height")) + 10) / 2});

        });

        animateNavGraphNodes(newGraph);

        scrollObject.mCustomScrollbar("destroy");

        if (orientation === "vertical") {
            scrollObject.css("display", "inline")
                        .animate({width: "80%"}, 2000);

            d3.select("#scroll-content").transition().duration(2000).style("float", "right");

            $("#HUD")
                .animate({width: "15%"}, 2000)
                .animate({height: "100%"}, 2000);

            // Set the mousewheel to scroll vertically
            setScrollableContent("y");

        } else {
            scrollObject.css("display", "block")
                        .animate({width: "100%"}, 2000);

            d3.select("#scroll-content")
              .transition()
              .duration(2000)
              .style("float", "");

            $("#HUD")
                .animate({height: "15%"}, 2000)
                .animate({width: "100%"}, 2000);

            // Set the mousewheel to scroll horizontally
            setScrollableContent("x");

        }

        setTimeout(function () { resetGraphView(); }, 5000);
        setMapSize();
    });
}

function setStyles() {
    "use strict";

}

function animateText() {
    "use strict";

}

function animateOptionRects() {
    "use strict";

}

function setViewBoxOfGraphs(graph) {
    "use strict";
    var viewBox = getViewBox(graph);
    document.getElementsByTagName("svg")[0].setAttribute("viewBox", viewBox);
    document.getElementsByTagName("svg")[1].setAttribute("viewBox", viewBox);
}

function getViewBox(graph) {
    "use strict";
    var index  = graph.indexOf("viewbox");
    var substr = graph.substring(index + 9);
    index = substr.indexOf("\"");
    return substr.substring(0, index);
}

function animateNavGraphNodes(graph) {
    "use strict";
    $.each($(graph).find(".node"), function (i, node) {
        d3.select("#nav-graph").select("#" + $(this).attr("id") + "-map-node")
            .select("rect").transition().duration(5000).attr({x: $(node).find('rect').attr("x"),
                y: $(node).find('rect').attr("y")}).attr('end', function () { resetGraphView(); });
    });
}

function animateGraphEdges(newGraph) {
    "use strict";
    $.each($(newGraph).find(".edge"), function () {
        d3.select("#" + $(this).attr("id")).select("path").transition().duration(5000)
            .attr("d", $(this).find("path").attr("d"));

        d3.select("#" + $(this).attr("id")).selectAll("polygon").transition().duration(5000)
            .attr("points", $(this).find("polygon").attr("points"));
    });
}

function updateAbsoluteHeights(newGraph) {
    "use strict";
    svgWidth = parseFloat($(newGraph).attr("width")) * 4 / 3;
    svgHeight = parseFloat($(newGraph).attr("height")) * 4 / 3;
}

function resetZoom() {
    "use strict";
    zoom = 100;
}