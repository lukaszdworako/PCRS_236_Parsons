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
    AlertModal.prompt('Create New Tag', function(value) {
        if (value) {
            createProblemTag(value);
        }
    });
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
            AlertModal.alert(
                'Tag Format Error',
                data['validation_error']['name']);
            return;
        }

        $('.select-multiple-field').multiSelect('addOption', {
            value: data['pk'],
            text: data['name'],
            index: 0,
        });
    });
}

function showClearSubmissionsDialog() {
    AlertModal
        .clear()
        .setTitle('Clear submissions to this problem?')
        .setBody('All submissions to this problem will be removed.')
        .addFooterElement($('<button class="btn btn-danger pull-left"></button>')
            .attr('type', 'button')
            .text('Clear')
            .click(function() {
                clearSubmissionsForCurrentProblem();
            }))
        .addCancelButtonToFooter('right')
        .show();
}

function clearSubmissionsForCurrentProblem() {
    $.ajax({
        url:    "{{ object.get_absolute_url }}/clear",
        method: "POST",
    }).success(function(data) {
        // Clear errors on the page.
        $('.has-error').removeClass('has-error');
        // Remove error help blocks
        var helpBlocks = $('.help-block');
        for (var i = 0; i < helpBlocks.length; i++) {
            var block = $(helpBlocks[i]);
            if (block.attr('id').indexOf('error') > -1) {
                block.remove();
            }
        }
        AlertModal.hide();
    });
}

$(function() {
    // Must load after all the other JS, so we run at the end of the call stack
    setTimeout(setUpMultipleSelectFields, 0);
});

