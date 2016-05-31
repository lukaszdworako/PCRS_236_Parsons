// Make the tags section nice 'n' fancy
function setUpMultipleSelectFields() {
    var searchBoxHtml = '<input type="text"' +
        'class="textInput textinput form-control" placeholder="Search" />';

    $('.select-multiple-field').multiSelect({
        selectableHeader: searchBoxHtml,
        selectionHeader: '<h5>Selected</h5>',
        afterInit: function(ms) {
            var that = this;
            var $selectableSearch = that.$selectableUl.prev();
            var selectableSearchString = '#' + that.$container.attr('id') +
                ' .ms-elem-selectable:not(.ms-selected)';

            // TODO implement an "add" button
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

$(function() {
    // Must load after all the other JS, so we run at the end of the call stack
    setTimeout(setUpMultipleSelectFields, 0);
});

