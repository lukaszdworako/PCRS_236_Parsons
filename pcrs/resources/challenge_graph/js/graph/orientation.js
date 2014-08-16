/*global $, d3*/


/**
 * Sets the #change-orientation button click event.
 * TODO: The code has been difficult to split up. d3 transitions haven't been working in separate functions.
 */
function setChangeOrientationEvent() {
    "use strict";
    var orientation = 'horizontal';
    $("#change-orientation").click(function () {
        var graphObject = $("#graph");
        var scrollObject = $("#scroll-content");
        var navGraphObject = $("#nav-graph");

        var transitionDuration = 5000;
        var animationDuration = 2000;
        var ease = 'elastic';

        orientation = getNewOrientation(orientation);
        var newGraph = getGraph(orientation);
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

        if (orientation === "vertical") {
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
    });
}


/**
 * Sets the new coordinates of the rects, text, counter rects, and counter texts.
 * // TODO: Find out why below helper functions don't work.
 * @param newGraph The SVG content of the new graph.
 * @param ease The ease attribute of the d3 transitions. (Ex: 'linear', 'elastic'...)
 *        Refer to http://blog.vctr.me/experiments/transition-tweens.html for good examples.
 * @param transitionDuration The duration the d3 transitions take.
 */
function setNewGraphCoordinates(newGraph, ease, transitionDuration) {
    "use strict";

    $.each($(newGraph).find(".node"), function (i, node) {
        // TODO: Find out why below helper functions don't work.
        var texts = $("#graph")
            .find("#" + $(this)
                .attr("id")).find("text");

        var graphNode = $("#" + $(node).attr("id"));

        d3.select("#graph")
            .select("#" + $(this).attr("id"))
            .select("rect")
            .transition()
            .duration(transitionDuration)
            .ease(ease)
            .attr({x: $(node).find('rect').attr("x"),
                   y: $(node).find('rect').attr("y")});

        $(texts).each(function (j) {
            var text = $(node).find('text').get(j);
            var graphText = $(graphNode).find('text').get(j);
            d3.select("#" + $(node).attr("id"))
                .select("#" + $(graphText).attr("id"))
                .transition()
                .duration(transitionDuration)
                .ease(ease)
                .attr({x: $(text).attr("x"),
                       y: $(text).attr("y")});
        });

        d3.select("#graph")
            .select("#" + $(this).attr("id"))
            .select(".missing-counter")
            .transition()
            .duration(transitionDuration)
            .ease(ease)
            .attr({x: parseFloat($(node).find('.rect').attr("x")) +
                      parseFloat($(node).find('.rect').attr('width'))  - 25,
                   y: parseFloat($(node).find('.rect').attr("y")) +
                     (parseFloat($(node).find('.rect').attr("height")) - 20) / 2});

        d3.select("#graph")
            .select("#" + $(this).attr("id"))
            .select(".counter-text")
            .transition()
            .duration(transitionDuration)
            .ease(ease)
            .attr({x: parseFloat($(node).find('.rect').attr("x")) +
                      parseFloat($(node).find('.rect').attr('width'))  - 15,
                   y: parseFloat($(node).find('.rect').attr("y")) +
                     (parseFloat($(node).find('.rect').attr("height")) + 10) / 2});


    });
}


//function animateGraphNodes(transitionDuration, node, ease) {
//    d3.select("#graph")
//        .select("#" + $(this).attr("id"))
//        .select("rect")
//        .transition()
//        .duration(transitionDuration)
//        .ease(ease)
//        .attr({x: $(node).find('rect').attr("x"),
//            y: $(node).find('rect').attr("y")});
//}
//
//function animateText(transitionDuration, node, ease) {
//    var graphNode = $("#" + $(node).attr("id"));
//    var texts = $("#graph")
//        .find("#" + $(this).attr("id"))
//        .find("text");
//
//    $(texts).each(function (j) {
//        var text = $(node).find('text').get(j);
//        var graphText = $(graphNode).find('text').get(j);
//        d3.select("#" + $(node).attr("id"))
//            .select("#" + $(graphText).attr("id"))
//            .transition()
//            .duration(transitionDuration)
//            .ease(ease)
//            .attr({x: $(text).attr("x"),
//                y: $(text).attr("y")});
//    });
//}
//
//function animateMissingCounters(transitionDuration, node, ease) {
//    d3.select("#graph")
//        .select("#" + $(this).attr("id"))
//        .select(".missing-counter")
//        .transition()
//        .duration(transitionDuration)
//        .ease(ease)
//        .attr({x: parseFloat($(node).find('.rect').attr("x")) +
//            parseFloat($(node).find('.rect').attr('width'))  - 25,
//            y: parseFloat($(node).find('.rect').attr("y")) +
//                (parseFloat($(node).find('.rect').attr("height")) - 20) / 2});
//}
//
//function animateCounterText(transitionDuration, node, ease) {
//    console.log('its happening');
//    d3.select("#graph")
//        .select("#" + $(this).attr("id"))
//        .select(".counter-text")
//        .transition()
//        .duration(transitionDuration)
//        .ease(ease)
//        .attr({x: parseFloat($(node).find('.rect').attr("x")) +
//            parseFloat($(node).find('.rect').attr('width'))  - 15,
//            y: parseFloat($(node).find('.rect').attr("y")) +
//                (parseFloat($(node).find('.rect').attr("height")) + 10) / 2});
//
//}


/**
 * Sets the SVG viewBox attribute of the new graph.
 * @param newGraph The SVG content of the new graph.
 */
function setViewBoxOfGraphs(newGraph) {
    "use strict";
    var viewBox = getViewBox(newGraph);
    document.getElementsByTagName("svg")[0].setAttribute("viewBox", viewBox);
    document.getElementsByTagName("svg")[1].setAttribute("viewBox", viewBox);
}


/**
 * Gets the new viewBox attribute from the new graph.
 * @param newGraph The SVG content of the new graph.
 * @returns {string} The viewBox attribute setting.
 */
function getViewBox(newGraph) {
    "use strict";
    var index  = newGraph.indexOf("viewbox");
    var substr = newGraph.substring(index + 9);
    index = substr.indexOf("\"");
    return substr.substring(0, index);
}


/**
 * Animates the #nav-graph nodes (map nodes).
 * @param newGraph The SVG content of the new graph.
 * @param ease The ease attribute of the d3 transitions. (Ex: 'linear', 'elastic'...)
 *        Refer to http://blog.vctr.me/experiments/transition-tweens.html for good examples.
 * @param transitionDuration The duration the d3 transitions take.
 */
function animateNavGraphNodes(newGraph, ease, transitionDuration) {
    "use strict";
    $.each($(newGraph).find(".node"), function (i, node) {
        d3.select("#nav-graph")
          .select("#" + $(this)
          .attr("id") + "-map-node")
          .select("rect")
          .transition()
          .duration(transitionDuration)
          .ease(ease)
          .attr({x: $(node).find('rect').attr("x"),
                 y: $(node).find('rect').attr("y")})
          .attr('end', function () { window['graph-view'].reset(); });
    });
}


/**
 * Animates the graph edges.
 * @param newGraph he SVG content of the new graph.
 * @param ease The ease attribute of the d3 transitions. (Ex: 'linear', 'elastic'...)
 *        Refer to http://blog.vctr.me/experiments/transition-tweens.html for good examples.
 * @param transitionDuration The duration the d3 transitions take.
 */
function animateGraphEdges(newGraph, ease, transitionDuration) {
    "use strict";
    $.each($(newGraph).find(".edge"), function () {
        d3.select("#" + $(this).attr("id"))
          .select("path")
          .transition()
          .duration(transitionDuration)
          .ease(ease)
          .attr("d", $(this).find("path").attr("d"));

        d3.select("#" + $(this).attr("id"))
          .selectAll("polygon")
          .transition()
          .duration(transitionDuration)
            .ease(ease)
          .attr("points", $(this).find("polygon").attr("points"));
    });
}


/**
 * Updates the absolute sizes of the main graph.
 * @param newGraph The SVG content of the new graph.
 */
function updateAbsoluteSizes(newGraph) {
    "use strict";
    svgWidth = parseFloat($(newGraph).attr("width")) * 4 / 3;
    svgHeight = parseFloat($(newGraph).attr("height")) * 4 / 3;
}


/**
 * Resets the zoom (scale factor-esque var) to 100.
 */
function resetZoom() {
    "use strict";
    zoom = 100;
}


/**
 * Resets the scroll position of #scroll-content to 0.
 */
function resetScrollPosition() {
    "use strict";
    $("#scroll-content").mCustomScrollbar("scrollTo", "0");
}


/**
 * Gets the orientation of the new graph.
 * @param orientation The current orientation of the graph. Either 'vertical' or 'horizontal'.
 * @returns {string} The new orientation of the graph.
 */
function getNewOrientation(orientation) {
    "use strict";
    return orientation === "horizontal" ? "vertical" : "horizontal";
}


/**
 * Removes the custom scrollbar from #scroll-content.
 */
function removeScrollbar() {
    "use strict";
    $("#scroll-content").mCustomScrollbar("destroy");
}