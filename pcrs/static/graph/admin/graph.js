var canvasElements = [];
var currRow = 0;
var color_normal = "black";
var color_hover = "orange";

var progress_done = "#8bc34a";
var progress_in_progress = "#ffc107";
var progress_locked = "#424242";
var progress_banned = "#f44336";

var add_dependency_mode = false;
var del_dependency_mode = false;
var add_quest_mode = false;
var del_quest_mode = false;
var add_row_mode = false;
var del_row_mode = false;
var dependency_node = null;
var dependency_node_alt = null;

var quest_start_color = [0, 0, 0];
var quest_end_color   = [255, 255, 255];

var minimap_window_size = 1224;

// generates graph
function generateGraph() {

    var questCount = 0;
    $.get(root + "/content/challenges/api/challenge_list", {option: 'all'}, function(data) {
        data.forEach(function (element) {
            questCount++;
            addRowToTable(element['id'], element['name'])
            element['challenge'].forEach(function (challengeElement) {
                if (currRow < challengeElement['y_pos']) {
                    for ( ; currRow < challengeElement['y_pos']; ) {
                        currRow++;
                        addRowToTable(element['id'], null)
                    }
                } else if (currRow > challengeElement['y_pos']) {
                    console.log("Elements are not loading in proper order, check your sorting");
                    return;
                }
                var dependencies = challengeElement['prerequisite'];
                var node = $("div[quest-id='" + element['id'] + "'][x='" + challengeElement['x_pos'] + "'][y='" + challengeElement['y_pos'] + "']");
                node.attr('id', challengeElement['id']);
                if ('score' in challengeElement && (challengeElement['score'] / challengeElement['out_of']) == 1) {
                    generateNode(document.getElementById(challengeElement["id"]), "done", challengeElement["name"], 100, null, challengeElement["description"]);
                }
                // They've attempted the problem, but not gotten 100% yet
                else if ('score' in challengeElement) {
                    generateNode(document.getElementById(challengeElement["id"]), "progress", challengeElement["name"],
                                 (challengeElement['score'] / challengeElement['out_of']) * 100, null, challengeElement["description"]);
                } else {
                    var done = 0;
                    var challengeDeps = "";
                    for (var i = 0; i < dependencies.length; i++) {
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
                    if (done == dependencies.length) {
                        generateNode(document.getElementById(challengeElement["id"]), "progress", challengeElement["name"], 0, null, challengeElement["description"]);
                    }
                    else {
                        generateNode(document.getElementById(challengeElement["id"]), "locked", challengeElement["name"], 0, challengeDeps, challengeElement["description"]);
                    }
                }
                for (var i = 0; i < dependencies.length; i++) {
                    addDependency(dependencies[i]["line_pos"], $("#" + dependencies[i]["parent_challenge_id"]), $("#" + dependencies[i]["child_challenge_id"]));
                }
            });
            currRow = 0;

        });
        if (questCount == 0) {
                        $('<div class="row row-line" > <i quest-id="12" id="add-quest" class="fa fa-plus-circle" title="Add Quest"></i></div>')
            .appendTo($("#challenge-graph"));
            $('<div class="row table-row" y="0"><div class="col-sm-12 cold-md-2"><h4 class="quest-marker-title">Make a Quest<h4></div><div class="col-sm-3 table-col" y="0" x="0"></div><div class="col-sm-3 table-col" y="0" x="1"></div><div class="col-sm-3 table-col" y="0" x="2"></div></div>')
            .appendTo($("#challenge-graph"));
        }
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
            let num_challenges = $(row).children('.col-sm-3[id]').length;
            let done_challenges = $(row).children('.col-sm-3[id]').find('.node-left-done').length;
            if (num_challenges != done_challenges) {
                $('html, body').animate({
                    scrollTop: $(row).offset().top + 10
                });
                return false;
            }
        });
    });
}

