let canvasElements = [];
let currRow = 0;
let color_normal = "#000";
let color_hover = "orange";

let progress_done = "#8bc34a";
let progress_in_progress = "#ffc107";
let progress_locked = "#424242";
let progess_banned = "#f44336";

let even_quest = true;
let quest_start_color = [230, 230, 230];
let quest_end_color   = [240, 240, 240];

let minimap_window_size = 1224;
let graphData = null

let isDOMLoaded = false;
let isDataReady = false

//Start the async call ASAP, also has logic to ensure both the call and DOM
//is loaded before generating the graph.
getGraphData();
function getGraphData() {
    $.get(root + "/content/challenges/api/challenge_list", {option: '0'}, function(data) {
        graphData = data;
        isDataReady = true;
        if (isDOMLoaded)
            generateGraph(graphData);
    });
}

//Create event handlers for the graph
$(document).ready(function() {
    let theCanvas = $("#edges");
    let theTable = $("#challenge-graph");

    isDOMLoaded = true;
    if (isDataReady)
        generateGraph(graphData);

    // Load popovers for the bootstrap hover tooltips
    $('[data-toggle="popover"]').popover();

    // Color the dependency paths by drawing a new dependency with a different color
    $(document).on("mouseenter", ".challenge-node", function(node) {
        var $id = $(node.target).closest('.col-sm-2').attr("id");
        canvasElements.forEach(function(element) {
            if (element['child'] == $id) {
                addDependency(element["pos"], $("#" + element["parent"]),
                              $("#" + element["child"]), save = false, color = color_hover);
            }
        });
    });
    // Reset the color of the dependency paths
    $(document).on("mouseleave", ".challenge-node", function(node) {
        reloadCanvas();
    });

    theTable.scroll(function(node) {
        reloadCanvas();
    });

    $(window).resize(function() {
        reloadCanvas()
    });


    // Hacky method to get links working with challenge nodes
    $(document).on("click", ".challenge-node", function(event) {
        // Find the ID of the parent TD element
        $td_parent = $(event.target.closest('.col-sm-2'));
        $challenge_node = $($td_parent).find('.challenge-node');
        // Only allow them to go to a specific challenge if the content isn't locked
        if (['done', 'progress'].indexOf($challenge_node.attr('data-status')) >= 0)  {
            window.location.href = root + "/content/challenges/" + $td_parent.attr('id') + "/1";
        }
    });
});

/**
 * Reloads the canvas by redrawing all of the dependencies between each node.
 * Ensures all dependencies line up as the table is shifted around.
 * O(n) where n is the number of dependencies.
 */
function reloadCanvas() {
    var canvasElement = $("#edges");
    var tableElement = $("#challenge-graph").css("zIndex", "4");
    canvasElement[0].getContext("2d").clearRect(0, 0, canvasElement[0].width, canvasElement[0].height);
    canvasElement.css("zIndex", "0").css("pointerEvents", "none").attr("width", tableElement.width()).attr("height", tableElement.height()).css("paddingBottom", tableElement.css("paddingBottom"));
    canvasElements.forEach(function (element) {
        addDependency(element["pos"], $("#" + element["parent"]), $("#" + element["child"]), false, color_normal);
    });
    $('[data-toggle="popover"]').popover();
}

/**
 * Adds a quest grouping for each quest to the table.
 * O(1) I think, depending on how jQuery inserts rows,
 * it could be O(n) where n is number of rows in the table
 *
 * @param {number} questID The ID of the quest
 * @param {string} questName The name of the quest
 */
function addRowToTable(questID, questName, requiredQuiz) {
    // Add a row for each y-coordinate depth
    let row = $('<div/>').attr('y', currRow).addClass('row').addClass('table-row').attr("quest-id", questID);
    let quest_marker = $('<div/>').addClass('col-sm-2');
    let quest_marker_title = $('<h4/>').addClass('quest-marker-title');
    if (requiredQuiz != null) {
        quest_marker_title.html((questName == null) ? "" : questName);
        quest_marker_title.append('<br/><p style="font-size:12px;color:#777;">Requires ' + requiredQuiz + '</p>');
    }
    else {
        quest_marker_title.text((questName == null) ? "" : questName);
    }
    quest_marker.append(quest_marker_title);
    row.append(quest_marker);
    for (var j = 0; j < 3; j++) {
        var col = $('<div/>').attr('y', currRow).attr('x', j).attr('quest-id', questID).addClass('col-sm-2');
        row.append(col);
    }
    $("#challenge-graph").append(row);
}

