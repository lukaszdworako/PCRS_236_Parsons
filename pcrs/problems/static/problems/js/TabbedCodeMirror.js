/**
 * A fancy tabbed code mirror widget.
 */
function TabbedCodeMirror() {
    this.isEditable = false; // Are tabs editable, that is.
    this.mirrors = [];
    this.$tabs = $('<ul class="nav nav-tabs tabbed-code-mirror"></ul>');
    this.$content = $('<div class="tab-content"></div>');
    // Used for the add-file-button widget
    this.newFileOptions = {};
    this._forcedFileExtension = '';
    this._codeIsClean = true;
}

/**
 * Checks if any file has been created, deleted, renamed, moved, or editted.
 *
 * @return {bool} True if any code has been changed, moved, etc.
 */
TabbedCodeMirror.prototype.isClean = function() {
    if ( ! this._codeIsClean) {
        return false;
    }
    for (var i = 0; i < this.mirrors.length; i++) {
        if ( ! this.mirrors[i].isClean()) {
            return false;
        }
    }
    return true;
}

/**
 * Set the content as 'clean'.
 * @see isClean
 */
TabbedCodeMirror.prototype.markClean = function() {
    this._codeIsClean = true;

    for (var i = 0; i < this.mirrors.length; i++) {
        this.mirrors[i].markClean();
    }
}

/**
 * Get the jQuery representation of the TabbedCodeMirror
 */
TabbedCodeMirror.prototype.getJQueryObject = function() {
    return this.$tabs.add(this.$content);
}

/**
 * Refresh the active code mirror.
 */
TabbedCodeMirror.prototype.refresh = function() {
    this.mirrors[this.getActiveTabIndex()].refresh();
}

/**
 * Adds a set of edit widgets.
 *
 * After calling this, widgets for deleting, inserting, moving,
 * and renaming tabs will appear.
 */
TabbedCodeMirror.prototype.enableTabEditingWidgets = function() {
    if (this.isEditable) {
        return;
    }
    this.isEditable = true;

    for (var i = 0; i < this.mirrors.length; i++) {
        this._addEditWidgetsToTab(i);
    }

    this.$tabs.append(this._createAddFileTab());
    this._showOrHideTabs();

    var that = this;
    this.$tabs.sortable({
        axis: 'x',
        items: '> :not(:last)', // not the 'add' button
        start: function(event, ui) {
            var startPosition = ui.item.index();
            ui.item.data('startPosition', startPosition);
        },
        stop: function(event, ui) {
            var startPosition = ui.item.data('startPosition');
            var endPosition = ui.item.index();
            // Cancel because we swap the tabs manually
            $(this).sortable('cancel');
            that.moveTab(startPosition, endPosition);
        },
    });
}

/**
 * Sets the default options for creating new files.
 *
 * This is needed when this isEditable is set.
 *
 * @param {Object} options The options to pass to addFile by default.
 * @see enableTabEditingWidgets
 */
TabbedCodeMirror.prototype.setNewFileOptions = function(options) {
    this.newFileOptions = options;
}

/**
 * Forces files to have the given extension when renaming.
 *
 * @param {string} ext The extension to force, or a blank string to unset.
 */
TabbedCodeMirror.prototype.setForcedFileExtension = function(ext) {
    this._forcedFileExtension = ext;
}

// Adds edit widgets (the drop down menu)
TabbedCodeMirror.prototype._addEditWidgetsToTab = function(index) {
    var $tab = this.$tabs.find('li').eq(index);
    var $tabButton = $tab.find('a').first();
    $tabButton.addClass("tab-dropdown-title");

    var $dropSection = $('<div href="#" class="dropdown"></div>')
        .append($('<a href="#"></a>')
            .attr('data-toggle', 'dropdown')
            .append('<b class="caret"></b>'));
    var $dropDownMenu = this._createDropDownMenu();

    $dropSection.append($dropDownMenu);
    $tab.append($dropSection);
}

TabbedCodeMirror.prototype._createDropDownMenu = function() {
    var $dropDownMenu = $('<div class="dropdown-menu"></div>');

    var that = this;
    $dropDownMenu.append($('<a class="dropdown-item" type="a"></a>')
        .text('Rename')
        .click(function() {
            var index = $(this).closest('li').index();
            that._attemptRenamingTab(index);
        }));
    $dropDownMenu.append($('<a class="dropdown-item" type="a"></a>')
        .text('Delete')
        .click(function() {
            var index = $(this).closest('li').index();
            that._attemptDeletingTab(index);
        }));
    $dropDownMenu.append($('<a class="dropdown-item" type="a"></a>')
        .text('Move Left')
        .click(function() {
            var index = $(this).closest('li').index();
            if (index > 0) {
                that.moveTab(index, index - 1);
            }
        }));
    $dropDownMenu.append($('<a class="dropdown-item" type="a"></a>')
        .text('Move Right')
        .click(function() {
            var index = $(this).closest('li').index();
            if (index < that.getFileCount() - 1) {
                that.moveTab(index, index + 1);
            }
        }));

    return $dropDownMenu;
}

