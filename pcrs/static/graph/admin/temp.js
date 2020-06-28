canvasElements = [];
color_normal = "black";
color_hover = "orange";

$(document).ready(function(){
    // Load popovers for the bootstrap hover tooltips
    $('[data-toggle="popover"]').popover();

    var theCanvas = $("#edges");
    var theTable = $("#quest_table > tbody");

    // Color the dependency paths by drawing a new dependency with a different color
    $(document).on("mouseenter", ".challenge-node", function(node) {
        var $id = $(node.target).closest("td").attr("id");
        canvasElements.forEach(function(element) {
            if (element['child'].attr("id") == $id) {
                addDependency(element["pos"], element["parent"], element["child"], save = false, color = color_hover);
            }
        });
    });
    // Reset the color of the dependency paths
    $(document).on("mouseleave", ".challenge-node", function(node) {
        reloadCanvas();
    });

    reloadCanvas();
    $.get(root + "/content/challenges/api/challenge_list", function (data) {
        var maxRow = 0;
        data.forEach(function (element) {
            if (element["y_pos"] > maxRow)
                maxRow = element["y_pos"];
        });
        for(var i = 0; i <= maxRow; i++) {
            theTable.append("<tr><td></td><td></td><td></td></tr>");
        }
        data.forEach(function (element) {
            theTable[0].rows[element["y_pos"]].cells[element["x_pos"]].setAttribute("id", element["id"]);
            generateNode(document.getElementById(element["id"]), "progress", element["name"], 0, null, element["description"]);
        });
        data.forEach(function (element) {
            element["prerequisite"].forEach(function (depend) {
                addDependency(depend["line_pos"], $("#" + depend["parent_challenge"]), $("#" + depend["child_challenge"]));
            });
        });
    });
});

function reloadCanvas() {
    var tableElement = $(document.getElementById("quest_table"));
    var canvasElement = $(document.getElementById("edges"));
    canvasElement[0].getContext("2d").clearRect(0, 0, canvasElement[0].width, canvasElement[0].height);
    canvasElement[0].style.position = "absolute";
    canvasElement[0].style.left = tableElement.offset().left;
    canvasElement[0].style.top = tableElement.offset().top;
    canvasElement[0].style.zIndex = 10;
    tableElement[0].style.zIndex = 11;
    canvasElement[0].setAttribute("width", tableElement.width());
    canvasElement[0].setAttribute("height", tableElement.height());
    canvasElements.forEach(function (element) {
        addDependency(element["pos"], element["parent"], element["child"], false, color_normal);
    });
    $('[data-toggle="popover"]').popover();
}

function removeDependencies(node) {
    for(var i = 0; i < canvasElements.length; i++) {
        if (canvasElements[i]["parent"] == node || canvasElements[i]["child"] == node) {
            canvasElements.splice(i, 1);
        }
    }
    reloadCanvas();
}

function addDependency(pos, parent, child, store = true, color = color_normal) {
    if (pos < 1 || pos > 3) {
        return null;
    }
    if (store) {
        theElement = [];
        theElement["pos"] = pos;
        theElement["parent"] = parent;
        theElement["child"] = child;
        canvasElements.push(theElement);
    }
    var parentRow = parent.closest("tr").index() + 1;
    var parentCol = parent.index();
    var childRow = child.closest("tr").index();
    var childCol = child.index();

    var nodeHorGap = parseFloat($("#quest_table").css("border-spacing").split(" ")[0]);
    var nodeVertGap = parseFloat($("#quest_table").css("border-spacing").split(" ")[1]);

    var imageWidth = $(".node-left").width() / 4;

    var srcX, srcY, destX, destY;
    var context = $("#edges")[0].getContext("2d");
    context.beginPath();
    if (childRow - (parentRow - 1) == 1) {
        srcX = nodeHorGap + (parent.width()/2) + (nodeHorGap + parent.width()) * parentCol;
        if (childCol == 0)
            srcX -= 15;
        else if (childCol == 2)
            srcX += 15;
        srcY = (nodeVertGap + parent.height()) * parentRow;
        destX = nodeHorGap + (child.width()/2) + (nodeHorGap + child.width()) * childCol;
        if (parentCol == 0)
            destX -= 15;
        else if (parentCol == 2)
            destX += 15;
        destY = nodeVertGap + (nodeVertGap + child.height()) * childRow;
        context.moveTo(srcX, srcY);
        context.lineTo(srcX, srcY + (imageWidth * pos));
        context.lineTo(destX, srcY + (imageWidth * pos));
        context.lineTo(destX, destY);
    } else { //Side Connection
        srcY = nodeVertGap + (parent.height()/2) + (nodeVertGap + parent.height()) * (parentRow - 1);
        destY = nodeVertGap + (child.height()/2) + (nodeVertGap + child.height()) * childRow;
        if (parentCol == 0) {
            srcX = nodeHorGap;
            destX = nodeHorGap;
            context.moveTo(srcX, srcY);
            context.lineTo(srcX - 15, srcY);
            context.lineTo(srcX - 15, destY);
            context.lineTo(destX, destY);
        } if (parentCol == 2) {
            srcX = (nodeHorGap * 3) + (parent.width() * 3)
            destX = (nodeHorGap * 3) + (child.width() * 3)
            context.moveTo(srcX, srcY);
            context.lineTo(srcX + 15, srcY);
            context.lineTo(srcX + 15, destY);
            context.lineTo(destX, destY);
        }
    }
    context.lineWidth = 3;
    context.strokeStyle = color;
    // Draw a few times to darken the line
    for (var i = 0; i < 3; i++) {
        context.stroke();
    }
}

function generateNode(HoldingElement, type, title, progress, depends, description) {
    var icon = "ban";
    var prog = "0%";
    if (type == "done") {
        icon = "check";
        prog = progress + "%";
    } else if (type == "progress") {
        icon = "pencil";
        prog = progress + "%";
    } else if (type == "locked") {
        icon = "lock";
        prog = "Locked";
    } else if (type == "expired") {
        icon = "ban";
        prog = "Past Due";
    }
    HoldingElement.innerHTML = '<div data-title="' + title + '"' +
                               'class="challenge-node"' +
                               'title="Description"' +
                               'data-delay=\'{"show":"0", "hide":"0"}\'' +
                               'data-offset="10px 10px"' +
                               'data-toggle="popover"' +
                               'data-content="' + description + '"' +
                               'data-trigger="hover"' +
                               '>' +
                               '<div class="node-body">' +
                               '<div class="node-left node-left-' + type + '">' +
                               '<i class="fa fa-' + icon + ' node-icon" aria-hidden="true"></i>' +
                               '</div>' +
                               '<div class="node-main">' +
                               '<div class="node-top">' +
                               title +
                               '</div>' +
                               '<div class="progress">' +
                               '<div class="progress-bar" role="progressbar" style="width:' + (isNaN(progress) ? "0" : progress) + '%"/>' +
                               '</div>' +
                               '</div>' +
                               '</div>' +
                               '</div>' +
                               '<div class="node-content">' +
                               '<p>' +
                               '<strong>Requires:</strong> ' + (depends != null ? depends : "None") +
                               '</p>' +
                               '</div>'
    reloadCanvas();
}