/**
 * Logic to draw lines between any 2 given nodes.
 * O(1)
 */
function addDependency(pos, parent, child, store = true, color = color_normal) {
    if (pos < 1 || pos > 3 || parent.length == 0 || child.length == 0) {
        return null;
    }
    if (store) {
        theElement = [];
        theElement["pos"] = pos;
        theElement["parent"] = parent.attr("id");
        theElement["child"] = child.attr("id");
        canvasElements.push(theElement);
    }
    var parentRow = parent.closest('.row').index();
    var parentCol = parent.index() -1;
    var childRow = child.closest('.row').index();
    var childCol = child.index() - 1;

    var srcX, srcY, destX, destY;
    var canvas = $("#edges");
    var context = canvas[0].getContext("2d");

    //object positions vars relative to the window
    var canvas_pos = canvas.offset();
    var parent_pos = parent.offset();
    var child_pos = child.offset();

    parent_centre = parent_pos.left - canvas_pos.left + (parent.width() / 2);

    child_centre = child_pos.left - canvas_pos.left + (child.width() / 2);

    var parentArr = [0, 0, 0];
    var childArr = [0, 0, 0];

    parentArr[0] = parent_centre - (parent.width() / 4);
    parentArr[1] = parent_centre;
    parentArr[2] =  parent_centre + (parent.width() / 4);

    childArr[0] = child_centre - (child.width() / 4);
    childArr[1] = child_centre;
    childArr[2] =  child_centre + (child.width() / 4);

    if (parentCol == childCol) {
        srcX = parentArr[parentCol];
        srcY = parent_pos.top - canvas_pos.top + parent.height();
        destX = childArr[childCol];
        destY = child_pos.top - canvas_pos.top;
    } else if (parentCol < childCol) {
        if (childCol - parentCol == 1) {
            srcX = parentArr[parentCol + 1];
            srcY = parent_pos.top - canvas_pos.top + parent.height();
            destX = childArr[childCol -1];
            destY = child_pos.top - canvas_pos.top;
        } else {
            srcX = parentArr[2];
            srcY = parent_pos.top - canvas_pos.top + parent.height();
            destX = childArr[0];
            destY = child_pos.top - canvas_pos.top;
        }
    } else {
        if (parentCol - childCol == 1) {
            srcX = parentArr[parentCol - 1];
            srcY = parent_pos.top - canvas_pos.top + parent.height();
            destX = childArr[childCol + 1];
            destY = child_pos.top - canvas_pos.top;
        } else {
            srcX = parentArr[0];
            srcY = parent_pos.top - canvas_pos.top + parent.height();
            destX = childArr[2];
            destY = child_pos.top - canvas_pos.top;
        }
    }


    context.lineWidth = 3;
    context.strokeStyle = color;
    context.beginPath();
    context.moveTo(srcX, srcY);
    context.lineTo(destX, destY);
    context.stroke();


    context.lineWidth = 8;
    context.strokeStyle = color;
    context.beginPath();
    context.arc(srcX, srcY, 4, 0, 2*Math.PI, true);
    context.stroke();

    context.beginPath();
    context.arc(destX, destY, 4, 0, 2*Math.PI, true);
    context.stroke();
}

/**
 * Generates the HTML for a new challenge node and returns it as a string.
 * O(1)
 */
