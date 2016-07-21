/**
 * Extension that handles blocked ranges and hash portions of code
 *
 * getHashedCode can be used to generate PCRS-submittable content
 */
function SubmissionTabbedCodeMirror() {
    TabbedCodeMirror.call(this);
}
SubmissionTabbedCodeMirror.prototype =
    Object.create(TabbedCodeMirror.prototype);
SubmissionTabbedCodeMirror.prototype.constructor = SubmissionTabbedCodeMirror;

SubmissionTabbedCodeMirror._blockedLineClass =
    'CodeMirror-activeline-background';

/**
 * @override
 *
 * @param {array} [options.block_ranges] Lines to block the user from editing.
 * @param {array} [options.hash_ranges] Lines to hash. See getHashedCode
 * @see TabbedCodeMirror.addFile for an explanation of other options
 */
SubmissionTabbedCodeMirror.prototype.addFile = function(options) {
    TabbedCodeMirror.prototype.addFile.apply(this, arguments);

    var mirror = this.mirrors[this.mirrors.length - 1];

    if ('block_ranges' in options) {
        this._blockLinesInMirror(mirror, options.block_ranges);
    }
    if ('hash_ranges' in options) {
        this._hashLinesInMirror(mirror, options.hash_ranges);
    }
}

SubmissionTabbedCodeMirror.prototype._blockLinesInMirror =
        function(mirror, ranges) {
    // Highlight the given ranges
    for (var i = 0; i < ranges.length; i++) {
        for (var j = ranges[i].start; j <= ranges[i].end; j++) {
            mirror.addLineClass(
                j - 1, '', SubmissionTabbedCodeMirror._blockedLineClass);
        }
    }
    var that = this;
    // Block the given ranges
    mirror.on('beforeChange', function(cm, change) {
        var start = Math.min(change.to.line, change.from.line);
        var end = Math.max(change.to.line, change.from.line);

        if (that._rangeLiesInBlockedArea(mirror, start, end)) {
            change.cancel();
        }
    });
}

SubmissionTabbedCodeMirror.prototype._hashLinesInMirror =
        function(mirror, ranges) {
    for (var i = 0; i < ranges.length; i++) {
        var start = ranges[i].start - 1;
        var end = ranges[i].end - 1;
        // We only care about the start index
        // The end is determined dynamically
        mirror.addLineClass(start, '', 'hash-start');
    }
}

/**
 * Determines if a range intersects the target ranges.
 */
SubmissionTabbedCodeMirror.prototype._rangeLiesInBlockedArea =
        function(mirror, start, end) {
    var blockedClass = SubmissionTabbedCodeMirror._blockedLineClass;
    for (var i = start; i <= end; i++) {
        var wrapClass = mirror.lineInfo(i).wrapClass;
        if (wrapClass && wrapClass.indexOf(blockedClass) > -1) {
            return true;
        }
    }
    return false;
}

/**
 * Insert hash keys where the modifiable code starts and ends.
 */
SubmissionTabbedCodeMirror.prototype._getHashedCodeFromMirror =
        function(mirror, hash) {
    var code = '';
    var inHash = false;

    var blockedClass = SubmissionTabbedCodeMirror._blockedLineClass;
    for (var i = 0; i < mirror.lineCount(); i++) {
        var wrapClass = mirror.lineInfo(i).wrapClass;
        // Blocked code
        if (wrapClass && wrapClass.indexOf(blockedClass) > -1) {
            if (inHash) {
                code += hash + '\n';
                inHash = false;
            }
            continue;
        }
        // The start of a hash segment
        if (wrapClass && wrapClass.indexOf('hash-start') > -1) {
            if (inHash) {
                // student_code tags back to back
                code += hash + '\n';
            }
            code += hash + '\n';
            inHash = true;
        }

        code += mirror.getLine(i) + '\n';
    }
    if (inHash) {
        code += hash + '\n';
    }
    return code;
}

/**
 * Hashes all of the code mirrors in order.
 * Hashes surround specified code for the server to parse.
 */
SubmissionTabbedCodeMirror.prototype.getHashedCode = function(hash) {
    var code = '';
    for (var i = 0; i < this.mirrors.length; i++) {
        var mirror = this.mirrors[i];
        code += this._getHashedCodeFromMirror(mirror, hash);

        if (i < this.mirrors.length - 1) {
            code += '\n';
        }
    }
    return code;
}

/**
 * Parses the given tagged code text and adds files from it.
 *
 * This utilizes TagManager to parse the text.
 *
 * @param {string} code Text littered with tags - which will be parsed out
 * @see addFile
 */
SubmissionTabbedCodeMirror.prototype.addFilesFromTagText = function(code) {
    while (this.getFileCount() > 0) {
        this.removeFileAtIndex(0);
    }

    var files = TagManager.parseCodeIntoFiles(code);

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var codeObj = TagManager.stripTagsForStudent(file.code);
        this.addFile({
            'name': file.name,
            'code': codeObj.code,
            'block_ranges': codeObj.block_ranges,
            'hash_ranges': codeObj.hash_ranges,
        });
    }

    this.setActiveTabIndex(0);
    this.markClean();
}

