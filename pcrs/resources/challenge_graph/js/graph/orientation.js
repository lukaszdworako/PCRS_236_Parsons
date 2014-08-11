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
        $("svg:first").attr("width", $(graph).attr("width"));
        $("svg:first").attr("height", $(graph).attr("height"));
        $("#nav-graph").attr("width", parseFloat($(graph).attr("width")) * 0.1);
        $("#nav-graph").attr("height", parseFloat($(graph).attr("height")) * 0.1);
        console.log(parseFloat($(graph).attr("height")));
        $("#nav-graph").find("#graph0").attr("transform", $(graph).find("#graph0").attr("transform"));
        d3.select("#graph0").transition().duration(5000).attr("transform", $(graph).find("#graph0").attr("transform"));

        $.each($(graph).find(".node"), function (i, node) {
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