$(document).ready(function(){
    // Load popovers for the bootstrap hover tooltips
    $('[data-toggle="popover"]').popover();

    var theCanvas = $("#edges");
    var theTable = $("#challenge-graph");

    generateGraph();

    // Color the dependency paths by drawing a new dependency with a different color
    $(document).on("mouseenter", ".challenge-node", function(node) {
        reloadCanvas();
        var $id = $(node.target).closest('.col-sm-3').attr("id");
        canvasElements.forEach(function(element) {
            if (element['child'] == $id) {
                addDependency(element["pos"], $("#" + element["parent"]), $("#" + element["child"]), save = false, color = color_hover);
            }
        });


    });
    // Reset the color of the dependency paths
    $(document).on("mouseleave", ".challenge-node", function(node) {
         reloadCanvas();
    });


    // delete row button handler
    $(document).on("click", "#rm-row", function() {
        delRow($(this).closest('div.row'));
    });

    // add row button handler
    $(document).on("click", "#add-row", function() {
        var row = $(this).closest('div.row')
        addRow(row.attr('quest-id'), row.attr('y'), row);
    });

        // remove dependencies button handler
    $(document).on("click", "#rm-dependencies", function(btn) {
        if($.contains(document.getElementById("challenge-graph"), btn.target)) {
            deleteDependencyButton();
        }
    });

    // add dependencies button handler
    $(document).on("click", "#add-dependencies", function(btn) {
        if($.contains(document.getElementById("challenge-graph"), btn.target)) {
            createDependencyButton();
        }
    });

    $(document).on("click", ".close", function(btn) {
        if($.contains(document.getElementById("challenge-graph"), btn.target)) {
            rmNode($(this).closest('.col-sm-3'));
        }
    });

    //remove Quest
    $(document).on("click", "#rm-quest", function() {
        rmQuest($(this).closest('div.row').attr('quest-id'));
    });

    //add Quest
    $(document).on("click", "#add-quest", function() {
            var row  = $(this).closest('div.row');
            addRow('new-quest', 0, row );
            dependency_node = $(".selected-green");
            dependency_node_alt = row;
            $('#quest-modal-text').val("");
            $('#quest-modal-select').children().remove();
            $.get(root + "/content/quests/api/quest_list_unused", function(data) {
                data.forEach(function (element) {
                    $("#quest-modal-select").append("<option value='" + element['name'] + "'> (" + element['id'] + ") " + element['name'] + "</option>");
                });
                $("#quest-modal").modal("show").css("zIndex", 9000);
            });

    });

    // add node
    $(document).on("click", "#add-node", function(){
        var col = $(this).closest('.table-col')
        col.addClass('selected-green');
        addNodeModal();
    });

    $(document).on("keyup", "#NodeSearch", function(){
        var value = $(this).val().toLowerCase();
        $("#node-modal-select ").attr('size', 6);
            $("#node-modal-select option").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $(document).on("click", ".node-left", function(){
        var col = $(this).closest('.table-col')
        if (!(add_dependency_mode || del_dependency_mode)){
            window.location.href = root + "/content/challenges/" + col.attr('id');
        }
    });

    theTable.scroll(function(node) {
        reloadCanvas();
    });

    $(window).resize(function() {
        reloadCanvas()
    });

    //Make clicking a challenge node take the user to the edit page
    $(document).on("click", ".challenge-node", function(event) {

    });

    $(document).on("click", ".quest-marker-title", function(event) {
        // Find the ID of the parent TD element
        $parent = $(event.target.closest('.row'));
        newPath = root + "/content/quests/"
        // if the button is "Make a Quest", parent's quest-id is undefined.
        if ($parent.attr('quest-id') === undefined) {
            window.location.href = newPath + "create"
        } else {
            window.location.href = newPath + $parent.attr('quest-id');
        }

    });

    reloadCanvas();
});

$(document).on("click", function(event) {
    if (add_dependency_mode && $.contains(document.getElementById("challenge-graph"), event.target)) {
        if (dependency_node == null) {
            dependency_node = $(event.target).closest("div.col-sm-3");
            dependency_node.toggleClass("selected-green");
        } else {
            if (dependency_node.closest("div.row").index() > $(event.target).closest("div.row").index()) {
                var linePos = 1;
                if ($(event.target).closest("div.col-sm-3").index() == 2)
                    linePos = 2;
                else if ($(event.target).closest("div.col-sm-3").index() == 3)
                    linePos = 3;
                addDependency(linePos, $(event.target).closest("div.col-sm-3"), dependency_node);
                $.post(root + "/content/challenges/api/modify_dependencies",
                       {"mode": "create", "parent_id": $(event.target).closest("div.col-sm-3").attr("id"),
                        "child_id": dependency_node.attr("id"), "line_pos": linePos },
                       null);
            } else if (dependency_node.closest("div.row").index() < $(event.target).closest("div.row").index()) {
                var linePos = 1;
                if (dependency_node.index() == 2)
                    linePos = 2;
                else if (dependency_node.index() == 3)
                    linePos = 3;
                addDependency(linePos, dependency_node, $(event.target).closest("div.col-sm-3"));
                $.post(root + "/content/challenges/api/modify_dependencies",
                       {"mode": "create", "child_id": $(event.target).closest("div.col-sm-3").attr("id"),
                        "parent_id": dependency_node.attr("id"), "line_pos": linePos },
                       null);
            }
            $(".selected-green").removeClass("selected-green");
            dependency_node = null;
            add_dependency_mode = false;
        }
    } else if (del_dependency_mode && $.contains(document.getElementById("challenge-graph"), event.target)) {
        if (dependency_node == null) {
            dependency_node = $(event.target).closest("div.col-sm-3");
            dependency_node.toggleClass("selected-red");
        } else {
            if (dependency_node.closest("div.row").index() > $(event.target).closest("div.row").index()) {
                removeDependency($(event.target).closest("div.col-sm-3").attr("id"), dependency_node.attr("id"));
            } else if (dependency_node.closest("row").index() < $(event.target).closest("div.col-sm-3").index()) {
                removeDependency(dependency_node.attr("id"), $(event.target).closest("div.col-sm-3").attr("id"));
            }
            $(".selected-red").removeClass("selected-red");
            dependency_node = null;
            del_dependency_mode = false;
        }
    }
});

$(document).keyup(function (event) {
    if (event.which == 27) {
        exitAllModes();
    }
});

function reloadCanvas() {
    var tableElement = $("#challenge-graph");
    var canvasElement = $("#edges");
    canvasElement[0].getContext("2d").clearRect(0, 0, canvasElement[0].width, canvasElement[0].height);
    canvasElement[0].style.zIndex = 3;
    tableElement[0].style.zIndex = 5;
    canvasElement.attr("width", tableElement.width());
    canvasElement.attr("height", tableElement.height());
    canvasElement.css("paddingBottom", tableElement.css("paddingBottom"));
    canvasElements.forEach(function (element) {
        addDependency(element["pos"], $("#" + element["parent"]), $("#" + element["child"]), false, color_normal);
    });
    handleDragging();
}

function addRowToTable(questID, questName) {
    let row = $('<div/>').attr('y', currRow).attr('quest-id', questID).addClass('row').addClass('table-row');
    let quest_marker = $('<div/>').addClass('col-sm-2').addClass('col-sx-2');
    let quest_marker_title = $('<h4/>');
    quest_marker_title.addClass('quest-marker-title');
    quest_marker_title.text((questName == null) ? "" : questName);
    if (questName != null) {
        let questAddRm = $('<div/>').addClass('quest-btns');
        let buttonQuestAdd = $('<i/>').attr('quest-id', questID).attr('id', 'add-quest').addClass('fa').addClass('fa-plus-circle').attr("title", "Add Quest Below");
        let buttonQuestRm = $('<i/>').attr('quest-id', questID).attr('id', 'rm-quest').addClass('fa').addClass('fa-minus-circle').attr("title", "Remove Quest");
        quest_marker.append(quest_marker_title);
        questAddRm.prepend(buttonQuestAdd);
        questAddRm.append(buttonQuestRm);
        quest_marker.append(questAddRm);
    }
    $(row).append(quest_marker);
    for (var j = 0; j < 3; j++) {
        var col = $('<div/>').attr('y', currRow).attr('x', j).attr('quest-id', questID).addClass('col-sm-3').addClass('col-sx-3').addClass('table-col');
        var addNode = $('<i/>').attr('id', 'add-node').addClass('fa').addClass('fa-plus-square').attr("title", "Add Node");
        col.append(addNode);
        $(row).append(col);
    }
    let rowAddRm = $('<div/>').addClass('col-sm-1').addClass('col-sx-1').addClass('row-btns').attr('y', currRow).attr('quest-id', questID);
    let buttonAdd = $('<i/>').attr('id', 'add-row').addClass('add-row').addClass('fa').addClass('fa-plus-circle').attr("title", "Add Row Below");
    let buttonRm = $('<i/>').attr('id', 'rm-row').addClass('rm-row').addClass('fa').addClass('fa-minus-circle').attr("title", "Remove Row");
    $(rowAddRm).append(buttonAdd);
    $(rowAddRm).append(buttonRm);
    $(row).append(rowAddRm);
    $("#challenge-graph").append(row);
}

function removeDependencies(id) {
    $.post(root + "/content/challenges/api/modify_dependencies",
        {"mode": "remove all", "child_id": id, "parent_id": id },
        null);
    for(var i = 0; i < canvasElements.length; i++) {
        if (canvasElements[i]["parent"] == id || canvasElements[i]["child"] == id) {
            updateIcon($('#' + canvasElements[i]["child"]));
            canvasElements.splice(i, 1);
            i = i - 1;

        }
    }
    reloadCanvas();
}
// removed dependencies based on the given parent id and child id
function removeDependency(parentID, childID) {
    for(var i = 0; i < canvasElements.length; i++) {
        if (canvasElements[i]["parent"] == parentID && canvasElements[i]["child"] == childID) {
            canvasElements.splice(i, 1);
            $.post(root + "/content/challenges/api/modify_dependencies",
                       {"mode": "remove", "child_id": childID, "parent_id": parentID },
                       null);

            updateIcon($('#' + childID));
            break;
        }
    }
    reloadCanvas();
}

function createDependencyButton() {
    if (del_dependency_mode) {
        deleteDependencyButton();
    }
    add_dependency_mode = !add_dependency_mode
    if (add_dependency_mode == false) {
        $(".selected-green").removeClass("selected-green");
        dependency_node = null;
    }
}

function deleteDependencyButton() {
    if (add_dependency_mode) {
        createDependencyButton();
    }
    del_dependency_mode = !del_dependency_mode
    if (del_dependency_mode == false) {
        $(".selected-red").removeClass("selected-red");
        dependency_node = null;
    }
}

function exitAllModes() {
    if (add_dependency_mode) {
        createDependencyButton();
    }
    if (del_dependency_mode) {
        deleteDependencyButton();
    }
    if (add_quest_mode) {
        createQuestButton();
    }
    if (del_quest_mode) {
        deleteQuestButton();
    }
    if (add_row_mode) {
        createRowButton();
    }
    if (del_row_mode) {
        deleteRowButton();
    }
}

function addNewQuestHandler() {
    var questName;
    if ($("#quest-modal-text").val() == "")
        questName = $("#quest-modal-select").find(":selected").attr("value");
    else
        questName = $("#quest-modal-text").val();
    parentRow = dependency_node.index();
    childRow = dependency_node.index();
    var nodeIDs = [];
    for(var y = parentRow; y <= childRow; y++) {
        for(var x = 1; x <= 3; x++) {
            var nodeID = $("div.row").eq(y).children()[x].getAttribute("id");
            if (nodeID != null) {
                nodeIDs.push(nodeID);
            }
        }
    }
    $.post(root + "/content/quests/api/new_quest", {"quest_name": questName, "prev_quest_id": dependency_node_alt.attr("quest-id"),  "affected_challenges": nodeIDs}, function (data) {
        for(var y = parentRow; y <= childRow; y++) {
            var nodeID = $("div.row").eq(y).attr("quest-id", data["new_quest"]);
            for(var i = 1; i <= 4; i++) {
                $("div.row").eq(y).children()[i].setAttribute("quest-id", data["new_quest"]);
            }
            $($("div.row").eq(y).children()[0]).children()[0].innerHTML = questName;
        }
    });
    $(".selected-green").removeClass("selected-green");
    dependency_node = null;
    dependency_node_alt = null;
    add_quest_mode = false;
}

function addNewQuestCancelHandler() {
    var row =  $(".selected-green")
    if (row.attr("quest-id",) == "new-quest") {
        row.remove();
    } else{
        row.removeClass("selected-green");
    }
    dependency_node = null;
    dependency_node_alt = null;
    add_quest_mode = false;
}

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

    updateIcon(child, lock = true);

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

function generateNode(HoldingElement, type, title, progress, depends, description) {
    var icon = "ban";
    var prog = "0%";
    var rmNodeBtn = ' ';
    var dependencyBtns = ' ';
    var color;
    if (type == "done") {
        icon = "check";
        prog = "0" + "%";
        color = progress_locked;
    } else if (type == "progress") {
        icon = "pencil";
        prog = progress + "%";
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

    rmNodeBtn = '<div class="challenge-close"> <a class="close"></a></div>';
    dependencyBtns = '<i class="rm-dependency fa fa-minus" id="rm-dependencies"> </i> ' +
                     '<i class="add-dependency fa fa-plus" id="add-dependencies"> </i> '
    HoldingElement.innerHTML = '<div class="challenge-node"' +
                               ' title="Description" >' +
                               '<div class="node-body">'+
                               rmNodeBtn +
                               '<div class=" node-left node-left-' + type + '">' +
                               '<i class="fa fa-' + icon + ' node-icon" aria-hidden="true"></i>' +
                               '</div>' +
                               '<div class="node-main">' +
                               '<div class="node-top">' +
                               title +
                               '</div>' +
                               '<div class="progress">' +
                               '<div class="progress-bar" role="progressbar"' +
                                'style="background-color:' + color + ';' +
                                'width:' + (isNaN(progress) ? "0" : progress) + '%"/>' +
                               '</div>' +
                               '</div>' +
                               '</div>' +
                               '</div>' +
                               '<div class="node-content">' +
                               '<p style="text-align:center;">' + "Dependencies" +
                               dependencyBtns +
                               '</p>' +
                               '</div>'


    reloadCanvas();
}

// deletes the row given by $row iff the row has no nodes in a currently
function delRow($row) {
    var done = false;
    $row.children().each(function (index) {
        if($(this).children('.challenge-node').length > 0) {
            alert("This row has nodes in it.\nRemove them first.");
            done = true;
            return;
        }
    });
    if (done == true){
        return;
    }
    $row.remove();
    var quests = $("div.row[quest-id='" + $row.attr("quest-id") + "']")
    var yCount = 0;
    quests.each(function (index) {
        $(this).attr("y", yCount);
        $(this).children().each(function (index) {
            if (!$(this).hasClass("quest-marker")) {
                if ($(this).attr("y") != yCount) {
                    $(this).attr("y", yCount);
                    if ($(this).children('.challenge-node').length > 0)
                        $.post(root + "/content/challenges/api/move_challenge",
                               {"challenge_id": $(this).attr("id"), "x_pos": $(this).attr("x"), "y_pos": yCount,
                                "quest_id": $(this).attr("quest-id"), "nullify": 'false'},
                                null);
                }
            }
        });
        yCount++;
    });
    reloadCanvas();
}

function addRow(questID, rowNum, row) {
    let newRow = $('<div/>').attr('y', rowNum).attr('quest-id', questID).addClass('row').addClass('table-row');
    let quest_marker = $('<div/>').addClass('col-sm-2');
    let quest_marker_title = $('<h4/>');
    quest_marker_title.addClass('quest-marker-title');
    let title = row.find('.quest-marker-title').text()

    //if this row is place holder for a new Quest
    if (questID == 'new-quest') {
        newRow.addClass('selected-green');
        title = ' ';
        quest_marker_title.text(title);
        quest_marker.append(quest_marker_title);
        let questAddRm = $('<div/>').addClass('quest-btns');
        let buttonQuestAdd = $('<i/>').attr('id', 'add-quest').addClass('fa').addClass('fa-plus-circle').attr("title", "Add Quest");
        let buttonQuestRm = $('<i/>').attr('id', 'rm-quest').addClass('fa').addClass('fa-minus-circle').attr("title", "Remove Quest");
        quest_marker.append(quest_marker_title);
        questAddRm.prepend(buttonQuestAdd);
        questAddRm.append(buttonQuestRm);
        quest_marker.append(questAddRm);
    }


    $(newRow).append(quest_marker);

    for (var j = 0; j < 3; j++) {
        var col = $('<div/>').attr('y', rowNum).attr('x', j).attr('quest-id', questID).addClass('col-sm-3').addClass('table-col');
        var addNode = $('<i/>').attr('id', 'add-node').addClass('fa').addClass('fa-plus-square').attr("title", "Add Node");
        col.append(addNode);
        $(newRow).append(col);
    }
    let rowAddRm = $('<div/>').addClass('col-sm-1').addClass('row-btns').attr('y', rowNum).attr('quest-id', questID);
    let buttonAdd = $('<i/>').attr('id', 'add-row').addClass('add-row').addClass('fa').addClass('fa-plus-circle').attr("title", "Add Row Below");
    let buttonRm = $('<i/>').attr('id', 'rm-row').addClass('rm-row').addClass('fa').addClass('fa-minus-circle').attr("title", "Remove Row");
    $(rowAddRm).append(buttonAdd);
    $(rowAddRm).append(buttonRm);
    $(newRow).append(rowAddRm);

    if (questID == 'new-quest') {
        var quests = $("div.row[quest-id='" + row.attr("quest-id") + "']");
        var lastRow = row;
        quests.each(function (index) {
            if ($(this).attr("y") > lastRow.attr("y")){
                lastRow = $(this);
            }

        });
        $(newRow).insertAfter(lastRow);

    } else {

        $(newRow).insertAfter(row);

        var quests = $("div.row[quest-id='" + questID + "']");
        var yCount = 0;
        quests.each(function (index) {
            $(this).attr("y", yCount);
            $(this).children('.table-col').each(function (index) {
                if ($(this).attr("y") != yCount) {
                    $(this).attr("y", yCount);
                    if ($(this).children('.challenge-node').length > 0) {
                        $.post(root + "/content/challenges/api/move_challenge",
                               {"challenge_id": $(this).attr("id"), "x_pos": $(this).attr("x"), "y_pos": yCount,
                                "quest_id": $(this).attr("quest-id"), "nullify": 'false'},
                                null);
                    }
                }
            });
            yCount++;
        });

    }
    reloadCanvas();


}

//removing the node given by node
function rmNode(node) {
    var id = node.attr('id');
    node.removeAttr('id');
    node.children().remove();
    var addNode = $('<i/>').attr('id', 'add-node').addClass('fa').addClass('fa-plus-square').attr("title", "Add Node");
    node.append(addNode);
    $.post(root + "/content/challenges/api/move_challenge",
       {"challenge_id": id, "x_pos": node.attr("x"), "y_pos": node.attr("y"),
        "quest_id": node.attr("quest-id"), "nullify": 'true'},
        null);
    removeDependencies(id);
}

// removes a Quest by the given quest ID
function rmQuest(questID) {
    if (confirm("are you sure want to delete this quest")){
        $.post(root + "/content/quests/api/remove_quest", {"old_quest": questID}, function(result){location.reload()});
    }
}

// sets and displays add node modal
function addNodeModal(){
        $.get(root + "/content/challenges/api/challenge_list_unplaced", function (data) {
            $('#node-modal-select').children().remove();
            data.forEach(function(element) {
                $("#node-modal-select").append("<option value='" + element['id'] + "'> " + element['name'] + "</option>");
            });
            $('#NodeSearch').val('');
            $('#node-modal-text').val('');
            $("#node-modal").modal("show").css("zIndex", 9000);
        });
}

function addNodeHandler() {
    var node = $(".selected-green");
    if ($("#node-modal-text").val() == "") {
        var id = $("#node-modal-select").find(":selected").attr("value");
        if(id == null ) {
            alert("no node selected")
            node.removeClass('selected-green');
            return
        }
        var name = $("#node-modal-select").find(":selected").text();
        unplacedNode = $("#" +id);
        unplacedNode.parent().remove();
        node.children().remove();
        node.attr('id', id);

        generateNode(document.getElementById(id), "done", name, 100, null, "description");
        $.post(root + "/content/challenges/api/move_challenge",
           {"challenge_id": id, "x_pos": node.attr("x"), "y_pos": node.attr("y"),
            "quest_id": node.attr("quest-id"), "nullify": 'false'},
            null);
    } else {
        var name = $("#node-modal-text").val();
        $.post(root + "/content/challenges/api/create_challenge", {"name": name, "x_pos": node.attr("x"), "y_pos": node.attr("y"),
            "quest_id": node.attr("quest-id")}, function (data) {
             if(data["id"] != -1){
                node.children().remove();
                node.attr('id', data["id"]);

                generateNode(document.getElementById(data["id"]), "done", name, 100, null, "description");
             } else {
                alert("invalid node name");
             }

        });
    }
    node.removeClass('selected-green')
}

// switches the icon for a certain node
function updateIcon(node, lock = false) {

    var icon = node.find('.node-left')
    if(lock) {
        icon.addClass('node-left-locked').removeClass('node-left-progress');
        icon.children().addClass('fa-lock').removeClass('fa-pencil');
    }else {
        icon.removeClass('node-left-locked').addClass('node-left-progress');
        icon.children().removeClass('fa-lock').addClass('fa-pencil');
    }


}