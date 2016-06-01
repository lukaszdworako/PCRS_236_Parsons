// The 'root' variable is defined in base.html

// Make the tags section nice 'n' fancy
function setUpMultipleSelectFields() {
    var tagsSelectField = $('.select-multiple-field');

    tagsSelectField.after('<a class="btn btn btn-success" role="button" onclick="showAddTagDialog()">' +
        '<span class="glyphicon glyphicon-plus"></span>   Add</a>');
    tagsSelectField.after('<br />');

    var searchBoxHtml = '<input type="text"' +
        'class="textInput textinput form-control" placeholder="Search" />';

    tagsSelectField.multiSelect({
        selectableHeader: searchBoxHtml,
        selectionHeader: '<h5>Selected</h5>',
        afterInit: function(ms) {
            var that = this;
            var $selectableSearch = that.$selectableUl.prev();
            var selectableSearchString = '#' + that.$container.attr('id') +
                ' .ms-elem-selectable:not(.ms-selected)';

            that.qs = $selectableSearch.quicksearch(selectableSearchString)
                .on('keydown', function(e) {
                    var isDownArrowOrTab = e.which === 40 || e.which == 9;
                    if (isDownArrowOrTab) {
                        that.$selectableUl.focus();
                        return false;
                    }
                });
        },
        afterSelect: function() {
            this.qs.cache();
        },
        afterDeselect: function() {
            this.qs.cache();
        },
    });
}

function showAddTagDialog() {
    createProblemTag(prompt('Tag name: '));
}

function createProblemTag(name) {
    $.ajax({
        url:    root + "/content/tags/create",
        method: "POST",
        data: {
            'name': name,
        },
    }).success(function(data) {
        if ('validation_error' in data) {
            alert(data['validation_error']['name']);
            return;
        }

        $('.select-multiple-field').multiSelect('addOption', {
            value: data['pk'],
            text: data['name'],
            index: 0,
        });
    });
}

$(function() {
    // Must load after all the other JS, so we run at the end of the call stack
    setTimeout(setUpMultipleSelectFields, 0);
});

