$(document).ajaxError(function () {
    alert('Something went wrong.');
});

var $uiselected = null;


$(document).ready(function () {

    $(document).on('click', '.item', select);

    $(document).on('click', '#add-page', addPage);
    $(document).on('click', '.delete-page', deletePage);

    $(document).on('click', '#add-text', addText);
    $(document).on('click', '#save-text', saveText);

    $(document).on('click', '#save', savePages);


    $(".page").sortable({
        connectWith: ".page",
        update: function (event, ui) {
            $('#save').prop('disabled', false);
        }
    });

    $(".items").sortable({
        connectWith: ".page"
    });

    // make pages selectable
    $("#challenge").selectable({
        selecting: function (event, ui) {
            // allow only one page to be selected
            if ($(".ui-selected, .ui-selecting").length > 1) {
                $(ui.selecting).removeClass("ui-selecting");
            }
        }});

    // bind deletion of items to d key
    $(document).keypress(
        function (event) {
            if (event.which == 100 && $uiselected != null) {
                deleteItem($($uiselected));
            }
        });
});

function select(event) {
    if ($uiselected != null) {
        $uiselected.toggleClass('uiselected');
    }
    $uiselected = $(event.target).parent('.item');
    $uiselected.toggleClass('uiselected');
}

function addPage() {
    $.post(document.URL + '/page/create', {csrftoken: csrftoken})
        .success(function (data) {
            $new_item = $("<div/>", {
                class: "page well",
                id: "page-" + data['pk']
            });
            $delete = $("<i/>", {
                class: "delete-page glyphicon glyphicon-remove pull-right"
            });
            $new_item.prepend($delete);
            $('#challenge').append($new_item);
            $new_item.sortable();
        });
}

function deletePage() {
    if (confirm('Are you sure you would like to delete this page?')) {
        $item = $(event.target).parent('.page');
        $.post(document.URL + '/' + $item.attr('id') + '/delete')
            .success(function (data) {
                $item.remove();
            });
    }
}

function addText() {
    $uiselected = null;
    var $page = $('.ui-selected');
    if ($page.length == 0) {
        alert('Please select the page you would like to add the text to.')
    }
    else {
        $('#text-entry-modal').modal();
    }
}

function saveText(event) {
    var $page = $('.ui-selected');

    $.post(document.URL + '/' + $page.attr('id') + '/text/create', {
        text: $('#text-entry').val(),
        csrftoken: csrftoken
    })
        .success(function (data) {
            var $new_item = $("<div/>", {
                    html: $('#text-entry').val(),
                    class: "text well",
                    id: "textblock-" + data['pk']
            });
            $page.append($new_item);
            $('#save').prop('disabled', false);
        });
}

function deleteItem($item) {
    var id = $item.attr('id');
    // if text
    if (id.match('^textblock')) {
        $.post(document.URL + '/' + id + '/delete', {csrftoken: csrftoken})
            .success(function() { $item.remove() });
    }
    // video or problem: put the item back into the appropriate list
    if (id.match('^video')) {
        $('#videos').append($item.remove());
    }
    // problem
    if (id.match('^problem')) {
        var list_id = id.match('[^-]*'); // match up to the dash
        $('#'+list_id).append($item.remove());
    }
    $item.toggleClass('uiselected');
    $uiselected = null;
    $('#save').prop('disabled', false);
}

function savePages() {
    var page_object_list = $.map(
        $('.page'),
        function (el, i) {
            return [$.grep($(el).sortable('toArray'),
                function (e, i) {
                    return e != ''
                })];
        }
    );

    $.post(document.URL + '/pages', {
        page_object_list: JSON.stringify(page_object_list),
        csrftoken: csrftoken
    }).success(function () {
        $('#save').attr('disabled', 'disabled');
    });
}