TabbedCodeMirror.prototype._createAddFileTab = function() {
    var that = this;
    var $addButton = $('<a href="#" class="add-file-button"></a>')
        .append($('<span class="glyphicon glyphicon-plus"></span>'))
        .click(function() {
            var options = $.extend({}, that.newFileOptions); // copy

            // Ensure the name is unique
            var i = 1;
            while (that.indexForTabWithName(options.name) != -1) {
                options.name = i + '_' + that.newFileOptions.name;
                i++;
            }

            that.addFile(options);
            that._codeIsClean = false;
            that.setActiveTabIndex(that.getFileCount() - 1);
            return false;
        });
    return $('<li></li>').append($addButton);
}

/**
 * Finds the index of the tab with the given name.
 *
 * @param name {string} The name of the tab
 * @return {number} Index of the tab, or -1 if not found.
 */
TabbedCodeMirror.prototype.indexForTabWithName = function(name) {
    for (var i = 0; i < this.mirrors.length; i++) {
        var tabTitle = this._tabTitleButtonAtIndex(i).text();
        if (tabTitle == name) {
            return i;
        }
    }
    return -1;
}

// Event callback to rename a tab
TabbedCodeMirror.prototype._attemptRenamingTab = function(index) {
    var that = this;
    AlertModal.prompt('File Name:', function(value) {
        if ( ! value) {
            return;
        }
        var err = that._validateTabName(value);
        if (err) {
            AlertModal.alert('Invalid File Name', err);
            return;
        }
        value = that._addFileExtensionForFileName(value);
        that.renameFileAtIndex(index, value);
    });
}

/*
 * Possibly adds a file extension to the given value.
 *
 * The extension is provided in the newFileOptions.
 * If the extension is provided, this does nothing.
 * @param {string} value The file name to add an extension to.
 * @return The file name with an extension.
 */
TabbedCodeMirror.prototype._addFileExtensionForFileName = function(value) {
    var extension = this._forcedFileExtension;
    if ( ! extension) {
        return value;
    }
    return value.endsWith('.' + extension)
        ? value
        : value + '.' + extension;
}

// Returns a string when a validation error occured. Otherwise null.
TabbedCodeMirror.prototype._validateTabName = function(value) {
    if ( ! value.match(/^[\._a-zA-Z0-9]+$/)) {
        return 'Please enter a name with only numbers' +
            ', letters, underscores, and periods.';
    } else if (this.indexForTabWithName(value) != -1) {
        return 'Tab with name "' + value + '" already exists.';
    }
    return false;
}

// Event callback to delete a tab
TabbedCodeMirror.prototype._attemptDeletingTab = function(index) {
    if (this.getFileCount() == 1) {
        AlertModal.alert('', 'You cannot delete the last tab');
        return;
    }

    var that = this;
    AlertModal
        .clear()
        .setTitle('Are you sure you want to delete ' +
            this._tabTitleButtonAtIndex(index).text() + '?')
        .setBody('This file will be permenantly deleted.')
        .addFooterElement($('<button class="btn btn-danger pull-left"></button>')
            .attr('type', 'button')
            .text('Delete')
            .click(function() {
                // If we are deleting the current tab, switch away.
                if (index == that.getActiveTabIndex()) {
                    that.setActiveTabIndex(index == 0 ? 1 : index - 1);
                }
                that.removeFileAtIndex(index);
                AlertModal.hide();
            }))
        .addCancelButtonToFooter('right')
        .show();
}

/**
 * Gets the file names and raw contents.
 */
TabbedCodeMirror.prototype.getFiles = function() {
    var files = [];
    for (var i = 0; i < this.mirrors.length; i++) {
        files.push({
            'name': this._tabTitleButtonAtIndex(i).text(),
            'code': this.mirrors[i].getValue(),
        });
    }
    return files;
}

TabbedCodeMirror.prototype._tabTitleButtonAtIndex = function(index) {
    var $tab = this.$tabs.find('li').eq(index);
    return $tab.find('a').first();
}

/**
 * Adds a file to the end of the file list.
 *
 * @param {Object} options Options for this file tab.
 * @param {string} options.name The name of the file.
 * @param {string} options.code The content of the file.
 * @param {string} options.mode The CodeMirror mode.
 * @param {string} [options.theme=undefined] CodeMirror theme name.
 * @param {string} [options.readOnly=false]] If this file is read only.
 */
