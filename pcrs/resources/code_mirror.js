function create_to_code_mirror (language, version, location){
    hcm = to_code_mirror(language, version, $('#'+location), $('#'+location).text(), true);
    if (!(location in cmh_list)){
        cmh_list[location] = hcm;
    }
}

function cmModeForLanguageAndVersion(language, version) {
    if (language == 'python') {
        return {
            name: language,
            version: version,
            singleLineStringErrors: false
        }
    } else if (language == 'sql'){
        return 'text/x-plsql';
    } else if (language == 'ra'){
        return 'text/ra';
    } else if (language == 'c'){
        return 'text/x-csrc';
    } else if (language == 'java'){
        return 'text/x-java';
    }
}

/**
 * Replaced a div with a code mirror div.
 *
 * @param language The programming language to use.
 * @param version The programming language version
 * @param location A jQuery object to emplace on top of
 * @param value The code to initially set - file tags included
 * @param lock Should the code be locked, or modifiable?
 */
function to_tabbed_code_mirror(language, version, location, value, lock) {
    var tcm = new TabbedCodeMirror();

    location.before(tcm.getJQueryObject());
    location.remove();

    var files = TagManager.parseCodeIntoFiles(value);

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        tcm.addFile({
            'name': file.name,
            'code': file.code,
            'mode': cmModeForLanguageAndVersion(language, language_version),
            'theme': user_theme,
        });
    }
    tcm.setActiveTabIndex(0);

    return tcm;
}

function to_code_mirror (language, version, location, value, lock) {
    historyCodeMirror = CodeMirror(
        function(elt) {
            $(location).replaceWith(elt);
        }, {
            mode: cmModeForLanguageAndVersion(language, version),
            //themes can be found in codemirror4.1/theme; must be loaded in submission.html
            theme: user_theme,
            value: value,
            lineNumbers: 'True',
            indentUnit: 4,
            readOnly: lock,
            lineWrapping: 'True',
            flattenSpans: 'False'
        });
    return historyCodeMirror;
}

/**
 * For every line of code inside a pair of [block] [/block] tags,
 * highlight this code with a different background color
 */
function highlightCodeMirrorWithTags(mirror, tag_list) {
    // Block input in the highlighted area
    mirror.on("cursorActivity", function() {
        blockInput(mirror);
    });

    // Check for tags to apply code highlighting
    var first_line = mirror.firstLine();
    var last_line = mirror.lastLine();
    for (var i = first_line; i <= last_line; i++) {
        for (var j = 0; j < tag_list.length; j++) {
            if (tag_list[j].start <= i+1 && tag_list[j].end >= i+1) {
                mirror.addLineClass(i, '', 'CodeMirror-activeline-background');
                break;
            }
        }
    }
}

function preventDeleteLastLine(mirror) {
    mirror.getSelectedLines = function () {
        var selected_lines = [];

        if (mirror.somethingSelected()) {
            var start_line = mirror.getCursor(true).line;
            var end_line = mirror.getCursor(false).line;
            for(var i = start_line; i <= end_line; i++) {
                selected_lines.push(mirror.lineInfo(i));
            }
        }

        return selected_lines;
    }

    mirror.setOption("extraKeys", {
        "Backspace": guardBackspace,
        "Delete": guardDelete,
    });

    mirror.setOption("lineWrapping", true);
}

function guardBackspace(editor) {
    var curLine = editor.getCursor().line;
    var curLineChar = editor.getCursor().ch;

    var prevLine = (curLine > 0) ? curLine - 1 : 0;

    var isSelection = editor.somethingSelected();
    var blockedCodeSelected = isSelection && editor.getSelectedLines().filter(function(line) {
        return line.wrapClass == 'CodeMirror-activeline-background';
    }).length > 0;

    var curLineEmpty = editor.lineInfo(curLine).text.length == 0;
    var curLineFirstChar = curLineChar == 0;
    var prevLineWrapClass = editor.lineInfo(prevLine).wrapClass;

    // Allow deleting selections, characters on the same line and previous unblocked lines
    if ((!blockedCodeSelected)
        && ((!curLineEmpty && !curLineFirstChar)
            || (prevLineWrapClass != 'CodeMirror-activeline-background'))) {

        // Resume default behaviour
        return CodeMirror.Pass;
    }
}

function guardDelete(editor) {
    var curLine = editor.getCursor().line;
    var curLineLen = editor.lineInfo(curLine).text.length;
    var curLineChar = editor.getCursor().ch;

    var lastLine = editor.lineCount() - 1;
    var nextLine = (curLine < lastLine) ? curLine + 1 : lastLine;

    var isSelection = editor.somethingSelected();
    var blockedCodeSelected = isSelection && editor.getSelectedLines().filter(function(line) {
        return line.wrapClass == 'CodeMirror-activeline-background';
    }).length > 0;

    var curLineEmpty = curLineLen == 0;
    var curLineLastChar = curLineChar == curLineLen;
    var nextLineWrapClass = editor.lineInfo(nextLine).wrapClass;

    // Allow deleting selections, characters on the same line and following unblocked lines
    if ((!blockedCodeSelected)
        && ((!curLineEmpty && !curLineLastChar)
            || (nextLineWrapClass != 'CodeMirror-activeline-background'))) {

        // Resume default behaviour
        return CodeMirror.Pass;
    }
}

/**
 * For every line of code inside a pair of [block] [/block] tags,
 * the user is unable to clicks over it (modify the code)
 */
function blockInput(mirror) {
    var line_num = mirror.getCursor().line;
    var line_count;
    var wrapClass = mirror.lineInfo(line_num).wrapClass;

    if (wrapClass == 'CodeMirror-activeline-background') {
        line_count = mirror.lineCount();
        for (var i = 0; i < line_count; i++){
            wrapClass = mirorr.lineInfo(i).wrapClass;
            if (wrapClass != 'CodeMirror-activeline-background'){
                mirror.setCursor(i, 0);
                return true;
            }
        }
        mirror.replaceRange("\n", CodeMirror.Pos(mirror.lastLine()));
        mirror.setCursor(mirror.lineCount(), 0);
    }
}

/**
 * Extends the selection of a given code mirror to wrap entire lines.
 *
 * For instance, if part of one line is selected, it will
 * select that entire line. If part of multiple lines are
 * selected, it will wrap around them all.
 */
function extendMirrorSelectionAroundLines(mirror) {
    var head = mirror.getCursor('head');
    var anchor = mirror.getCursor('anchor');

    if (anchor.line >= head.line) {
        head.ch = 0;
        anchor.ch = mirror.getDoc().getLine(anchor.line).length;
    } else {
        head.ch = mirror.getDoc().getLine(head.line).length;
        anchor.ch = 0;
    }

    mirror.setSelection(anchor, head);
}

