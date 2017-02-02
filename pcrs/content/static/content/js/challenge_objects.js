var $uiselected = null;
var source_button = null;

$(document).ready(function () {

    $(document).on('click', '.item', select);

    $(document).on('click', '#add-page', addPage);
    $(document).on('click', '.delete-page', deletePage);
    $(document).on('click', '.remove_item', deleteItemHelper);

    $(document).on('click', '#add-text', addText);
    $(document).on('keypress', '#add-text', add_text_enter);
    $(document).on('click', '#save-text', saveText);
    $(document).on('click', '#save-page-num', select_given_page);

    $(document).on('click', '#save_top', savePages);
    $(document).on('click', '#save_bot', savePages);
    $(document).on('click', '.btn-object-add', add_text_enter);

    $('.btn-object-visibility').on('click', change_problem_visibility);

    $(document).on('change', '#page_num', update_page_location);

    $(".page").sortable({
        connectWith: ".page",
        update: function (event, ui) {
            $('#save_top').prop('disabled', false);
            $('#save_bot').prop('disabled', false);
//            resize_problems();
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

    var original_position = $('.problem-tab-content').offset().top;
    $(window).scroll(function(e){
        $el = $('.problem-tab-content');
        var challenge_bottom = $('#challenge').position().top + $('#challenge').height();
        var new_height = $(window).height();

        if (challenge_bottom - $(window).scrollTop() < new_height){
            new_height =  challenge_bottom - $(window).scrollTop();
        }
        if ($(window).scrollTop() > original_position) {
            $el.css({
                'margin-top':$(window).scrollTop()-original_position+10,
                'height':new_height});
        }
        else{
            $el.css({
                'margin-top':''});
        }
    });

    if ($(window).scrollTop() > original_position) {
            $('.problem-tab-content').css({
                'margin-top':$(window).scrollTop()-original_position+10,
                'height':$(window).height() - 60});
    }

    var new_height = $(window).height();
    var challenge_bottom = $('#challenge').position().top + $('#challenge').height();
    if (challenge_bottom - $(window).scrollTop() < new_height){
        new_height =  challenge_bottom - $(window).scrollTop() - 60;
    }
    $('.problem-tab-content').css({'height':new_height});

//    resize_problems();
});

function select_given_page(){
    /**
     * For Visually impaired users, after they choose page and location add content
     */

    var selected_page = $('#page_num').val().trim();
    var selected_location = $('#page_location').val().trim();
    if (!selected_page.isNaN){
        if ($(document).find('#challenge').find('[id*="page-"]').length >= selected_page){
            if (selected_page > 0){
                if ($(source_button).hasClass("btn-object-add")){
                    $($($(document).find('#challenge').find('[id*="page-"]')[selected_page-1]).children()[selected_location]).after($(source_button).parent());
                    $('#save_top').prop('disabled', false);
                    $('#save_bot').prop('disabled', false);
//                    resize_problems();
                }
                else{
                    $(document).find('#challenge').find('[id*="page-"]').removeClass("ui-selected");
                    $($(document).find('#challenge').find('[id*="page-"]')[selected_page-1]).addClass("ui-selected");
                    addText();
                }
            }
            else{
                alert("Number should not be negative");
            }
        }
        else{
            alert("Number is too big");
        }
    }
    else{
        alert("Input must be a number");
    }
}

function add_text_enter(event){
    /**
     * Set up page number choices for visually impaired users
     */

    source_button = null;
    if(event.which == 13 || event.which == 1){
        event.preventDefault();
        source_button = this;
        var number_of_pages = $('#challenge').children().length;
            $('#page-entry-modal').find('.pcrs-modal-title').text("There are "+number_of_pages+" pages. To which page and in what position you want to add the element to?");
        $('#page_num').empty();
        for (var page_num = 1; page_num < number_of_pages+1; page_num++){
            $('#page_num').append("<option value="+page_num+">"+page_num+"</option>");
        }
        update_page_location();
        $('#page-entry-modal').modal();
    }
}

function update_page_location(){
    /**
     * Change the possible problem locations given selected page
     */

    var selected_page_num = $('#page_num').val() - 1;
    var number_of_components = $($('[id*="page-"]')[selected_page_num]).children().length;
    $('#page_location').empty();
    for (var comp_index = 0; comp_index < number_of_components; comp_index++){
        $('#page_location').append("<option value="+comp_index+">"+comp_index+"</option>");
    }
}

function select(event) {
    /**
     * Allows to select a ui element
     */

    if ($uiselected != null) {
        $uiselected.toggleClass('uiselected');
    }
    $uiselected = $(event.target).parent('.item');
    $uiselected.toggleClass('uiselected');
}

function addPage() {
    /**
     * Add a new page to the window
     */

    $.post(document.URL + '/page/create', {csrftoken: csrftoken})
        .success(function (data) {
            $new_item = $("<div/>", {
                class: "page",
                id: "page-" + data['pk']
            });
            $delete = $("<i/>", {
                class: "delete-page xs-x-button-right"
            });
            $new_item.prepend($delete);
            $('#challenge').append($new_item);
            $new_item.sortable({
                connectWith: ".page",
                update: function (event, ui) {
                    $('#save_top').prop('disabled', false);
                    $('#save_bot').prop('disabled', false);
//                    resize_problems();
                }
            });
        });
}

function deletePage() {
    /**
     * remove selected page form the window
     */

    if (confirm('Are you sure you would like to delete this page?')) {
        $item = $(this).parent('.page');
        $.post(document.URL + '/' + $item.attr('id') + '/delete')
            .success(function (data) {
                $item.remove();
//                resize_problems();
            });
    }
}

function addText() {
    /**
     *  Allows to add text of button was clicked
     */

    $uiselected = null;
    var $page = $('.ui-selected');
    if ($page.length == 0) {
        alert('Please select the page you would like to add the text to.')
    }
    else {
        $('#text-entry-modal').attr('textblock-pk', '');
        $('#text-entry').val('');
        $('#text-entry-modal').modal();
//        resize_problems();
    }
}

function updateText(pk) {
    var text = $('#textblock-' + pk + ' .html').text();
    /*
     * ui-selectee is needed for dragging to look nice.
     * We don't want it to show up in the edit box, though!
     */
    $('#text-entry-modal').attr('textblock-pk', pk);
    $('#text-entry').val(text);
    $('#text-entry-modal').modal();
}

function saveText(event) {
    /**
     * Add a text element to a page
     */

    var $page = $('.ui-selected');

    var pk = $('#text-entry-modal').attr('textblock-pk');
    var text = $('#text-entry').val();

    if ( ! text) {
        // Blank fields break stuff!
        return;
    }

    if (pk) {
        // Update an existing entry
        $.post(document.URL + '/textblock-' + pk + '/update', {
            'text': text,
        }).success(function (data) {
            $('#textblock-' + pk + ' p').html(text);

            $('#save_top').prop('disabled', false);
            $('#save_bot').prop('disabled', false);
        });
    } else {
        // Create a new entry
        $.post(document.URL + '/' + $page.attr('id') + '/text/create', {
            text: text,
            csrftoken: csrftoken
        }).success(function (data) {
            var $new_item = $("<div/>", {
                html: "<div><p class='ui-selectee'>" + $('#text-entry').val() + "</p></div>",
                class: "textblock item ui-selectee",
                id: "textblock-" + data['pk']
            });
            $new_item.prepend($("<button/>",{
                class: "remove_item ui-selectee xs-x-button-right",
                title: "Delete Item",
                html:"<span class='at'>Delete Text Block "+$('#text-entry').val()+"</span>"
            }));
            var edit_button = $("<a/>", {
                class: 'pull-right',
                href: 'javascript:void(0)',
                onclick: 'updateText(' + data['pk'] + ');',
                title: 'Edit',
            });
            edit_button.prepend($('<i/>', {
                'style': 'color:navy',
                'class': 'pencil-icon',
            }));
            $new_item.prepend(edit_button);

            $page.append($new_item);
            $('#save_top').prop('disabled', false);
            $('#save_bot').prop('disabled', false);
        });
    }
}

function deleteItemHelper(){
    deleteItem($(this).parent());
}

function deleteItem($item) {
    var id = $item.attr('id');
    // if text
    if (id.match('^textblock')) {
        $.post(document.URL + '/' + id + '/delete', {csrftoken: csrftoken})
            .success(function () {
                $item.remove()
            });
    }
    // video or problem: put the item back into the appropriate list
    if (id.match('^video')) {
        $('#videos').append($item.remove());
    }
    // problem
    if (id.match('^problem')) {
        var list_id = id.match('[^-]*'); // match up to the dash
        $('#' + list_id).append($item.remove());
    }
    $item.toggleClass('uiselected');
    $uiselected = null;
    $('#save_top').prop('disabled', false);
    $('#save_bot').prop('disabled', false);
//    resize_problems();
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
        $('#save_bot').attr('disabled', 'disabled');
        $('#save_top').attr('disabled', 'disabled');
    });
}

function change_problem_visibility(){
    /**
     * Change the visibility of the problem and change the look of the button
     */

    var parent_id = $(this).parent('div').attr('id');
    var current_problem_type = parent_id.split("-")[0];
    var current_problem_pk = parent_id.split("-")[1];
    var this_button = this;
    var send_data = {problem_type:current_problem_type,
                     problem_pk:current_problem_pk,
                     csrftoken: csrftoken};
    $.post(document.URL + '/change_status', send_data)
        .success(function (data) {
            var new_visibility = data['new_visibility'];
            var old_visibility = data['old_visibility'];
            socket.emit('itemUpdate', {
                item: {
                        id: current_problem_type.replace('problems_', '')
                            + "-" + current_problem_pk,
                        problem_type: current_problem_type,
                        pk: current_problem_pk,
                        properties: {is_visible: new_visibility == 'open'}},
                secret_key: secret_key});

            if (old_visibility == 'open'){
                $(this_button).removeClass('visibility-open');
                $(this_button).addClass('visibility-'+new_visibility);
                $(this_button).find('.at').text(
                    $(this_button).parent().find('.searchable_content').text() +
                    " Visibility is " +
                    new_visibility);
            }
            else{
                $(this_button).removeClass('visibility-'+old_visibility);
                    $(this_button).addClass('visibility-'+new_visibility);
                    $(this_button).find('.at').text(
                        $(this_button).parent().find('.searchable_content').text() +
                        " Visibility is " +
                        new_visibility);
            }

            $(this_button).prop('title', "Visibility "+new_visibility);
        });
}
