/**
 * A fancy tabbed code mirror widget.
 */
function TabbedCodeMirror() {
    this.mirrors = [];
    this.$tabs = $('<ul id="code-tabs" class="nav nav-tabs"></ul>');
    this.$content = $('<div id="code-tab-content" class="tab-content"></div>');
}

TabbedCodeMirror._blockedLineClass = 'CodeMirror-activeline-background';

// Used to generate unique dom IDs for the code mirrors - needed for tabbing
TabbedCodeMirror._mirrorDomCounter = 0;
TabbedCodeMirror._generateDomId = function() {
    return '#tabbed-code-mirror-' + (TabbedCodeMirror._mirrorDomCounter++);
}

/**
 * Adds a file to the end of the file list.
 *
 * @param {Object} options Options for this file tab.
 * @param {string} options.name The name of the file.
 * @param {string} options.code The content of the file.
 * @param {string} options.mode The CodeMirror mode.
 * @param {string} [options.blocked_lines=[]] Lines to block the user from editing.
 * @param {string} [options.readOnly=false]] If this file is read only.
 */
TabbedCodeMirror.prototype.addFile = function(options) {
    var that = this;
    var tabIndex = this.$tabs.length;
    var contentId = TabbedCodeMirror._generateDomId();
    var $tabButton = $('<a data-toggle="tab"></a>')
        .attr('href', contentId)
        .append(options.name);
    this.$tabs.append($('<li></li>').append($tabButton));

    var mirror = CodeMirror(function(elt) {
        that.$content.append(elt);
    }, {
        mode: options.mode,
        value: options.code,
        lineNumbers: 'True',
        indentUnit: 4,
        readOnly: 'readOnly' in options ? options.readOnly : false,
        lineWrapping: 'True',
        flattenSpans: 'False',
    });
    mirror.getWrapperElement().id = contentId;
    mirror.getWrapperElement().className += ' tab-pane';
    this.mirrors.append(mirror);

    if ('blocked_lines' in options) {
        TabbedCodeMirror._blockLinesInMirror(mirror, options.blocked_lines);
    }

    // Refresh code mirrors when switching tabs to prevent UI glitches
    $tabButton.click(function(e) {
        e.preventDefault();
        $(this).tab('show');
        mirror.refresh();
    });
    this._showOrHideTabs();
}

TabbedCodeMirror._blockLinesInMirror = function(mirror, ranges) {
    // Highlight the given ranges
    for (var i = 0; i < ranges.length; i++) {
        for (var j = ranges[i].start; j <= ranges[i].end; j++) {
            var line = j + 1;
            mirror.addLineClass(line, '', 'CodeMirror-activeline-background');
        }
    }
    // Block the given ranges
    mirror.on('beforeChange', function(cm, change) {
        var start = Math.min(change.to, change.from);
        var end = Math.max(change.to, change.from);

        if (TabbedCodeMirror._rangeLiesInBlockedArea(mirror, start, end)) {
            change.cancel();
        }
    });
}

/**
 * Determines if a range intersects the target ranges.
 */
TabbedCodeMirror._rangeLiesInBlockedArea = function(mirror, start, end) {
    for (var i = mirror.firstLine(); i < mirror.lastLine(); i++) {
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
    this.$tabs.get(index).remove();
    this.$content.get(index).remove();
    this.mirrors.splice(index, 1);
    this._showOrHideTabs();
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
    for (var i = 0; i < this.$tabs.length; i++) {
        if (this.$tabs.get(i).hasClass('active')) {
            return i;
        }
    }
    return -1;
}

/**
 * Switch to the tab at the given index.
 */
TabbedCodeMirror.prototype.setActiveTabIndex = function(index) {
    this.$tabs.get(index).addClass('active');
    this.$content.get(index).addClass('active');
}

/**
 * Hashes all of the code mirrors in order.
 * Hashes surround student code for the server to parse.
 */
TabbedCodeMirror.prototype.getHashedCode = function(hash) {
    var code = '';
    for (var i = 0; i < this.mirrors.length; i++) {
        var mirror = this.mirrors[i];
        code += TabbedCodeMirror.getHashedCodeFromMirror(mirror, hash);
    }
    return code;
}

/**
 * Insert hash keys where the student code starts and ends.
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

