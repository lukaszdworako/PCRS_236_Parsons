/**
 * A fancy tabbed code mirror widget.
 */
function TabbedCodeMirror() {
    this.isEditable = false;
    this.mirrors = [];
    this.$tabs = $('<ul class="nav nav-tabs tabbed-code-mirror"></ul>');
    this.$content = $('<div class="tab-content"></div>');
    // Used for the add-file-button widget
    this.newFileOptions = {};
}

TabbedCodeMirror._blockedLineClass = 'CodeMirror-activeline-background';

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
 *
 * @see setAddButtonCallback
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
    var name = prompt('Tab name:');
    if ( ! name) {
        return;
    }

    if ( ! name.match(/^[\._a-zA-Z0-9]+$/)) {
        alert('Please enter a name with only numbers' +
            ', letters, underscores, and periods.');
    } else if (this.indexForTabWithName(name) != -1) {
        alert('Tab with name "' + name + '" already exists.');
    } else {
        this.renameFileAtIndex(index, name);
    }
}

// Event callback to delete a tab
TabbedCodeMirror.prototype._attemptDeletingTab = function(index) {
    if (this.getFileCount() == 1) {
        alert('You cannot delete the last tab');
        return;
    }

    var confirmation = confirm('Are you sure you want to delete ' +
        this._tabTitleButtonAtIndex(index).text() + '?');
    if ( ! confirmation) {
        return;
    }

    // If we are deleting the current tab, switch away.
    if (index == this.getActiveTabIndex()) {
        this.setActiveTabIndex(index == 0 ? 1 : index - 1);
    }
    this.removeFileAtIndex(index);
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
 * @param {string} [options.block_ranges=[]] Lines to block the user from editing.
 * @param {string} [options.hash_ranges=[]] Lines to hash. See getHashedCode
 * @param {string} [options.readOnly=false]] If this file is read only.
 */
TabbedCodeMirror.prototype.addFile = function(options) {
    var that = this;
    var $tabButton = $('<a data-toggle="tab" href="#"></a>')
        .append(options.name);

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
    }
    if ('theme' in options) {
        codeMirrorOptions.theme = options.theme;
    }

    var mirror = CodeMirror(function(elt) {
        that.$content.append(elt);
    }, codeMirrorOptions);
    mirror.getWrapperElement().className += ' tab-pane';
    this.mirrors.push(mirror);

    if ('block_ranges' in options) {
        TabbedCodeMirror._blockLinesInMirror(mirror, options.block_ranges);
    }
    if ('hash_ranges' in options) {
        TabbedCodeMirror._hashLinesInMirror(mirror, options.hash_ranges);
    }

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
}

TabbedCodeMirror._blockLinesInMirror = function(mirror, ranges) {
    // Highlight the given ranges
    for (var i = 0; i < ranges.length; i++) {
        for (var j = ranges[i].start; j <= ranges[i].end; j++) {
            mirror.addLineClass(j - 1, '', TabbedCodeMirror._blockedLineClass);
        }
    }
    // Block the given ranges
    mirror.on('beforeChange', function(cm, change) {
        var start = Math.min(change.to.line, change.from.line);
        var end = Math.max(change.to.line, change.from.line);

        if (TabbedCodeMirror._rangeLiesInBlockedArea(mirror, start, end)) {
            change.cancel();
        }
    });
}

TabbedCodeMirror._hashLinesInMirror = function(mirror, ranges) {
    for (var i = 0; i < ranges.length; i++) {
        var start = ranges[i].start - 1;
        var end = ranges[i].end - 1;
        mirror.addLineClass(start, '', 'hash-start');
        mirror.addLineClass(end, '', 'hash-end');
    }
}

/**
 * Determines if a range intersects the target ranges.
 */
TabbedCodeMirror._rangeLiesInBlockedArea = function(mirror, start, end) {
    for (var i = start; i <= end; i++) {
        var wrapClass = mirror.lineInfo(i).wrapClass;
        if (wrapClass.indexOf(TabbedCodeMirror._blockedLineClass) > -1) {
            return true;
        }
    }
    return false;
}

/**
 * Removes the file at the given index.
 */
TabbedCodeMirror.prototype.removeFileAtIndex = function(index) {
    this.$tabs.find('li').eq(index).remove();
    this.$content.find('.CodeMirror').eq(index).remove();
    this.mirrors.splice(index, 1);
    this._showOrHideTabs();
}

/**
 * Changes the name of the file at the given index.
 */
TabbedCodeMirror.prototype.renameFileAtIndex = function(index, name) {
    this._tabTitleButtonAtIndex(index).text(name);
}

/**
 * Move a tab.
 *
 * @param {int} to The index to move from.
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
    this.$tabs.find('.active').removeClass('active');
    this.$content.find('.active').removeClass('active');

    this.$tabs.find('li').eq(index).addClass('active');
    this.$content.find('.CodeMirror').eq(index).addClass('active');

    this.mirrors[index].refresh();
}

/**
 * Hashes all of the code mirrors in order.
 * Hashes surround specified code for the server to parse.
 */
TabbedCodeMirror.prototype.getHashedCode = function(hash) {
    var code = '';
    for (var i = 0; i < this.mirrors.length; i++) {
        var mirror = this.mirrors[i];
        code += TabbedCodeMirror._getHashedCodeFromMirror(mirror, hash);

        if (i < this.mirrors.length - 1) {
            code += '\n';
        }
    }
    return code;
}

/**
 * Insert hash keys where the modifiable code starts and ends.
 */
TabbedCodeMirror._getHashedCodeFromMirror = function(mirror, hash) {
    var code = '';

    for (var i = 0; i < mirror.lineCount(); i++) {
        var wrapClass = mirror.lineInfo(i).wrapClass;
        // Blocked code
        if (wrapClass && wrapClass.indexOf(TabbedCodeMirror._blockedLineClass) > -1) {
            continue;
        }
        // The start of a hash segment
        if (wrapClass && wrapClass.indexOf('hash-start') > -1) {
            code += hash + '\n';
        }

        code += mirror.getLine(i) + '\n';

        // The end of a hash segment
        if (wrapClass && wrapClass.indexOf('hash-end') > -1) {
            code += hash + '\n';
        }
    }
    return code;
}

