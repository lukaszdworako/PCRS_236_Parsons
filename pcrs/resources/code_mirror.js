function create_to_code_mirror (language, version, location){
    hcm = to_code_mirror(language, version, $('#'+location), $('#'+location).text(), true);
    if (!(location in cmh_list)){
        cmh_list[location] = hcm;
    }
}

function to_code_mirror (language, version, location, value, lock){

    var mode;
    if (language == 'python'){
        mode = {name: language,
                version: version,
                singleLineStringErrors: false}
    }
    else if (language == 'sql'){
        mode = 'text/x-plsql';
    }
    else if (language == 'ra'){
        mode = 'text/ra';
    }
    else if (language == 'c'){
        mode = 'text/x-csrc';
    }
    else if (language == 'java'){
        mode = 'text/x-java';
    }
    historyCodeMirror = CodeMirror(function(elt) {
        $(location).replaceWith(elt);
        }, {mode: mode,
          //themes can be found in codemirror4.1/theme; must be loaded in submission.html
            theme: user_theme,
            value: value,
            lineNumbers: 'True',
            indentUnit: 4,
            readOnly: lock,
            lineWrapping: 'True',
            flattenSpans: 'False'});


    return historyCodeMirror;
}

/**
 * Turns a div with code into a set of code mirrors with tabs.
 *
 * @param codeDiv The div with code tags included to replace.
 * @param languageAndProblemId
 * @return {Object} A hash of code mirrors
 */
function createTabbedCodeMirrorsFromCodeDiv(codeDiv, languageAndProblemId) {
    var newCodeMirrors = {};

    var codeText = codeDiv.text();
    var defaultName = 'StudentCode.java';
    var files = TagManager.parseCodeIntoFiles(codeText);

    codeDiv.replaceWith('<ul id="code-tabs" class="nav nav-tabs"></ul>' +
        '<div id="code-tab-content" class="tab-content"></div>');

    var codeTabs = $('#code-tabs');
    var codeTabContent = $('#code-tab-content');

    // Create a code mirror for each file.
    for (var i = 0; i < files.length; i++) {
        var name = files[i]['name'];
        var codeObj = removeTags(files[i]['code']);
        var codeMirrorId = languageAndProblemId + '-' + i;

        codeTabs.append('<li><a data-toggle="tab" ' +
            'href="#' + codeMirrorId + '">' + name + '</a></li>');

        codeTabContent.append('<div id="code_mirror_replacement"></div>');
        var codeMirrorReplacement = $('#code_mirror_replacement');

        var codeMirror = to_code_mirror(
            language, 'text/x-java', codeMirrorReplacement,
            codeObj.source_code, false);

        codeMirror.getWrapperElement().id = codeMirrorId;
        codeMirror.getWrapperElement().className += ' tab-pane';
        newCodeMirrors[codeMirrorId] = codeMirror;

        highlightCodeMirrorWithTags(codeMirror, codeObj.tag_list);
        preventDeleteLastLine(codeMirror);
    }

    $('#code-tabs li').first().addClass('active');
    $('#code-tab-content div').first().addClass('active');

    // Refresh code mirrors when switching tabs to prevent UI glitches
    $('#code-tabs a').click(function(e) {
        e.preventDefault();
        $(this).tab('show');
        var codeMirrorId = this.getAttribute('href').substring(1);
        newCodeMirrors[codeMirrorId].refresh();
    });

    if (files.length == 1) {
        $('#code-tabs').hide();
    }

    return newCodeMirrors;
}

// TODO create a TabbedCodeMirror class

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
            || (prevLineWrapClass != 'CodeMirror-Activeline-background'))) {

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

