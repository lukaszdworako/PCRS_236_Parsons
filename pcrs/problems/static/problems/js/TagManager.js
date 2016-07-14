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
    var ranges = TagManager.findTagRanges(code)['no_tag'];

    var lines = code.split('\n');

    // Go backwards to avoid shifting tag offsets
    for (var i = ranges.length - 1; i >= 0; i--) {
        var start = ranges[i].start;
        var end = ranges[i].end;

        lines.splice(end, 0, '[/student_code]');
        lines.splice(start, 0, '[student_code]');
    }
    return lines.join('\n');
}

/**
 * Finds the ranges of each type of tag.
 *
 * @param {string} code Raw code without [file] tags.
 * @return {Object} Several arrays of ranges corresponding to tag types.
 */
TagManager.findTagRanges = function(code) {
    var tag_lists = {
        'blocked': [],
        'hidden': [],
        'student_code': [],
        'no_tag': [],
    };

    // How many tags deep we are (assuming tags can be embedded)
    var tag_depth = 0;

    // The line of the last closing tag
    var lastTagLine = -1;

    var lines = code.split('\n');
    // Store all tags open and close lines
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var match;

        if (match = line.match(/^[ \t]*\[([\w_]+)\][ \t]*$/)) {
            tag_depth += 1;
            var tagList = tag_lists[match[1]];

            tagList.push({
                start: i + 1,
                end: null,
            });
        } else if (match = line.match(/^[ \t]*\[\/([\w_]+)\][ \t]*$/)) {
            lastTagLine = i;
            tag_depth -= 1;
            var tagList = tag_lists[match[1]];
            tagList[tagList.length - 1].end = i + 1;
        // If no tags are on this line and we aren't inside any tags
        } else if (tag_depth == 0) {
            var noTagList = tag_lists['no_tag'];

            // Create a new no_tag entry if this is _right after_ a close tag
            if (i == lastTagLine + 1) {
                noTagList.push({
                    start: i,
                    end: i + 1,
                });
            } else {
                noTagList[noTagList.length - 1].end += 1;
            }
        }

        if (tag_depth < 0) throw new Error("Mismatching tags");
    }
    if (tag_depth != 0) throw new Error("Mismatching tags");

    return tag_lists;
}

/**
 * Determines the ranges of code that have any tags.
 * Can be used to determine if tag insertion in given spots is legal.
 *
 * @param {string} code Raw code without [file] tags.
 * @return {Array} Objects with 'start' line and 'end' line params.
 */
TagManager.findRangesWithTags = function(code) {
    var namedTagRanges = TagManager.findTagRanges(code);
    delete namedTagRanges.no_tag;
    var tagNames = Object.keys(namedTagRanges);
    var allTagRanges = [];

    for (var i = 0; i < tagNames.length; i++) {
        var tagList = namedTagRanges[tagNames[i]];
        for (var j = 0; j < tagList.length; j++) {
            allTagRanges.push(tagList[j]);
        }
    }

    return allTagRanges;
}

/**
 * Remove [block] and [student_code] tags
 * from source code.
 */
TagManager.stripTagsForStudent = function(code) {
    var lines = code.split("\n");
    var student_view_line = 1;

    var block_ranges = [];
    var hash_ranges = [];

    code = "";
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];

        if (line.indexOf("[blocked]") > -1) {
            block_ranges.push({
                'start': student_view_line,
                'end': 0,
            });
        } else if( line.indexOf("[/blocked]") > -1) {
            block_ranges[block_ranges.length - 1].end = student_view_line - 1;
        } else if (line.indexOf("[student_code]") > -1) {
            hash_ranges.push({
                'start': student_view_line,
                'end': 0,
            });
        } else if (line.indexOf("[/student_code]") > -1) {
            hash_ranges[hash_ranges.length - 1].end = student_view_line - 1;
        } else {
            code += lines[i] + '\n';
            student_view_line++;
        }
    }

    // Remove last \n escape sequence
    code = code.substring(0, code.length - 1);

    return {
        code:         code,
        block_ranges: block_ranges,
        hash_ranges:  hash_ranges,
    };
}

