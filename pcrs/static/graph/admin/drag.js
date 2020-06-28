original = null;

function handleDragging() {
    $(function() {
        $(".challenge-node").draggable({
            stack: "div",
            helper: "clone",
            zIndex: 9999,
            containment: "window",
            appendTo: 'body',
            scroll: true,
            start: function() {
                $original_div = $(this);
                $original_div.css("zIndex", 9999);
                $original_td = $(this).parent();
                $original_td.css("zIndex", 9999);
                original = $original_td;
                var tds = $('.table-col');
                tds.addClass('drag-available');
                $original_td.removeClass('drag-available');
                $.each(tds, function (index, value) {
                    value = $(value);
                    if (value.children("div").length == 0)
                        value.addClass('empty-block');
                        value.addClass('table-col');
                });
                $('.quest-marker').removeClass('drag-avaliable');
                $('.quest-marker').removeClass('empty-block');
            },
            stop: function(event, ui) {
                $('.drag-available').removeClass('drag-available');
                $('.empty-block').removeClass('empty-block');
                $(this).css("zIndex", 0);
                $(this).parent().css("zIndex", 9000);
                $(".tab-content").css("overflow-x", "hidden");
            },
            revert: "invalid",
            revertDuration: 100,
        });
        $(".table-col").droppable({
            accept: function () {
                return $(this).hasClass('empty-block');
            },
            drop: function(event, ui) {
                var $this = $(this);
                ui.draggable.parent().append($(this).children());
                $(this).append(ui.draggable);
                ui.draggable.css({
                    left: '',
                    top: ''
                });
                ui.draggable.position({
                    my: "center",
                    at: "center",
                    of: $this,
                    using: function(pos) {
                        $(this).animate(pos, 0, "linear");
                    }
                });
                ui.draggable.parent().attr("id", original.attr("id"));
                var isRemoved = false
                $.post(root + "/content/challenges/api/move_challenge",
                       {"challenge_id": ui.draggable.parent().attr("id"), "x_pos": ui.draggable.parent().attr("x"), "y_pos": ui.draggable.parent().attr("y"),
                        "quest_id": ui.draggable.parent().attr("quest-id"), "nullify": isRemoved},
                       null);

                original.removeAttr("id");
                // if a node has be moved to a different row remove its dependencies
                if(ui.draggable.parent().attr("quest-id") != original.attr("quest-id") || ui.draggable.parent().attr("y") != original.attr("y")){
                    removeDependencies(ui.draggable.parent().attr("id"));
                }
                reloadCanvas();
                if (original.children('.fa').length == 0){
                    original.append($('<i/>').attr('id', 'add-node').addClass('fa').addClass('fa-plus-square').attr("title", "Add Node"))
                }
            }
        });
    });
}
