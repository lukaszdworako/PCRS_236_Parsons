/**
 * A fancy tabbed code mirror widget.
 */
function TabbedCodeMirror() {
    this.mirrors = [];
    this.$tabs = $('<ul id="code-tabs" class="nav nav-tabs"></ul>');
    this.$content = $('<div id="code-tab-content" class="tab-content"></div>');
}

TabbedCodeMirror._blockedLineClass = 'CodeMirror-activeline-background';

/**
 * Gets the file names and raw contents.
 */
TabbedCodeMirror.prototype.getFiles = function() {
    var files = [];
    for (var i = 0; i < this.mirrors.length; i++) {
        files.push({
            'name': this.$tabs.find('a').eq(i).text(),
            'code': this.mirrors[i].getValue(),
        });
    }
    return files;
}

/**
 * Adds a file to the end of the file list.
 *
 * @param {Object} options Options for this file tab.
 * @param {string} options.name The name of the file.
 * @param {string} options.code The content of the file.
 * @param {string} options.mode The CodeMirror mode.
 * @param {string} [options.theme=undefined] CodeMirror theme name.
 * @param {string} [options.blocked_lines=[]] Lines to block the user from editing.
 * @param {string} [options.readOnly=false]] If this file is read only.
 */
TabbedCodeMirror.prototype.addFile = function(options) {
    var that = this;
    var $tabButton = $('<a data-toggle="tab" href="#"></a>')
        .append(options.name);
    this.$tabs.append($('<li></li>').append($tabButton));

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

    if ('blocked_lines' in options) {
        TabbedCodeMirror._blockLinesInMirror(mirror, options.blocked_lines);
    }

    // Refresh code mirrors when switching tabs to prevent UI glitches
    $tabButton.click(function(e) {
        e.preventDefault();
        that.setActiveTabIndex($(this).parent().index());
    });
    this._showOrHideTabs();
}

TabbedCodeMirror._blockLinesInMirror = function(mirror, ranges) {
    // Highlight the given ranges
    for (var i = 0; i < ranges.length; i++) {
        for (var j = ranges[i].start; j <= ranges[i].end; j++) {
            mirror.addLineClass(j - 1, '', 'CodeMirror-activeline-background');
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

/**
 * Determines if a range intersects the target ranges.
 */
TabbedCodeMirror._rangeLiesInBlockedArea = function(mirror, start, end) {
    for (var i = start; i <= end; i++) {
        var wrapClass = mirror.lineInfo(i).wrapClass;
        if (wrapClass == 'CodeMirror-activeline-background') {
            return true;
        }
    }
    return false;
}

/**
 * Removes the file at the given index.
 */
TabbedCodeMirror.prototype.removeFileAtIndex = function(index) {
    this.$tabs.children().get(index).remove();
    this.$content.get(index).remove();
    this.mirrors.splice(index, 1);
    this._showOrHideTabs();
}

/**
 * Changes the name of the file at the given index.
 */
TabbedCodeMirror.prototype.renameFileAtIndex = function(index, name) {
    this.$tabs.find('a').eq(index).text(name);
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

TabbedCodeMirror.prototype._showOrHideTabs = function() {
    if (this.mirrors.length <= 1) {
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
 * Hashes surround modifiable code for the server to parse.
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
    var inside_student_code = false;

    for (var i = 0; i < mirror.lineCount(); i++){
        var wrapClass = mirror.lineInfo(i).wrapClass;

        if (wrapClass == 'CodeMirror-activeline-background') {
            if (inside_student_code) {
                code += hash + '\n';
                inside_student_code = false;
            }
        } else {
            if ( ! inside_student_code) {
                code += hash + '\n';
                inside_student_code = true;
            }
        }

        code += mirror.getLine(i);
        code += '\n';
    }
    code += hash;
    return code;
}

