/**
 * An extension to the PCRS TabbedCodeMirror that helps trace highlighting.
 */
function EditorTabbedCodeMirror() {
    TabbedCodeMirror.call(this);
    this.activeLine = -1;
    this.activeMirror = -1;
}
EditorTabbedCodeMirror.prototype = Object.create(TabbedCodeMirror.prototype);
EditorTabbedCodeMirror.prototype.constructor = EditorTabbedCodeMirror;

EditorTabbedCodeMirror._tracedLineClass = 'CodeMirror-activeline-background';
EditorTabbedCodeMirror._breakpointGutterId = 'EditorTabbedCodeMirror-bpgi';

/**
 * Adds a click callback to all file gutters.
 *
 * @param {function} A callback with fileName and lineNumber parameters.
 * The lineNumber starts at index 0.
 */
EditorTabbedCodeMirror.prototype.setGutterClickCallback = function(callback) {
    var that = this;
    for (var i = 0; i < this.mirrors.length; i++) {
        var mirror = this.mirrors[i];
        var fileName = this._tabTitleButtonAtIndex(i).text();
        // Ugly closure to avoid resetting the fileName var for each tab
        mirror.on('gutterClick', (function(fileName) {
            return function(cm, line, gutterId, ev) {
                // Only left click
                if (ev.which == 1) {
                    callback(fileName, line);
                }
            }
        })(fileName));
    }
}

/**
 * @override
 */
EditorTabbedCodeMirror.prototype._createCodeMirrorOptions = function(options) {
    var codeMirrorOptions =
        TabbedCodeMirror.prototype._createCodeMirrorOptions.apply(
            this, arguments);

    codeMirrorOptions.gutters = [
        EditorTabbedCodeMirror._breakpointGutterId,
        'CodeMirror-linenumbers',
    ];
    return codeMirrorOptions;
}

/**
 * Toggles the breakpoint indicator beside the given line.
 *
 * @param {string} fileName The tab name to mark
 * @param {number} lineNumber The line to mark
 */
EditorTabbedCodeMirror.prototype.toggleBreakpointIndicator =
        function(fileName, lineNumber) {
    var fileIndex = this.indexForTabWithName(fileName);
    var mirror = this.mirrors[fileIndex];
    var fileInfo = mirror.lineInfo(lineNumber);

    var marker = fileInfo.gutterMarkers
        ? null
        : this._createBreakpointMarkerDom();

    var gutterId = EditorTabbedCodeMirror._breakpointGutterId;
    mirror.setGutterMarker(lineNumber, gutterId, marker);
}

/**
 * Generates a DOM element to display as a breakpoint.
 */
EditorTabbedCodeMirror.prototype._createBreakpointMarkerDom = function() {
    var marker = document.createElement('div');
    marker.className = 'EditorTabbedCodeMirror-breakpoint';
    return marker;
}

/**
 * Highlights the given line for a given visualizer step.
 *
 * @param {number} lineNumber The line to highlight - starting at 0
 * @param {string} fileName The file to highlight inside.
 *                          The TCM will automatically switch here.
 */
EditorTabbedCodeMirror.prototype.setHighligtedLineAndFile = function(
        lineNumber, fileName) {
    if (this.getFileCount() == 0) {
        // It hasn't been initialized yet
        return;
    }
    this._resetOldHighlight();

    this.activeMirror = this.indexForTabWithName(fileName);
    this.activeLine = lineNumber;

    this.mirrors[this.activeMirror].addLineClass(this.activeLine, '',
        EditorTabbedCodeMirror._tracedLineClass);

    this.setActiveTabIndex(this.activeMirror);
}

EditorTabbedCodeMirror.prototype._resetOldHighlight = function() {
    if (this.activeLine != -1 && this.activeMirror != -1) {
        this.mirrors[this.activeMirror].removeLineClass(this.activeLine, '',
            EditorTabbedCodeMirror._tracedLineClass);
    }
}

