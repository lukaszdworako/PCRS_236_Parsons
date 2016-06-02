function TagManager() {
}

/**
 * Splits code into corresponding files.
 *
 * @param {string} code Raw code text with tags included.
 * @return {Array} Objects with 'name' and 'code' parameters (both strings).
 *                 If there are no [file] tags, the 'name' param will be null.
 */
TagManager.parseCodeIntoFiles = function(code) {
    var files = [];
    var match;
    while (match = /[\t ]*\[file ([A-Za-z0-9_\.]+)\][\t ]*\n/.exec(code)) {
        var endMatch = code.match(/\n[\t ]*\[\/file\][\t ]*/);
        var studentCodeStart = match.index + match[0].length;
        var studentCodeEnd = endMatch.index;

        files.push({
            'name': match[1],
            'code': code.substring(studentCodeStart, studentCodeEnd),
        });

        code = code.slice(endMatch.index + endMatch[0].length);
    }

    // If there are no [file] tags (legacy support)
    if (files.length == 0) {
        files.push({
            'name': null,
            'code': code,
        });
    }

    return files;
}

/**
 * Joins the given files into a code string (probably to be submitted).
 *
 * @see parseCodeIntoFiles
 * @param {Array} files An array of file objects with 'name' and 'code' params.
 * @return {string} Raw code with [file <name>] tags included.
 *                  If a file name is null, there will be no file tags.
*/
TagManager.concatFilesIntoCode = function(files) {
    // If there is only one file with no name (legacy support)
    if (files.length == 1 && files[0].name == null) {
        return files[0].code;
    }

    var code = "";
    for (var i = 0; i < files.length; i++) {
        var f = files[i];
        code += '[file ' + f.name + ']\n' + f.code + '\n[/file]';
        if (i < files.length - 1) {
            code += '\n';
        }
    }
    return code;
}

/**
 * Adds student code tags to the given code where necessary.
 * The given code should _NOT_ have any file tags.
 * Code tags will be inserted around non-wrapped lines (e.g. no blocked tags)
 *
 * @param {string} code Raw code (but without [file] tags)
 * @return {string} The code with student tags inserted
*/
TagManager.addStudentCodeTags = function(code) {
    var lines = code.split('\n');
    var new_code = "";
    var student_code_tag_open = false;
    var some_tag_open = 0;
    var just_closed = false;
    var student_code_tag_count = 0;

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        // Check other tags
        if (line.indexOf("[blocked]") > -1 || line.indexOf("[hidden]") > -1 ||
            line.indexOf("[student_code]") > -1) {
            if(line.indexOf("[student_code]") > -1) {
                student_code_tag_count += 1;
            }
            some_tag_open += 1;
        }
        if (line.indexOf("[/blocked]") > -1 || line.indexOf("[/hidden]") > -1 ||
            line.indexOf("[/student_code]") > -1) {
            some_tag_open -= 1;
            just_closed = true;
        }
        // Add student_code tag
        if (some_tag_open == 0 && just_closed == false && student_code_tag_open == false) {
            new_code +=  "[student_code]\n" + line + '\n';
            student_code_tag_count += 1;
            student_code_tag_open = true;
        } else if (some_tag_open > 0 && student_code_tag_open == true) {
            new_code += "[/student_code]\n" + line + '\n';
            student_code_tag_open = false;
        } else {
            new_code += line + '\n';
        }
        just_closed = false;
    }
    // If no student_code included in the middle of the souce code
    if (student_code_tag_count == 0) {
        new_code += "[student_code]\n\n";
        student_code_tag_open = true;
    } else {
        // Remove last \n
        new_code = new_code.substring(0, new_code.length-1);
    }
    // Close last tag if needed
    if (student_code_tag_open == true) {
        new_code += "\n[/student_code]";
    }
    return new_code;
}

/**
 * Track all tags (both open and close state)
 */
TagManager.findTagPositions = function(code) {
    var lines = code.split('\n');
    var blocked_open = 0;
    var hidden_open = 0;
    var student_code_open = 0;

    var blocked_list = [];
    var hidden_list = [];
    var student_code_list = [];

    // Store all tags open and close lines
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];

        if((line.split("[blocked]").length - 1) > 0){
            blocked_list.push({"start": i+1, "end": 0});
            blocked_open += 1;
            continue;
        }
        if((line.split("[/blocked]").length - 1) > 0) {
            blocked_list[blocked_open - 1].end = i + 1;
            continue;
        }

        if((line.split("[hidden]").length - 1) > 0) {
            hidden_list.push({"start": i + 1, "end": 0});
            hidden_open += 1;
            continue;
        }
        if((line.split("[/hidden]").length - 1) > 0) {
            hidden_list[hidden_open - 1].end = i + 1;
            continue;
        }

        if((line.split("[student_code]").length - 1) > 0) {
            student_code_list.push({"start": i + 1, "end": 0});
            student_code_open += 1;
            continue;
        }
        if((line.split("[/student_code]").length - 1) > 0) {
            student_code_list[student_code_open - 1].end = i + 1;
        }
    }

    return {
        'blocked':      blocked_list,
        'hidden':       hidden_list,
        'student_code': student_code_list,
    };
}

