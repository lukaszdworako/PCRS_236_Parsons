/**
 * An extension to the PCRS TabbedCodeMirror that helps trace highlighting.
 */
function EditorTabbedCodeMirror() {
    TabbedCodeMirror.call(this);
    this.mirrorHeight = 300;
    this._makeContentResizable();
}
EditorTabbedCodeMirror.prototype = Object.create(TabbedCodeMirror.prototype);
EditorTabbedCodeMirror.prototype.constructor = EditorTabbedCodeMirror;

EditorTabbedCodeMirror._arrowPolygon = '0,0 6,5 0,10 0,0';
EditorTabbedCodeMirror._traceGutterId =
    'EditorTabbedCodeMirror-trace-gutter-id-';
EditorTabbedCodeMirror._breakpointGutterId =
    'EditorTabbedCodeMirror-breakpoint-gutter-id';

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
        // Two trace gutters for both arrows
        EditorTabbedCodeMirror._traceGutterId + '0',
        EditorTabbedCodeMirror._traceGutterId + '1',
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

    var gutterId = EditorTabbedCodeMirror._breakpointGutterId;

    var marker = fileInfo.gutterMarkers && fileInfo.gutterMarkers[gutterId]
        ? null // hide the breakpoint if it exists
        : this._renderBreakpointMarkerDom();

    mirror.setGutterMarker(lineNumber, gutterId, marker);
    mirror.refresh();
}

/**
 * Generates a DOM element to display as a breakpoint.
 */
EditorTabbedCodeMirror.prototype._renderBreakpointMarkerDom = function() {
    var marker = document.createElement('div');
    marker.className = 'EditorTabbedCodeMirror-breakpoint';
    return marker;
}

/**
 * @param {number} lineNumber The line to highlight - starting at 0
 * @param {string} fileName The file to highlight inside.
 *                          The TCM will automatically switch here.
 * @param {number} arrow.offset 0 or 1 to put the arrow in different gutters.
 * @param {string} arrow.color  A CSS color string for the arrow
 */
EditorTabbedCodeMirror.prototype.addArrowToLineAndFile = function(
        line, file, arrow) {
    if (this.getFileCount() == 0) {
        // It hasn't been initialized yet
        return;
    }
    var mirrorIndex = this.indexForTabWithName(file);
    var mirror = this.mirrors[mirrorIndex];

    this.setActiveTabIndex(mirrorIndex);
    mirror.scrollIntoView({
        ch: 0,
        line: line,
    });

    var marker = this._renderArrowWithColor(arrow.color);
    var gutterId = EditorTabbedCodeMirror._traceGutterId + arrow.offset;
    mirror.setGutterMarker(line, gutterId, marker);
}

EditorTabbedCodeMirror.prototype.resetStepArrows = function() {
    this.clearGutter(EditorTabbedCodeMirror._traceGutterId + '0');
    this.clearGutter(EditorTabbedCodeMirror._traceGutterId + '1');
}

/**
 * Clears all gutters for the given gutterId.
 *
 * @param {string} gutterId The gutter class to clear.
 */
EditorTabbedCodeMirror.prototype.clearGutter = function(gutterId) {
    for (var i = 0; i < this.mirrors.length; i++) {
        var mirror = this.mirrors[i];
        mirror.clearGutter(gutterId);
    }
}

/**
 * Renders a nice DOM arrow for the given CSS color.
 *
 * @param {string} color The color for the allow
 * @return A DOM SVG arrow elemnt.
 */
EditorTabbedCodeMirror.prototype._renderArrowWithColor = function(color) {
    var elementNamespace = 'http://www.w3.org/2000/svg';

    var svg = document.createElementNS(elementNamespace, 'svg');
    svg.setAttribute('class', 'EditorTabbedCodeMirror-trace-arrow');

    var polygon = document.createElementNS(elementNamespace, 'polygon');
    polygon.setAttribute('points', EditorTabbedCodeMirror._arrowPolygon);
    polygon.setAttribute('fill', color);

    svg.appendChild(polygon);
    return svg;
}

/**
 * @override
 */
EditorTabbedCodeMirror.prototype.addFile = function(options) {
    TabbedCodeMirror.prototype.addFile.apply(this, arguments);
    var newMirror = this.mirrors[this.mirrors.length - 1];
    newMirror.setSize(null, this.mirrorHeight + 'px');
}

/**
 * Allows the code mirrors to be manually resizable (vertically).
 */
EditorTabbedCodeMirror.prototype._makeContentResizable = function() {
    var that = this;
    this.$content.addClass('EditorTabbedCodeMirror-content');
    this.$content.resizable({
        handles: 's',
        minHeight: 100,
        resize: function(ev, ui) {
            that.setMirrorHeight($(this).height());
        },
    });
}

/**
 * Set a static height for all the mirrors
 */
EditorTabbedCodeMirror.prototype.setMirrorHeight = function(height) {
    this.mirrorHeight = height;
    for (var i = 0; i < this.mirrors.length; i++) {
        var mirror = this.mirrors[i];
        mirror.setSize(null, this.mirrorHeight + 'px');
    }
}

