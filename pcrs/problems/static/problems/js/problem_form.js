function ProblemFormHandler($form) {
    this.$form = $form;
}

/**
 * Should be called once the page loads.
 */
ProblemFormHandler.prototype.pageLoad = function() {
    this._setUpMultipleSelectFields();
}

// Make the tags section nice 'n' fancy
ProblemFormHandler.prototype._setUpMultipleSelectFields = function() {
    var that = this;

    $('#div_id_tags label').append(
        $('<a type="button"></a>')
            .attr('title', 'Test Suite Help')
            .attr('class', 'label-icon-button')
            .click(function() {
                that._showAddTagDialog();
            })
            .append('<i class="plus-sign-icon"></i>'));

    var searchBoxHtml = '<input type="text"' +
        'class="textInput textinput form-control" placeholder="Search" />';

    this.$form.find('.select-multiple-field').multiSelect({
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

ProblemFormHandler.prototype._showAddTagDialog = function() {
    var that = this;
    AlertModal.prompt('Create New Tag', function(value) {
        if (value) {
            that.createProblemTag(value);
        }
    });
}

ProblemFormHandler.prototype.createProblemTag = function(name) {
    var $selectMultipleField = this.$form.find('.select-multiple-field');
    $.ajax({
        // The 'root' variable is a global defined in base.html
        url:    root + "/content/tags/create",
        method: "POST",
        data: {
            'name': name,
        },
        dataType: 'json',
    }).success(function(data) {
        if ('validation_error' in data) {
            AlertModal.alert(
                'Tag Format Error',
                data['validation_error']['name']);
            return;
        }

        $selectMultipleField.multiSelect('addOption', {
            value: data['pk'],
            text: data['name'],
            index: 0,
        });
    });
}

/**
 * Override this if you want to call a custom ProblemFormHandler.
 *
 * This function exists so it can be overridden by various PCRS versions.
 */
var problemFormPageLoadCallback = function() {
    new ProblemFormHandler($('form')).pageLoad();
}

$(function() {
    problemFormPageLoadCallback();
});

/**
 * A callback for HTML generated in form.py.
 */
function showClearSubmissionsDialog(clearUrl) {
    AlertModal
        .clear()
        .setTitle('Clear submissions to this problem?')
        .setBody('All submissions to this problem will be removed.')
        .addFooterElement($('<button></button>')
            .attr('class', 'btn btn-danger pull-left')
            .attr('type', 'button')
            .text('Clear')
            .click(function() {
                clearSubmissionsForCurrentProblem(clearUrl);
            }))
        .addCancelButtonToFooter('right')
        .show();
}

function clearSubmissionsForCurrentProblem(clearUrl) {
    $.ajax({
        url:    clearUrl,
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