function generateNode(type, title, progress, depends, description) {
    var icon = "ban";
    var prog = 0;
    var color;
    if (type == "done") {
        icon = "check";
        prog = progress;
        color = progress_done;
    } else if (type == "progress") {
        icon = "pencil";
        prog = progress;
        color = progress_in_progress;
    } else if (type == "locked") {
        icon = "lock";
        prog = "Locked";
        color = progress_locked;
    } else if (type == "expired") {
        icon = "ban";
        prog = "Past Due";
        color = progress_banned;
    }
    return '<div data-title="' + title + '"' +
           'data-status="' + type + '"' +
           'class="challenge-node"' +
           'title="' + title + '"' +
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
           '<div class="progress-bar" role="progressbar"' +
           'style="background-color:' + color + ';' +
           'width:' + progress*100 + '%"/>' +
           '</div>' +
           '</div>' +
           '</div>' +
           '</div>' +
           '<div class="node-content">' +
           '<p>' +
           '<strong>Requires:</strong> ' + (depends != null ? depends : "None") +
           '</p>' +
           '</div>'
}

/**
 * Uses the above functions to generate the graph itself.
 * O(??)
 */
function generateGraph(data) {
    // Add the row and column divs (without any nodes)
    data.forEach(function(element) {
        addRowToTable(element['id'], element['name'], element['mastery_quiz']);
        currRow = 0;
        element['challenge'].forEach(function(challengeElement) {
            if (currRow < challengeElement['y_pos']) {
                while (currRow < challengeElement['y_pos']) {
                    currRow++;
                    addRowToTable(element['id'], null);
                }
            } else if (currRow > challengeElement['y_pos']) {
                console.log("Elements are not loading in proper order, check your sorting.");
                console.log("The graph may not appear as intended.");
            }
            var currentNode = $("div[quest-id='" + element['id'] + "'][x='" + challengeElement['x_pos'] + "'][y='" +
              challengeElement['y_pos'] + "']").attr('id', challengeElement['id']);
            var done = 0;
            var challengeDeps = "";
            var dependencies = challengeElement['prerequisite'];
            for (var i = 0; i < dependencies.length; i++) {
                addDependency(dependencies[i]["line_pos"], $("#" + dependencies[i]["parent_challenge_id"]),
                              $("#" + dependencies[i]["child_challenge_id"]));
                var parentNode = $('#' + dependencies[i]["parent_challenge_id"] + ' > .challenge-node')
                if (parentNode.attr("data-status") == "done"){
                    done++;
                } else {
                    challengeDeps += dependencies[i]["name"];
                    if (i != dependencies.length -1 - done){
                        challengeDeps += " | "
                    }
                }
            }
            if (challengeElement['enforce_prerequisites'] == false || done == dependencies.length) {
                if (challengeElement['completion'] == 1)
                    currentNode.html(generateNode("done", challengeElement["name"], challengeElement['completion'], null, challengeElement["description"]));
                else
                    currentNode.html(generateNode("progress", challengeElement["name"], challengeElement['completion'], null, challengeElement["description"]));
            }
            else {
                currentNode.html(generateNode("locked", challengeElement["name"], challengeElement['completion'], challengeDeps, challengeElement["description"]));
            }
        });
        currRow = 0;
        $("div.row[quest-id='" + element['id'] + "']").css("backgroundColor", even_quest ? quest_start_color : quest_end_color);
        even_quest = !even_quest;
	reloadCanvas();
    });

    //Minimap loading is terribly slow for the client (~200ms) lets
    //force this into an async function
    var int = setInterval( function() {
        let minimap = $('#challenge-graph').minimap({
            heightRatio : 0.70,
            widthRatio : 0.15,
            offsetHeightRatio : 0.2,
            offsetWidthRatio : 0.020,
            position : "right",
            touch: true,
            smoothScroll: true,
            smoothScrollDelay: 150
        });
        // On page load, hide the minimap if the window is too small
        if ($(window).width() < minimap_window_size) {
            minimap.hide();
        }
        // If we resize the window, hide/show the minimap (depending on size)
        $(window).resize(function() {
            if ($(window).width() < minimap_window_size) {
                minimap.hide();
            }
            else {
                minimap.show();
            }
        });
        clearInterval(int);
    }, 25);

    // Scroll down to where they're at
    $($('.row').get()).each(function(index, row) {
        let num_challenges = $(row).children('.col-sm-2[id]').length;
        let done_challenges = $(row).children('.col-sm-2[id]').find('.node-left-done').length;
        if (num_challenges != done_challenges) {
            $('html, body').animate({
                scrollTop: $(row).offset().top + 10
            });
            return false;
        }
    });
}
