/**
 * Extension which adds some metadata modification capabilities.
 *
 * Some of the features in this class:
 * - Add code tags (student code, blocked, and hidden)
 * - Display code from a student perspective, in a modal
 * - Highlight invalid code tags
 */
function AdminTabbedCodeMirror() {
    TabbedCodeMirror.call(this);
}
AdminTabbedCodeMirror.prototype = Object.create(TabbedCodeMirror.prototype);
AdminTabbedCodeMirror.prototype.constructor = AdminTabbedCodeMirror;

/**
 * @override
 */
AdminTabbedCodeMirror.prototype.getJQueryObject = function() {
    var $obj = TabbedCodeMirror.prototype.getJQueryObject.apply(this);
    var $buttons = this._createTagButtons();
    return $obj.add($buttons);
}

/**
 * @override
 */
AdminTabbedCodeMirror.prototype.addFile = function(options) {
    TabbedCodeMirror.prototype.addFile.apply(this, arguments);

    var mirror = this.mirrors[this.mirrors.length - 1];
    mirror.on('change', AdminTabbedCodeMirror._updateCodeHighLightOnMirror);
    AdminTabbedCodeMirror._updateCodeHighLightOnMirror(mirror);
}

/**
 * Creates buttons for various administrative code modifaction tasks.
 */
AdminTabbedCodeMirror.prototype._createTagButtons = function() {
    var btnTemplate = Handlebars.getTemplate('hb_icon_button');
    var that = this;
    return $('<br />')
        .add($(btnTemplate({
            type: 'primary',
            glyph: 'eye-open',
            text: 'Code Preview',
        })).click(function () {
            that._previewCode();
        }))
        .add($(btnTemplate({
            type: 'success',
            glyph: 'pencil',
            text: 'Student Code',
        })).click(function () {
            that._createTagAtCurrentSelection('student_code');
        }))
        .add($(btnTemplate({
            type: 'danger',
            glyph: 'ban-circle',
            text: 'Blocked',
        })).click(function () {
            that._createTagAtCurrentSelection('blocked');
        }))
        .add($(btnTemplate({
            type: 'danger',
            glyph: 'eye-close',
            text: 'Hidden',
        })).click(function () {
            that._createTagAtCurrentSelection('hidden');
        }))
}

/**
 * Displays a code preview, as the student would see the code.
 */
AdminTabbedCodeMirror.prototype._previewCode = function() {
    var previewTcm = new TabbedCodeMirror();
    previewTcm.setNewFileOptions($.extend({}, this.newFileOptions, {
        'readOnly': true,
    }));

    var files = this.getFiles();
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        previewTcm.addFile({
            'name': file.name,
            'code': this._cleanFileCodeForPreview(file.code),
        });
    }
    AlertModal.alert('Code Preview', previewTcm.getJQueryObject());
    previewTcm.refresh();
}

AdminTabbedCodeMirror.prototype._cleanFileCodeForPreview = function(code) {
    var code = TagManager.addStudentCodeTags(code);

    // The [\s\S] is another way to express "." with DOTALL enabled
    // Remove hidden portions
    code = code.replace(
        /\r?\n[ \t]*\[hidden\]\s*[\s\S]*\[\/hidden\][ \t]*/g, '');
    // Hide student_code and blocked tags
    code = code.replace(/\r?\n?\[\/?(student_code|blocked)\]/g, '');
    // The tag at the top of the file will leave a stray newline
    code = code.replace(/^[ \t]*\n/, '');

    return code;
}

/**
 * Create a new tag following some constraints (avoiding tags inside tags)
 */
AdminTabbedCodeMirror.prototype._createTagAtCurrentSelection =
        function(tagName) {
    var mirror = this.getCodeMirror(this.getActiveTabIndex());

    // Detect tags in the source code
    var code = mirror.getValue();
    var tagRanges = TagManager.findRangesWithTags(code);

    // The tail starts from index 0
    var start = mirror.getCursor(true).line + 1;
    // The head starts from index 0
    var end = mirror.getCursor(false).line + 1;

    for (var i = 0; i < tagRanges.length; i++) {
        if (start > tagRanges[i].end || end < tagRanges[i].start) {
            // The selection is outside of this tag.
            continue;
        }

        var title = 'Check your code selection!';
        var message = 'You Cannot include any other tag inside ' +
            'a hidden section, or along the same line.';
        AlertModal.alert(title, message);
        return;
    }

    extendMirrorSelectionAroundLines(mirror);
    // Add tag after verifications
    var selected_area = mirror.getSelection();

    mirror.replaceSelection(
        '[' + tagName + ']' + '\n' +
        selected_area + '\n'
        + '[/' + tagName + ']');
    // 'unselect' the tag area
    mirror.setCursor(mirror.getCursor());
}

// Callback to update invalid tag highlighting on a given mirror
AdminTabbedCodeMirror._updateCodeHighLightOnMirror = function(mirror) {
    // Check for tags to apply code highlighting
    var lineBegin = mirror.firstLine();
    var lineEnd = mirror.lastLine();

    var code_highlights = [];

    var openTagRegex = /^[ \t]*\[(hidden|blocked|student_code)\][ \t]*$/;
    var closeTagRegex = /^[ \t]*\[\/(hidden|blocked|student_code)\][ \t]*$/;
    for (var i = lineBegin; i <= lineEnd; i++) {
        var line = mirror.getLine(i);
        var match;

        if (match = openTagRegex.exec(line)) {
            var tagName = match[1];
            code_highlights.push(tagName);
        }

        if (code_highlights.length == 1) {
            // We are one level deep. So this is a valid code section
            mirror.removeLineClass(i);
        } else if (code_highlights.length > 1) {
            // We shouldn't be more that 1 level deep. Tag error!
            mirror.removeLineClass(i, '', 'CodeMirror-activeline-background');
            mirror.addLineClass(i, '', 'CodeMirror-error-background');
        } else if (code_highlights.length == 0) {
            // There are no code tags around this area - indicate so
            mirror.addLineClass(i, '', 'CodeMirror-activeline-background');
        }

        if (match = closeTagRegex.exec(line)) {
            var tagName = match[1];
            var matchedTag = code_highlights.pop();

            // Mismatching tag
            if (matchedTag != tagName) {
                mirror.removeLineClass(i, '',
                    'CodeMirror-activeline-background');
                mirror.addLineClass(i, '', 'CodeMirror-error-background');
            }
        }
    }

    // Some tag didn't end properly
    if (code_highlights.length != 0) {
        mirror.removeLineClass(lineEnd, '', 'CodeMirror-activeline-background');
        mirror.addLineClass(lineEnd, '', 'CodeMirror-error-background');
    }
}

