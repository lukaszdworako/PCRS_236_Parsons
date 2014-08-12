/**
 * Sets the #change-orientation button click event.
 */
function setChangeOrientationEvent() {
    $("#change-orientation").click(function () {
        $("#scroll-content").scrollLeft(0);
        zoom = 100;
        var navGraphObject = $("#nav-graph");
        orientation = orientation === "horizontal" ? "vertical" : "horizontal";
        var newGraph = getGraph(orientation);
        setViewBoxOfGraphs(newGraph);
        $("#map").width(parseFloat($(newGraph).attr("width")) * 0.1);
        updateAbsoluteHeights(newGraph);
        animateGraphEdges(newGraph);
        d3.selectAll(".edge").transition().duration(5000).style("opacity", 1);
        $("svg:first").attr("width", $(newGraph).attr("width"));
        $("svg:first").attr("height", $(newGraph).attr("height"));

        navGraphObject.attr("width", parseFloat($(newGraph).attr("width")) * 0.1);
        navGraphObject.attr("height", parseFloat($(newGraph).attr("height")) * 0.1);
        navGraphObject.find("#graph0").attr("transform", $(newGraph).find("#graph0").attr("transform"));
        d3.select("#graph0").transition().duration(5000).attr("transform", $(newGraph).find("#graph0").attr("transform"));

        $.each($(newGraph).find(".node"), function (i, node) {
            d3.select("#graph").select("#" + $(this).attr("id"))
                .select("rect").transition().duration(5000).attr({x: $(node).find('rect').attr("x"),
            y: $(node).find('rect').attr("y")});
            var texts = $("#graph")
                .find("#" + $(this)
                    .attr("id")).find("text");
            var graphNode = $("#" + $(node).attr("id"));
            $(texts).each(function (j) {
                var text = $(node).find('text').get(j);
                var graphText = $(graphNode).find('text').get(j);
                d3.select("#" + $(node)
                    .attr("id"))
                    .select("#" + $(graphText).attr("id"))
                    .transition()
                    .duration(5000)
                    .attr({x: $(text).attr("x"),
                    y: $(text).attr("y")});
            });
            console.log(parseFloat(($(node).find('.rect').attr("height")) - 20)/2);
            console.log(parseFloat($(node).find('.rect').attr("height")));
            d3.select("#graph").select("#" + $(this).attr("id")).select(".missing-counter")
                .transition().duration(5000).attr({x: parseFloat($(node).find('.rect').attr("x")) + parseFloat($(node).find('.rect').attr('width'))  - 25,
                    y: parseFloat(
                        $(node).find('.rect')
                               .attr("y")) + (parseFloat($(node).find('.rect').attr("height")) - 20)/2});
            d3.select("#graph").select("#" + $(this).attr("id")).select(".counter-text")
                .transition().duration(5000).attr({x: parseFloat($(node).find('.rect').attr("x")) + parseFloat($(node).find('.rect').attr('width'))  - 15,
                    y: parseFloat(
                        $(node).find('.rect')
                            .attr("y")) + (parseFloat($(node).find('.rect').attr("height")) + 10)/2});

        });

        animateNavGraphNodes(newGraph);

        if (orientation === "vertical") {
            $("#scroll-content").css("display", "inline").animate({width: "80%"}, 2000);
            d3.select("#scroll-content").transition().duration(2000).style("float", "right");
            $("#HUD")
                .animate({width: "15%"}, 2000)
                .animate({height: "100%"}, 2000);
        } else {
            $("#scroll-content").css("display", "block").animate({width: "100%"}, 2000);
            d3.select("#scroll-content").transition().duration(2000).style("float", "");
            $("#HUD")
                .animate({height: "15%"}, 2000)
                .animate({width: "100%"}, 2000);
        }

        $('#scroll-content').mCustomScrollbar('update');

        setTimeout(function(){resetGraphView()}, 5000);
        setMapSize();
    });
}

function animateText() {

}

function animateOptionRects() {

}

function setViewBoxOfGraphs(graph) {
    var viewBox = getViewBox(graph);
    document.getElementsByTagName("svg")[0].setAttribute("viewBox", viewBox);
    document.getElementsByTagName("svg")[1].setAttribute("viewBox", viewBox);
}

function getViewBox(graph) {
    var index  = graph.indexOf("viewbox");
    var substr = graph.substring(index + 9);
    index = substr.indexOf("\"");
    var viewBox = substr.substring(0, index);
    return viewBox;
}

function animateNavGraphNodes(graph) {
    $.each($(graph).find(".node"), function (i, node) {
        d3.select("#nav-graph").select("#" + $(this).attr("id") + "-map-node")
            .select("rect").transition().duration(5000).attr({x: $(node).find('rect').attr("x"),
                y: $(node).find('rect').attr("y")}).attr('end', function() {resetGraphView();});;
    });
}

function animateGraphEdges(newGraph) {
    $.each($(newGraph).find(".edge"), function () {
        d3.select("#" + $(this).attr("id")).select("path").transition().duration(5000)
            .attr("d", $(this).find("path").attr("d"));

        d3.select("#" + $(this).attr("id")).selectAll("polygon").transition().duration(5000)
            .attr("points", $(this).find("polygon").attr("points"));
    });
}

function updateAbsoluteHeights(newGraph) {
    svgWidth = parseFloat($(newGraph).attr("width")) * 4/3;
    svgHeight = parseFloat($(newGraph).attr("height")) * 4/3;
}

function resetZoom() {
    zoom = 100;
}