TabbedCodeMirror.prototype.addFile = function(options) {
    options = $.extend({}, this.newFileOptions, options);

    var that = this;
    var $tabButton = $('<a data-toggle="tab" href="#"></a>')
        .append(options.name);

    var codeMirrorOptions = this._createCodeMirrorOptions(options);

    var mirror = CodeMirror(function(elt) {
        that.$content.append(elt);
    }, codeMirrorOptions);

    mirror.getWrapperElement().className += ' tab-pane';
    this.mirrors.push(mirror);

    // Refresh code mirrors when switching tabs to prevent UI glitches
    $tabButton.click(function(e) {
        e.preventDefault();
        that.setActiveTabIndex($(this).parent().index());
    });

    var $listButton = $('<li></li>').append($tabButton);
    if (this.isEditable) {
        var addButton = this.$tabs.find('li').last();
        addButton.before($listButton);
        this._addEditWidgetsToTab($tabButton.parent().index());
    } else {
        this.$tabs.append($listButton);
    }
    this._showOrHideTabs();

    // Ensure at least one tab is selected
    if (this.getActiveTabIndex() == -1) {
        this.setActiveTabIndex(0);
    }
}

/**
 * Adds a collection of files to this tcm.
 *
 * @param {array} files The files to add.
 * @see addFile
 */
TabbedCodeMirror.prototype.addFiles = function(files) {
    for (var i = 0; i < files.length; i++) {
        this.addFile(files[i]);
    }
}

/**
 * Creates the options for new CodeMirror instances.
 *
 * @param {Object} options The TCM options.
 * @see addFile(options)
 */
TabbedCodeMirror.prototype._createCodeMirrorOptions = function(options) {
    var codeMirrorOptions = {
        mode: options.mode,
        value: options.code,
        lineNumbers: 'True',
        indentUnit: 4,
        lineWrapping: 'True',
        flattenSpans: 'False',
    };
    if ('readOnly' in options) {
        codeMirrorOptions.readOnly = options.readOnly;
        if (options.readOnly) {
            // Hide the cursor
            codeMirrorOptions.cursorHeight = 0;
        }
    }
    if ('theme' in options) {
        codeMirrorOptions.theme = options.theme;
    }
    return codeMirrorOptions;
}

/**
 * Removes the file at the given index.
 */
TabbedCodeMirror.prototype.removeFileAtIndex = function(index) {
    this.$tabs.find('li').eq(index).remove();
    this.$content.find('.CodeMirror').eq(index).remove();
    this.mirrors.splice(index, 1);
    this._showOrHideTabs();
    this._codeIsClean = false;
}

/**
 * Changes the name of the file at the given index.
 */
TabbedCodeMirror.prototype.renameFileAtIndex = function(index, name) {
    this._tabTitleButtonAtIndex(index).text(name);
    this._codeIsClean = false;
}

/**
 * Move a tab.
 *
 * @param {int} from The index to move from.
 * @param {int} to The index to move to.
 */
TabbedCodeMirror.prototype.moveTab = function(from, to) {
    // Bad stuff happens if incorrect indeces are given.
    if (Math.max(from, to) >= this.mirrors.length || Math.min(from, to) < 0) {
        throw new Error('Cannot move tab ' + from + ' to index ' + to);
    }

    var liTabs = this.$tabs.find('li');
    var fromTab = liTabs.eq(from);
    var toTab = liTabs.eq(to);

    var contentDivs = this.$content.find('.CodeMirror');
    var fromDiv = contentDivs.eq(from);
    var toDiv = contentDivs.eq(to);

    if (from <= to) {
        fromTab.insertAfter(toTab);
        fromDiv.insertAfter(toDiv);
    } else {
        fromTab.insertBefore(toTab);
        fromDiv.insertBefore(toDiv);
    }

    var mirror = this.mirrors.splice(from, 1)[0];
    this.mirrors.splice(to, 0, mirror);
    this._codeIsClean = false;
}

/**
 * Retrieves the CodeMirror object at the given tab index.
 */
TabbedCodeMirror.prototype.getCodeMirror = function(index) {
    return this.mirrors[index];
}

TabbedCodeMirror.prototype.getFileCount = function(index) {
    return this.mirrors.length;
}

TabbedCodeMirror.prototype._showOrHideTabs = function() {
    if ( ! this.isEditable && this.mirrors.length <= 1) {
        this.$tabs.hide();
    } else {
        this.$tabs.show();
    }
}

/**
 * Retrieve the active tab index, or -1 if none are active.
 */
TabbedCodeMirror.prototype.getActiveTabIndex = function() {
    return this.$tabs.find('.active').index();
}

/**
 * Switch to the tab at the given index.
 */
TabbedCodeMirror.prototype.setActiveTabIndex = function(index) {
    if (index < 0 || index >= this.mirrors.length) {
        throw new Error('index ' + index +
            ' is out of range [0,' + this.mirrors.length + ']')
    }

    this.$tabs.find('.active').removeClass('active');
    this.$content.find('.active').removeClass('active');

    this.$tabs.find('li').eq(index).addClass('active');
    this.$content.find('.CodeMirror').eq(index).addClass('active');

    this.mirrors[index].refresh();
}

