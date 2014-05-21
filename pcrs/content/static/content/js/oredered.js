$(document).ready(function () {
    $.ajaxSetup({ traditional: true });

    var $save_button = $("input[name='save-order']");
    $save_button.hide();

    $("#ordered").sortable({
        change: function (event, ui) {
            $save_button.show();
        }
    });
    $save_button.click(
        function () {
            $.post(document.URL + '/order',
                {
                    order: $("#ordered").sortable('toArray'),
                    csrftoken: csrftoken
                })
                .success(function (data) {
                    $save_button.hide();
                })
                .error(function () {
                    alert('Something went wrong.');
                });
        }
    );
});

function dragAndDrop(items) {
    items.sortable({
        connectWith: ".quest-box",
        scroll: false,
        appendTo: 'body',
        revert: false,
        receive: function (event, ui) {
            // list has changed - provide visual clue that some changes are not saved
            $save_button.removeClass('disabled');
            $(event.target).find(".challenge").each(function () {
                if ($(this).find(".close").length == 0)
                    $(this).prepend('<div class="close pull-right"><icon class="icon-white icon-remove"></icon></div>');
            });
        }
    });
}

$("#challenges").find(".challenge").draggable({
        connectToSortable: ".quest-box",
        helper: "clone",
        appendTo: 'body',
        revert: "invalid",
        scroll: false,
        zIndex: 9999
    });