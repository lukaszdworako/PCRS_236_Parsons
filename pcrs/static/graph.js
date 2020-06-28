canvasElements = [];

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
    reloadCanvas();
});

function reloadCanvas() {
    var tableElement = $(document.getElementById("content"));
    var canvasElement = $(document.getElementById("edges"));
    canvasElement[0].style.position = "absolute";
    canvasElement[0].style.left = tableElement.offset().left;
    canvasElement[0].style.top = tableElement.offset().top;
    canvasElement[0].style.zIndex = -1;
    canvasElement[0].setAttribute("width", tableElement.width());
    canvasElement[0].setAttribute("height", tableElement.height());
    canvasElements.forEach(function (element) {
        joinNodes(canvasElement[0], element["pos"], element["parent"], element["child"], false);
    });
}

function joinNodes(canvas, pos, parent, child, store = true) {
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
    var nodeBuffer = parseFloat($("table").css("border-spacing").split(" ")[1]);
    var imageWidth = $(".node-left").width() / 4;
    var srcX = parent.offset().left + (parent.width()/2) + imageWidth;
    var srcY = parent.offset().top + parent.height();
    var destX = child.offset().left + (child.width()/2) + imageWidth;
    var destY = child.offset().top;
    var context = canvas.getContext("2d");
    context.beginPath();
    context.moveTo(srcX, srcY);
    context.lineTo(srcX, srcY + (imageWidth * pos));
    context.lineTo(destX, srcY + (imageWidth * pos));
    context.lineTo(destX, destY);
    context.stroke();
}

function generateNode(HoldingElement, type, title, progress, depends) {
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
         'data-delay=\'{"show":"0", "hide":"0"}\'' +
         'data-offset="10px 10px"' +
         'data-toggle="popover"' +
         'data-content="' +
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.' +
            '"' +
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
            '<p><b>Completion:</b> ' + prog + '</p>' +
            '<p>' +
                '<strong>Requires:</strong> ' + (depends != null ? depends : "None") +
            '</p>' + 
       '</div>' +
                               '</div>';
    reloadCanvas();
}
