// NOTE: This version _might_ work with other versions!

/*

   Online Python Tutor
   https://github.com/pgbovine/OnlinePythonTutor/

   Copyright (C) Philip J. Guo (philip@pgbovine.net)

   Permission is hereby granted, free of charge, to any person obtaining a
   copy of this software and associated documentation files (the
   "Software"), to deal in the Software without restriction, including
   without limitation the rights to use, copy, modify, merge, publish,
   distribute, sublicense, and/or sell copies of the Software, and to
   permit persons to whom the Software is furnished to do so, subject to
   the following conditions:

   The above copyright notice and this permission notice shall be included
   in all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/


/* To import, put this at the top of your HTML page:

   <!-- requirements for pytutor.js -->
   <script type="text/javascript" src="js/d3.v2.min.js"></script>
   <script type="text/javascript" src="js/jquery-1.8.2.min.js"></script>
   <script type="text/javascript" src="js/jquery.ba-bbq.min.js"></script> <!-- for handling back button and URL hashes -->
   <script type="text/javascript" src="js/jquery.jsPlumb-1.3.10-all-min.js "></script> <!-- for rendering SVG connectors
   <script type="text/javascript" src="js/EditorTabbedCodeMirror.js"></script>
   DO NOT UPGRADE ABOVE 1.3.10 OR ELSE BREAKAGE WILL OCCUR -->
   <script type="text/javascript" src="js/jquery-ui-1.11.4/jquery-ui.min.js"></script> <!-- for sliders and other UI elements -->
   <link type="text/css" href="js/jquery-ui-1.11.4/jquery-ui.css" rel="stylesheet" />

   <script type="text/javascript" src="js/pytutor.js"></script>
   <link rel="stylesheet" href="css/pytutor.css"/>

*/


/* Coding gotchas:

   - NEVER use raw $(__) or d3.select(__) statements to select DOM elements.

   ALWAYS use myViz.domRoot or myViz.domRootD3 for jQuery and D3, respectively.

   Otherwise things will break in weird ways when you have more than one visualization
   embedded within a webpage, due to multiple matches in the global namespace.


   - always use generateID to generate unique CSS IDs, or else things will break
   when multiple ExecutionVisualizer instances are displayed on a webpage

*/

String.prototype.rtrim = function() {
    return this.replace(/\s*$/g, "");
}

var curVisualizerID = 1; // global to uniquely identify each ExecutionVisualizer instance

// domRootID is the string ID of the root element where to render this instance
// dat is data returned by the Python Tutor backend consisting of two fields:
//   code  - string of executed code
//   trace - a full execution trace
//
// params is an object containing optional parameters, such as:
//   jumpToEnd - if non-null, jump to the very end of execution if
//               there's no error, or if there's an error, jump to the
//               FIRST ENTRY with an error
//   startingInstruction - the (zero-indexed) execution point to display upon rendering
//                         if this is set, then it *overrides* jumpToEnd
//   hideOutput - hide "Program output" display
//   disableHeapNesting   - if true, then render all heap objects at the top level (i.e., no nested objects)
//   drawParentPointers   - if true, then draw environment diagram parent pointers for all frames
//                          WARNING: there are hard-to-debug MEMORY LEAKS associated with activating this option
//   textualMemoryLabels  - render references using textual memory labels rather than as jsPlumb arrows.
//                          this is good for slow browsers or when used with disableHeapNesting
//                          to prevent "arrow overload"
//   updateOutputCallback - function to call (with 'this' as parameter)
//                          whenever this.updateOutput() is called
//                          (BEFORE rendering the output display)
//   heightChangeCallback - function to call (with 'this' as parameter)
//                          whenever the HEIGHT of #dataViz changes
//   verticalStack - if true, then stack code display ON TOP of visualization
//                   (else place side-by-side)
//   visualizerIdOverride - override visualizer ID instead of auto-assigning it
//                          (BE CAREFUL ABOUT NOT HAVING DUPLICATE IDs ON THE SAME PAGE,
//                           OR ELSE ARROWS AND OTHER STUFF WILL GO HAYWIRE!)
//   compactFuncLabels - render functions with a 'func' prefix and no type label
//   showAllFrameLabels - display frame and parent frame labels for all functions (default: false)
//   hideCode - hide the code display and show only the data structure viz
//   lang - to render labels in a style appropriate for other languages
//          'py2' for Python 2, 'py3' for Python 3, 'js' for JavaScript, 'java' for Java,
//          'ts' for TypeScript, 'ruby' for Ruby, 'c' for C, 'cpp' for C++
//          [default is Python-style labels]
//   debugMode - some extra debugging printouts
function ExecutionVisualizer(domRootID, data, params) {
    this.files = data.files;
    this.curTrace = data.trace;
    this.curInstr = 0;

    this.params = params ? params : {};

    this.compactFuncLabels = this.params.compactFuncLabels;

    if (this.params.visualizerIdOverride) {
        this.visualizerID = this.params.visualizerIdOverride;
    } else {
        // needs to be unique!
        this.visualizerID = curVisualizerID;
        curVisualizerID++;
    }

    // avoid 'undefined' state
    this.disableHeapNesting = (this.params.disableHeapNesting == true);
    this.drawParentPointers = (this.params.drawParentPointers == true);
    this.textualMemoryLabels = (this.params.textualMemoryLabels == true);
    this.showAllFrameLabels = (this.params.showAllFrameLabels == true);

    // cool, we can create a separate jsPlumb instance for each visualization:
    this.jsPlumbInstance = jsPlumb.getInstance({
        Endpoint: ["Dot", {radius:3}],
        EndpointStyles: [{fillStyle: connectorBaseColor}, {fillstyle: null} /* make right endpoint invisible */],
        Anchors: ["RightMiddle", "LeftMiddle"],
        PaintStyle: {lineWidth:1, strokeStyle: connectorBaseColor},

            // bezier curve style:
            //Connector: [ "Bezier", { curviness:15 }], /* too much 'curviness' causes lines to run together */
            //Overlays: [[ "Arrow", { length: 14, width:10, foldback:0.55, location:0.35 }]],

            // state machine curve style:
        Connector: [ "StateMachine" ],
        Overlays: [[ "Arrow", { length: 10, width:7, foldback:0.55, location:1 }]],
        EndpointHoverStyles: [{fillStyle: connectorHighlightColor}, {fillstyle: null} /* make right endpoint invisible */],
        HoverPaintStyle: {lineWidth: 1, strokeStyle: connectorHighlightColor},
    });

    // true iff trace ended prematurely since maximum instruction limit has
    // been reached
    var instrLimitReached = false;


    // the root elements for jQuery and D3 selections, respectively.
    // ALWAYS use these and never use raw $(__) or d3.select(__)
    this.domRoot = $('#' + domRootID);
    this.domRootD3 = d3.select('#' + domRootID);

    // stick a new div.ExecutionVisualizer within domRoot and make that
    // the new domRoot:
    this.domRoot.html('<div class="ExecutionVisualizer"></div>');

    this.domRoot = this.domRoot.find('div.ExecutionVisualizer');
    this.domRootD3 = this.domRootD3.select('div.ExecutionVisualizer');

    this.sortedBreakpointSteps = [];

    this.classAttrsHidden = {}; // kludgy hack for 'show/hide attributes' for class objects

    // API for adding a hook, created by David Pritchard
    this.pytutor_hooks = {}; // keys, hook names; values, list of functions

    if (this.params.lang == 'java') {
        this.activateJavaFrontend(); // ohhhh yeah!
    }

    // how many lines does curTrace print to stdout max?
    this.numStdoutLines = 0;
    // go backwards from the end ... sometimes the final entry doesn't
    // have an stdout
    var lastStdout;
    for (var i = this.curTrace.length-1; i >= 0; i--) {
        lastStdout = this.curTrace[i].stdout;
        if (lastStdout) {
            break;
        }
    }

    if (lastStdout) {
        this.numStdoutLines = lastStdout.rtrim().split('\n').length;
    }

    this.tcm = new EditorTabbedCodeMirror();

    this.try_hook("end_constructor", {myViz:this});

    this.hasRendered = false;

    this.render(); // go for it!
}


/* API for adding a hook, created by David Pritchard
   https://github.com/daveagp

   [this documentation is a bit deprecated since Philip made try_hook a
   method of ExecutionVisualizer, but the general ideas remains]

   An external user should call
   add_pytutor_hook("hook_name_here", function(args) {...})
   args will be a javascript object with several named properties;
   this is meant to be similar to Python's keyword arguments.

   The hooked function should return an array whose first element is a boolean:
   true if it completely handled the situation (no further hooks
   nor the base function should be called); false otherwise (wasn't handled).
   If the hook semantically represents a function that returns something,
   the second value of the returned array is that semantic return value.

   E.g. for the Java visualizer a simplified version of a hook we use is:

   add_pytutor_hook(
   "isPrimitiveType",
   function(args) {
   var obj = args.obj; // unpack
   if (obj instanceof Array && obj[0] == "CHAR-LITERAL")
   return [true, true]; // yes we handled it, yes it's primitive
   return [false]; // didn't handle it, let someone else
   });

   Hook callbacks can return false or undefined (i.e. no return
   value) in lieu of [false].

   NB: If multiple functions are added to a hook, the oldest goes first.
   */
ExecutionVisualizer.prototype.add_pytutor_hook = function(hook_name, func) {
    if (this.pytutor_hooks[hook_name])
        this.pytutor_hooks[hook_name].push(func);
    else
        this.pytutor_hooks[hook_name] = [func];
}

/*

   [this documentation is a bit deprecated since Philip made try_hook a
   method of ExecutionVisualizer, but the general ideas remains]

   try_hook(hook_name, args): how the internal codebase invokes a hook.
   args will be a javascript object with several named properties;
   this is meant to be similar to Python's keyword arguments.
   E.g.,

   function isPrimitiveType(obj) {
   var hook_result = try_hook("isPrimitiveType", {obj:obj});
   if (hook_result[0]) return hook_result[1];
// go on as normal if the hook didn't handle it

Although add_pytutor_hook allows the hooked function to
return false or undefined, try_hook will always return
something with the strict format [false], [true] or [true, ...].
*/
ExecutionVisualizer.prototype.try_hook = function(hook_name, args) {
    if (this.pytutor_hooks[hook_name]) {
        for (var i=0; i<this.pytutor_hooks[hook_name].length; i++) {

            // apply w/o "this", and pack sole arg into array as required by apply
            var handled_and_result
                = this.pytutor_hooks[hook_name][i].apply(null, [args]);

            if (handled_and_result && handled_and_result[0])
                return handled_and_result;
        }
    }
    return [false];
}


// for managing state related to pesky jsPlumb connectors, need to reset
// before every call to renderDataStructures, or else all hell breaks
// loose. yeah, this is kludgy and stateful, but at least all of the
// relevant state gets shoved into one unified place
ExecutionVisualizer.prototype.resetJsPlumbManager = function() {
    this.jsPlumbManager = {
        heap_pointer_src_id: 1, // increment this to be unique for each heap_pointer_src_*

        // Key:   CSS ID of the div element representing the stack frame variable
        //        (for stack->heap connections) or heap object (for heap->heap connections)
        //        the format is: '<this.visualizerID>__heap_pointer_src_<src id>'
        // Value: CSS ID of the div element representing the value rendered in the heap
        //        (the format is given by generateHeapObjID())
        //
        // The reason we need to prepend this.visualizerID is because jsPlumb needs
        // GLOBALLY UNIQUE IDs for use as connector endpoints.
        //
        // TODO: jsPlumb might be able to directly take DOM elements rather
        // than IDs, which makes the above point moot. But let's just stick
        // with this for now until I want to majorly refactor :)

        // the only elements in these sets are NEW elements to be rendered in this
        // particular call to renderDataStructures.
        connectionEndpointIDs: d3.map(),
        heapConnectionEndpointIDs: d3.map(), // subset of connectionEndpointIDs for heap->heap connections
            // analogous to connectionEndpointIDs, except for environment parent pointers
        parentPointerConnectionEndpointIDs: d3.map(),

        renderedHeapObjectIDs: d3.map(), // format given by generateHeapObjID()
    };
}


// create a unique ID, which is often necessary so that jsPlumb doesn't get confused
// due to multiple ExecutionVisualizer instances being displayed simultaneously
ExecutionVisualizer.prototype.generateID = function(original_id) {
    // (it's safer to start names with a letter rather than a number)
    return 'v' + this.visualizerID + '__' + original_id;
}

// create a unique CSS ID for a heap object, which should include both
// its ID and the current step number. this is necessary if we want to
// display the same heap object at multiple execution steps.
ExecutionVisualizer.prototype.generateHeapObjID = function(objID, stepNum) {
    return this.generateID('heap_object_' + objID + '_s' + stepNum);
}


ExecutionVisualizer.prototype.render = function() {
    if (this.hasRendered) {
        alert('ERROR: You should only call render() ONCE on an ExecutionVisualizer object.');
        return;
    }

    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    var codeDisplayHTML =
        '<div id="codeDisplayDiv">\
        <div id="pyCodeOutputDiv"/>\
        <div id="legendDiv"/>\
        <div id="executionSliderDocs">\
            Click on a line number to set a breakpoint, then use the Forward and Back buttons to jump there.\
        </div>\
        <div id="executionSlider"/>\
        <div id="executionSliderFooter"/>\
        <div id="vcrControls">\
            <button id="jmpFirstInstr" class="btn btn-default" type="button">\
                &lt;&lt; First</button>\
            <button id="jmpBreakpointBack" class="btn btn-default" type="button">\
                &lt; Breakpoint</button>\
            <button id="jmpStepBack" class="btn btn-default" type="button">\
                &lt; Step</button>\
            <button id="jmpStepFwd" class="btn btn-default" type="button">\
                Step &gt;</button>\
            <button id="jmpBreakpointFwd" class="btn btn-default" type="button">\
                Breakpoint &gt;</button>\
            <button id="jmpLastInstr" class="btn btn-default" type="button">\
                Last &gt;&gt;</button>\
            <span id="curInstr">Step ? of ?</span>\
        </div>\
        <div id="errorOutput" class="alert-container red-alert"/>\
        </div>';

    var outputsHTML =
        '<div id="htmlOutputDiv"></div>\
        <div id="progOutputs">\
            <div id="printOutputDocs">Print output (drag lower right corner to resize)</div>\n\
            <textarea id="pyStdout" cols="40" rows="5" wrap="off" readonly></textarea>\
        </div>';

    var codeVizHTML =
        '<div id="dataViz">\
            <table id="stackHeapTable">\
                <tr>\
                    <td id="stack_td">\
                        <div id="stackHeader">Frames</div>\
                        <div id="stack"></div>\
                    </td>\
                    <td id="heap_td">\
                        <div id="globals_area">\
                            <div id="heapHeader">Globals</div>\
                        </div>\
                        <div id="heap">\
                            <div id="heapHeader">Objects</div>\
                        </div>\
                    </td>\
                </tr>\
            </table>\
        </div>';

    if (this.params.verticalStack) {
        this.domRoot.html('<table border="0" class="visualizer"><tr>' +
            '<td class="vizLayoutTd" id="vizLayoutTdFirst"">' +
            codeDisplayHTML + '</td></tr><tr><td class="vizLayoutTd" id="vizLayoutTdSecond">' +
            codeVizHTML + '</td></tr></table>');
    } else {
        this.domRoot.html('<table border="0" class="visualizer"><tr>' +
            '<td class="vizLayoutTd" id="vizLayoutTdFirst">' +
            codeDisplayHTML + '</td><td class="vizLayoutTd" id="vizLayoutTdSecond">' +
            codeVizHTML + '</td></tr></table>');
    }

    // position this under the code:
    //this.domRoot.find('#vizLayoutTdFirst').append(outputsHTML);

    // position this above visualization (started trying this on 2016-06-01)
    this.domRoot.find('#vizLayoutTdSecond').prepend(outputsHTML);

    this.domRoot.find('#legendDiv')
        .append('<svg id="prevLegendArrowSVG"/> line that has just executed')
        .append('<p style="margin-top: 4px"><svg id="curLegendArrowSVG"/> next line to execute</p>');

    myViz.domRootD3.select('svg#prevLegendArrowSVG')
        .append('polygon')
        .attr('points', EditorTabbedCodeMirror._arrowPolygon)
        .attr('fill', prevArrowColor);

    myViz.domRootD3.select('svg#curLegendArrowSVG')
        .append('polygon')
        .attr('points', EditorTabbedCodeMirror._arrowPolygon)
        .attr('fill', nextArrowColor);

    // enable left-right draggable pane resizer (originally from David Pritchard)
    this.domRoot.find('#codeDisplayDiv').resizable({
        handles: "e",
        minWidth: 100, //otherwise looks really goofy
        resize: function(event, ui) { // old name: syncStdoutWidth, now not appropriate
            // resize stdout box in unison
            //myViz.domRoot.find("#pyStdout").css("width", $(this).width() - 20 /* wee tweaks */);

            myViz.domRoot.find("#codeDisplayDiv").css("height", "auto"); // redetermine height if necessary
            myViz.renderSliderBreakpoints(); // update breakpoint display accordingly on resize
            if (myViz.params.updateOutputCallback) // report size change
                myViz.params.updateOutputCallback(this);
        }});

    // Create a persistent globals frame
    this.domRoot.find("#globals_area").append('<div class="stackFrame" id="'
            + myViz.generateID('globals') + '"><table class="stackFrameVarTable" id="'
            + myViz.generateID('global_table') + '"></table></div>');

    if (this.params.hideOutput) {
        this.domRoot.find('#progOutputs').hide();
    }

    this.domRoot.find("#jmpFirstInstr").click(function() {
        myViz.renderStep(0);
    });
    this.domRoot.find("#jmpLastInstr").click(function() {
        myViz.renderStep(myViz.curTrace.length - 1);
    });
    this.domRoot.find("#jmpStepBack").click(function() {
        myViz.stepBack();
    });
    this.domRoot.find("#jmpStepFwd").click(function() {
        myViz.stepForward();
    });
    this.domRoot.find("#jmpBreakpointBack").click(function() {
        myViz.stepBackToBreakpoint();
    });
    this.domRoot.find("#jmpBreakpointFwd").click(function() {
        myViz.stepForwardToBreakpoint();
    });

    // must postprocess curTrace prior to running precomputeCurTraceLayouts() ...
    var lastEntry = this.curTrace[this.curTrace.length - 1];

    this.instrLimitReached = (lastEntry.event == 'instruction_limit_reached');

    if (this.instrLimitReached) {
        this.curTrace.pop() // kill last entry
            var warningMsg = lastEntry.exception_msg;
        this.instrLimitReachedWarningMsg = warningMsg;
        myViz.domRoot.find("#errorOutput").html(htmlspecialchars(warningMsg));
        myViz.domRoot.find("#errorOutput").show();
    }

    // set up slider after postprocessing curTrace

    var sliderDiv = this.domRoot.find('#executionSlider');
    sliderDiv.slider({min: 0, max: this.curTrace.length - 1, step: 1});
    //disable keyboard actions on the slider itself (to prevent double-firing of events)
    sliderDiv.find(".ui-slider-handle").unbind('keydown');
    // make skinnier and taller
    sliderDiv.find(".ui-slider-handle").css('width', '0.8em');
    sliderDiv.find(".ui-slider-handle").css('height', '1.4em');
    this.domRoot.find(".ui-widget-content").css('font-size', '0.9em');

    this.domRoot.find('#executionSlider').bind('slide', function(evt, ui) {
        // this is SUPER subtle. if this value was changed programmatically,
        // then evt.originalEvent will be undefined. however, if this value
        // was changed by a user-initiated event, then this code should be
        // executed ...
        if (evt.originalEvent) {
            myViz.renderStep(ui.value);
        }
    });

    if (this.params.startingInstruction) {
        this.params.jumpToEnd = false; // override! make sure to handle FIRST

        // fail-soft with out-of-bounds startingInstruction values:
        if (this.params.startingInstruction < 0) {
            this.params.startingInstruction = 0;
        }
        if (this.params.startingInstruction >= this.curTrace.length) {
            this.params.startingInstruction = this.curTrace.length - 1;
        }

        assert(0 <= this.params.startingInstruction &&
                this.params.startingInstruction < this.curTrace.length);
        this.curInstr = this.params.startingInstruction;
    }

    if (this.params.jumpToEnd) {
        var firstErrorStep = -1;
        for (var i = 0; i < this.curTrace.length; i++) {
            var e = this.curTrace[i];
            if (e.event == 'exception' || e.event == 'uncaught_exception') {
                firstErrorStep = i;
                break;
            }
        }

        // set to first error step if relevant since that's more informative
        // than simply jumping to the very end
        if (firstErrorStep >= 0) {
            this.curInstr = firstErrorStep;
        } else {
            this.curInstr = this.curTrace.length - 1;
        }
    }

    if (this.params.hideCode) {
        this.domRoot.find('#vizLayoutTdFirst').hide(); // gigantic hack!
    }

    this.try_hook("end_render", {myViz:this});

    this.precomputeCurTraceLayouts();

    if ( ! this.params.hideCode) {
        this.renderSliderBreakpoints();
    }

    this.updateOutput();

    this._renderInitialTabbedCodeMirrorOver($('#pyCodeOutputDiv'));
    this.hasRendered = true;
}

/**
 * Create the initial tabbed code mirorr.
 *
 * @param {jQuery} $element The element to replace in the DOM.
 */
ExecutionVisualizer.prototype._renderInitialTabbedCodeMirrorOver =
        function($element) {
    $element.before(this.tcm.getJQueryObject());
    $element.remove();

    for (var i = 0; i < this.files.length; i++) {
        var file = this.files[i];
        this.tcm.addFile({
            'name': file.name,
            'code': file.code,
            // You will want to change this to a generic language if you port it
            'mode': cmModeForLanguageAndVersion('java', ''),
            'readOnly': true,
            'theme': user_theme,
        });
    }

    var that = this;
    this.tcm.setGutterClickCallback(function(fileName, lineNumber) {
        that.tcm.toggleBreakpointIndicator(fileName, lineNumber);

        var steps = that._stepsMatchingFileAndLine(fileName, lineNumber + 1);
        that._toggleStepBreakpoints(steps);
        that.renderSliderBreakpoints();
    });
}

/**
 * Toggles the given step breakpoints in the slider bar.
 *
 * @param {array} steps A list of integer steps
 */
ExecutionVisualizer.prototype._toggleStepBreakpoints = function(steps) {
    if (steps.length == 0) return;

    var alreadyMarked = this.sortedBreakpointSteps.indexOf(steps[0]) > -1;

    this.sortedBreakpointSteps = alreadyMarked
        ? $(this.sortedBreakpointSteps).not(steps).get() // Remove them all
        : this.sortedBreakpointSteps.concat(steps); // Add them all

    // sort() is lexicographical by default
    this.sortedBreakpointSteps.sort(function(first, second) {
        return first - second;
    });
}

/**
 * @param {string} fileName The file name to look for steps inside
 * @param {number} lineNumber The 1-indexed line number
 * @return {array} A list of integer step indices.
 */
ExecutionVisualizer.prototype._stepsMatchingFileAndLine =
        function(fileName, lineNumber) {
    var steps = [];
    for (var stepIndex = 0; stepIndex < this.curTrace.length; stepIndex++) {
        var step = this.curTrace[stepIndex];
        if (step.file == fileName && step.line == lineNumber) {
            steps.push(stepIndex);
        }
    }
    return steps;
}

// find the previous/next breakpoint to c or return -1 if it doesn't exist
ExecutionVisualizer.prototype.findPrevBreakpoint = function() {
    var myViz = this;
    var c = myViz.curInstr;

    if (myViz.sortedBreakpointSteps.length == 0) {
        return -1;
    } else {
        for (var i = 1; i < myViz.sortedBreakpointSteps.length; i++) {
            var prev = myViz.sortedBreakpointSteps[i-1];
            var cur = myViz.sortedBreakpointSteps[i];
            if (c <= prev)
                return -1;
            if (cur >= c)
                return prev;
        }

        // final edge case:
        var lastElt = myViz.sortedBreakpointSteps[myViz.sortedBreakpointSteps.length - 1];
        return (lastElt < c) ? lastElt : -1;
    }
}

ExecutionVisualizer.prototype.findNextBreakpoint = function() {
    var myViz = this;
    var c = myViz.curInstr;

    if (myViz.sortedBreakpointSteps.length == 0) {
        return -1;
    } else {
        for (var i = 0; i < myViz.sortedBreakpointSteps.length - 1; i++) {
            var cur = myViz.sortedBreakpointSteps[i];
            var next = myViz.sortedBreakpointSteps[i+1];
            if (c < cur)
                return cur;
            if (cur <= c && c < next) // subtle
                return next;
        }

        // final edge case:
        var lastElt = myViz.sortedBreakpointSteps[myViz.sortedBreakpointSteps.length - 1];
        return (lastElt > c) ? lastElt : -1;
    }
}


ExecutionVisualizer.prototype.stepForward = function() {
    this.stepTo(this.curInstr + 1);
}
ExecutionVisualizer.prototype.stepForwardToBreakpoint = function() {
    var index = this.findNextBreakpoint();
    if (index != -1) this.stepTo(index);
}
ExecutionVisualizer.prototype.stepBack = function() {
    this.stepTo(this.curInstr - 1);
}
ExecutionVisualizer.prototype.stepBackToBreakpoint = function() {
    var index = this.findPrevBreakpoint();
    if (index != -1) this.stepTo(index);
}
ExecutionVisualizer.prototype.stepTo = function(index) {
    if (index < 0 || index > this.curTrace.length - 1) {
        return;
    }
    this.curInstr = index;
    this.updateOutput();
}

ExecutionVisualizer.prototype.renderSliderBreakpoints = function() {
    this.domRoot.find("#executionSliderFooter").empty();
    var w = this.domRoot.find('#executionSlider').width();

    // I originally didn't want to delete and re-create this overlay every time,
    // but if I don't do so, there are weird flickering artifacts with clearing
    // the SVG container; so it's best to just delete and re-create the container each time
    var sliderOverlay = this.domRootD3.select('#executionSliderFooter')
        .append('svg')
        .attr('id', 'sliderOverlay')
        .attr('width', w)
        .attr('height', 12);

    var xrange = d3.scale.linear()
        .domain([0, this.curTrace.length - 1])
        .range([0, w]);

    sliderOverlay.selectAll('rect')
        .data(this.sortedBreakpointSteps)
        .enter().append('rect')
        .attr('x', function(d, i) {
            // make edge case of 0 look decent:
            return (d === 0) ? 0 : xrange(d) - 1;
        })
    .attr('y', 0)
        .attr('width', 2)
        .attr('height', 12)
        .style('fill', function(d) {
            return breakpointColor;
        });
}

// takes a string inputStr and returns an HTML version with
// the characters from [highlightIndex, highlightIndex+extent) highlighted with
// a span of class highlightCssClass
function htmlWithHighlight(inputStr, highlightInd, extent, highlightCssClass) {
    var prefix = '';
    if (highlightInd > 0) {
        prefix = inputStr.slice(0, highlightInd);
    }

    var highlightedChars = inputStr.slice(highlightInd, highlightInd + extent);

    var suffix = '';
    if (highlightInd + extent < inputStr.length) {
        suffix = inputStr.slice(highlightInd + extent, inputStr.length);
    }

    // ... then set the current line to lineHTML
    var lineHTML = htmlspecialchars(prefix) +
        '<span class="' + highlightCssClass + '">' +
        htmlspecialchars(highlightedChars) +
        '</span>' +
        htmlspecialchars(suffix);
    return lineHTML;
}


ExecutionVisualizer.prototype.renderStdout = function() {
    var curEntry = this.curTrace[this.curInstr];

    // if there isn't anything in curEntry.stdout, don't even bother
    // displaying the pane (but this may cause jumpiness later)
    if (!this.params.hideOutput && (this.numStdoutLines > 0)) {
        this.domRoot.find('#progOutputs').show();

        var pyStdout = this.domRoot.find("#pyStdout");

        // keep original horizontal scroll level:
        var oldLeft = pyStdout.scrollLeft();
        pyStdout.val(curEntry.stdout.rtrim() /* trim trailing spaces */);
        pyStdout.scrollLeft(oldLeft);
        pyStdout.scrollTop(pyStdout[0].scrollHeight); // scroll to bottom, though
    }
    else {
        this.domRoot.find('#progOutputs').hide();
    }
}


// This function is called every time the display needs to be updated
ExecutionVisualizer.prototype.updateOutput = function() {
    if (this.params.hideCode) {
        this.updateOutputMini();
    }
    else {
        this.updateOutputFull();
    }
    this.renderStdout();
    this.try_hook("end_updateOutput", {myViz:this});
}


ExecutionVisualizer.prototype.updateOutputFull = function() {
    assert(this.curTrace);
    assert( ! this.params.hideCode);

    // there's no point in re-rendering if this pane isn't even visible in the first place!
    if ( ! this.domRoot.is(':visible')) {
        return;
    }

    // call the callback if necessary (BEFORE rendering)
    if (this.params.updateOutputCallback) {
        this.params.updateOutputCallback(this);
    }

    var curEntry = this.curTrace[this.curInstr];

    if (this.params.debugMode) {
        console.log('updateOutputFull', curEntry);
        this.debugMode = true;
    }

    // PROGRAMMATICALLY change the value, so evt.originalEvent should be undefined
    this.domRoot.find('#executionSlider').slider('value', this.curInstr);

    // finally, render all of the data structures
    var curToplevelLayout = this.curTraceLayouts[this.curInstr];
    this.renderDataStructures(curEntry, curToplevelLayout);

    var prevDataVizHeight = this.domRoot.find('#dataViz').height();
    // call the callback if necessary (BEFORE rendering)
    if (this.domRoot.find('#dataViz').height() != prevDataVizHeight) {
        if (this.params.heightChangeCallback) {
            this.params.heightChangeCallback(this);
        }
    }

    this.renderVCRControls();
    this.renderErrors();
    this.renderTraceArrows();
}

ExecutionVisualizer.prototype.renderErrors = function() {
    var curEntry = this.curTrace[this.curInstr];
    if (curEntry.event == 'exception' ||
            curEntry.event == 'uncaught_exception') {
        assert(curEntry.exception_msg);

        if (curEntry.exception_msg == "Unknown error") {
            this.domRoot.find("#errorOutput").html('Unknown error: ' +
                'Please email a bug report to philip@pgbovine.net');
        } else {
            this.domRoot.find("#errorOutput").html(
                htmlspecialchars(curEntry.exception_msg));
        }

        this.domRoot.find("#errorOutput").show();
        this.curLineExceptionMsg = curEntry.exception_msg;
    } else {
        if ( ! this.instrLimitReached) { // ugly, I know :/
            this.domRoot.find("#errorOutput").hide();
        }
    }
}

ExecutionVisualizer.prototype.renderVCRControls = function() {
    var totalInstrs = this.curTrace.length;
    var isLastInstr = (this.curInstr == (totalInstrs - 1));
    var vcrControls = this.domRoot.find("#vcrControls");

    if (isLastInstr) {
        if (this.instrLimitReached) {
            vcrControls.find("#curInstr").html("Instruction limit reached");
        } else {
            vcrControls.find("#curInstr").html("Program terminated");
        }
    } else {
        vcrControls.find("#curInstr").html("Step " +
                String(this.curInstr + 1) + " of " + String(totalInstrs - 1));
    }
}

ExecutionVisualizer.prototype.renderTraceArrows = function() {
    var curEntry = this.curTrace[this.curInstr];

    this.tcm.resetStepArrows();

    var shouldDisplayNextArrow = this.curInstr < this.curTrace.length - 1 &&
        curEntry.file && curEntry.line !== undefined;

    // Previous arrow
    if (this.curInstr > 0) {
        var prevEntry = this.curTrace[this.curInstr - 1];
        if (prevEntry.file && prevEntry.line !== undefined) {
            var overlap = shouldDisplayNextArrow &&
                curEntry.line == prevEntry.line &&
                curEntry.file == prevEntry.file;
            var arrow = {
                color: prevArrowColor,
                // If the arrows overlap, offset the previous arrow
                offset: overlap ? 0 : 1,
            };
            this.tcm.addArrowToLineAndFile(prevEntry.line - 1, prevEntry.file,
                arrow);
        }
    }

    // Next arrow
    if (shouldDisplayNextArrow) {
        var arrow = {
            color: nextArrowColor,
            offset: 1,
        };
        this.tcm.addArrowToLineAndFile(curEntry.line - 1, curEntry.file,
            arrow);
    }
}

ExecutionVisualizer.prototype.updateOutputMini = function() {
    assert(this.params.hideCode);
    var curEntry = this.curTrace[this.curInstr];
    var curToplevelLayout = this.curTraceLayouts[this.curInstr];
    this.renderDataStructures(curEntry, curToplevelLayout);
}


ExecutionVisualizer.prototype.renderStep = function(step) {
    assert(0 <= step);
    assert(step < this.curTrace.length);

    // ignore redundant calls
    if (this.curInstr == step) {
        return;
    }

    this.curInstr = step;
    this.updateOutput();
}


// is this visualizer in C or C++ mode? the eventual goal is to remove
// this special-case kludge check altogether and have the entire
// codebase be unified. but for now, keep C/C++ separate because I don't
// want to risk screwing up the visualizations for the other languages
ExecutionVisualizer.prototype.isCppMode = function() {
    return (this.params.lang === 'c' || this.params.lang === 'cpp');
}


// Pre-compute the layout of top-level heap objects for ALL execution
// points as soon as a trace is first loaded. The reason why we want to
// do this is so that when the user steps through execution points, the
// heap objects don't "jiggle around" (i.e., preserving positional
// invariance). Also, if we set up the layout objects properly, then we
// can take full advantage of d3 to perform rendering and transitions.
ExecutionVisualizer.prototype.precomputeCurTraceLayouts = function() {

    // curTraceLayouts is a list of top-level heap layout "objects" with the
    // same length as curTrace after it's been fully initialized. Each
    // element of curTraceLayouts is computed from the contents of its
    // immediate predecessor, thus ensuring that objects don't "jiggle
    // around" between consecutive execution points.
    //
    // Each top-level heap layout "object" is itself a LIST of LISTS of
    // object IDs, where each element of the outer list represents a row,
    // and each element of the inner list represents columns within a
    // particular row. Each row can have a different number of columns. Most
    // rows have exactly ONE column (representing ONE object ID), but rows
    // containing 1-D linked data structures have multiple columns. Each
    // inner list element looks something like ['row1', 3, 2, 1] where the
    // first element is a unique row ID tag, which is used as a key for d3 to
    // preserve "object constancy" for updates, transitions, etc. The row ID
    // is derived from the FIRST object ID inserted into the row. Since all
    // object IDs are unique, all row IDs will also be unique.

    /* This is a good, simple example to test whether objects "jiggle"

       x = [1, [2, [3, None]]]
       y = [4, [5, [6, None]]]

       x[1][1] = y[1]

*/
    this.curTraceLayouts = [];
    this.curTraceLayouts.push([]); // pre-seed with an empty sentinel to simplify the code

    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    assert(this.curTrace.length > 0);
    $.each(this.curTrace, function(i, curEntry) {
        var prevLayout = myViz.curTraceLayouts[myViz.curTraceLayouts.length - 1];

        // make a DEEP COPY of prevLayout to use as the basis for curLine
        var curLayout = $.extend(true /* deep copy */ , [], prevLayout);

        // initialize with all IDs from curLayout
        var idsToRemove = d3.map();
        $.each(curLayout, function(i, row) {
            for (var j = 1 /* ignore row ID tag */; j < row.length; j++) {
                idsToRemove.set(row[j], 1);
            }
        });

        var idsAlreadyLaidOut = d3.map(); // to prevent infinite recursion

        function curLayoutIndexOf(id) {
            for (var i = 0; i < curLayout.length; i++) {
                var row = curLayout[i];
                var index = row.indexOf(id);
                if (index > 0) { // index of 0 is impossible since it's the row ID tag
                    return {row: row, index: index}
                }
            }
            return null;
        }

        function isLinearObj(heapObj) {
            var hook_result = myViz.try_hook("isLinearObj", {heapObj:heapObj});
            if (hook_result[0]) return hook_result[1];

            return heapObj[0] == 'LIST' || heapObj[0] == 'TUPLE' || heapObj[0] == 'SET';
        }

        function recurseIntoObject(id, curRow, newRow) {
            // heuristic for laying out 1-D linked data structures: check for enclosing elements that are
            // structurally identical and then lay them out as siblings in the same "row"
            var heapObj = curEntry.heap[id];

            assert(heapObj);

            if (isLinearObj(heapObj)) {
                $.each(heapObj, function(ind, child) {
                    if (ind < 1) return; // skip type tag

                    if (!myViz.isPrimitiveType(child)) {
                        var childID = getRefID(child);

                        // comment this out to make "linked lists" that aren't
                        // structurally equivalent look good, e.g.,:
                        //   x = (1, 2, (3, 4, 5, 6, (7, 8, 9, None)))
                        //if (myViz.structurallyEquivalent(heapObj, curEntry.heap[childID])) {
                        //  updateCurLayout(childID, curRow, newRow);
                        //}
                        if (myViz.disableHeapNesting) {
                            updateCurLayout(childID, [], []);
                        }
                        else {
                            updateCurLayout(childID, curRow, newRow);
                        }
                    }
                });
            }
            else if (heapObj[0] == 'DICT') {
                $.each(heapObj, function(ind, child) {
                    if (ind < 1) return; // skip type tag

                    if (myViz.disableHeapNesting) {
                        var dictKey = child[0];
                        if (!myViz.isPrimitiveType(dictKey)) {
                            var keyChildID = getRefID(dictKey);
                            updateCurLayout(keyChildID, [], []);
                        }
                    }

                    var dictVal = child[1];
                    if (!myViz.isPrimitiveType(dictVal)) {
                        var childID = getRefID(dictVal);
                        if (myViz.structurallyEquivalent(heapObj, curEntry.heap[childID])) {
                            updateCurLayout(childID, curRow, newRow);
                        }
                        else if (myViz.disableHeapNesting) {
                            updateCurLayout(childID, [], []);
                        }
                    }
                });
            }
            else if (heapObj[0] == 'INSTANCE' || heapObj[0] == 'CLASS') {
                jQuery.each(heapObj, function(ind, child) {
                    var headerLength = (heapObj[0] == 'INSTANCE') ? 2 : 3;
                    if (ind < headerLength) return;

                    if (myViz.disableHeapNesting) {
                        var instKey = child[0];
                        if (!myViz.isPrimitiveType(instKey)) {
                            var keyChildID = getRefID(instKey);
                            updateCurLayout(keyChildID, [], []);
                        }
                    }

                    var instVal = child[1];
                    if (!myViz.isPrimitiveType(instVal)) {
                        var childID = getRefID(instVal);
                        if (myViz.structurallyEquivalent(heapObj, curEntry.heap[childID])) {
                            updateCurLayout(childID, curRow, newRow);
                        }
                        else if (myViz.disableHeapNesting) {
                            updateCurLayout(childID, [], []);
                        }
                    }
                });
            }
            else if ((heapObj[0] == 'C_ARRAY') || (heapObj[0] == 'C_STRUCT')) {
                updateCurLayoutAndRecurse(heapObj);
            }
        }


        // a krazy function!
        // id     - the new object ID to be inserted somewhere in curLayout
        //          (if it's not already in there)
        // curRow - a row within curLayout where new linked list
        //          elements can be appended onto (might be null)
        // newRow - a new row that might be spliced into curRow or appended
        //          as a new row in curLayout
        function updateCurLayout(id, curRow, newRow) {
            if (idsAlreadyLaidOut.has(id)) {
                return; // PUNT!
            }

            var curLayoutLoc = curLayoutIndexOf(id);

            var alreadyLaidOut = idsAlreadyLaidOut.has(id);
            idsAlreadyLaidOut.set(id, 1); // unconditionally set now

            // if id is already in curLayout ...
            if (curLayoutLoc) {
                var foundRow = curLayoutLoc.row;
                var foundIndex = curLayoutLoc.index;

                idsToRemove.remove(id); // this id is already accounted for!

                // very subtle ... if id hasn't already been handled in
                // this iteration, then splice newRow into foundRow. otherwise
                // (later) append newRow onto curLayout as a truly new row
                if (!alreadyLaidOut) {
                    // splice the contents of newRow right BEFORE foundIndex.
                    // (Think about when you're trying to insert in id=3 into ['row1', 2, 1]
                    //  to represent a linked list 3->2->1. You want to splice the 3
                    //  entry right before the 2 to form ['row1', 3, 2, 1])
                    if (newRow.length > 1) {
                        var args = [foundIndex, 0];
                        for (var i = 1; i < newRow.length; i++) { // ignore row ID tag
                            args.push(newRow[i]);
                            idsToRemove.remove(newRow[i]);
                        }
                        foundRow.splice.apply(foundRow, args);

                        // remove ALL elements from newRow since they've all been accounted for
                        // (but don't reassign it away to an empty list, since the
                        // CALLER checks its value. TODO: how to get rid of this gross hack?!?)
                        newRow.splice(0, newRow.length);
                    }
                }

                // recurse to find more top-level linked entries to append onto foundRow
                recurseIntoObject(id, foundRow, []);
            }
            else {
                // push id into newRow ...
                if (newRow.length == 0) {
                    newRow.push('row' + id); // unique row ID (since IDs are unique)
                }
                newRow.push(id);

                // recurse to find more top-level linked entries ...
                recurseIntoObject(id, curRow, newRow);


                // if newRow hasn't been spliced into an existing row yet during
                // a child recursive call ...
                if (newRow.length > 0) {
                    if (curRow && curRow.length > 0) {
                        // append onto the END of curRow if it exists
                        for (var i = 1; i < newRow.length; i++) { // ignore row ID tag
                            curRow.push(newRow[i]);
                        }
                    }
                    else {
                        // otherwise push to curLayout as a new row
                        //
                        // TODO: this might not always look the best, since we might
                        // sometimes want to splice newRow in the MIDDLE of
                        // curLayout. Consider this example:
                        //
                        // x = [1,2,3]
                        // y = [4,5,6]
                        // x = [7,8,9]
                        //
                        // when the third line is executed, the arrows for x and y
                        // will be crossed (ugly!) since the new row for the [7,8,9]
                        // object is pushed to the end (bottom) of curLayout. The
                        // proper behavior is to push it to the beginning of
                        // curLayout where the old row for 'x' used to be.
                        curLayout.push($.extend(true /* make a deep copy */ , [], newRow));
                    }

                    // regardless, newRow is now accounted for, so clear it
                    for (var i = 1; i < newRow.length; i++) { // ignore row ID tag
                        idsToRemove.remove(newRow[i]);
                    }
                    newRow.splice(0, newRow.length); // kill it!
                }

            }
        }


        function updateCurLayoutAndRecurse(elt) {
            if (!elt) return; // early bail out

            if (isHeapRef(elt, curEntry.heap)) {
                var id = getRefID(elt);
                updateCurLayout(id, null, []);
            }
            recurseIntoCStructArray(elt);
        }

        // traverse inside of C structs and arrays to find whether they
        // (recursively) contain any references to heap objects within
        // themselves. be able to handle arbitrary nesting!
        function recurseIntoCStructArray(val) {
            if (val[0] === 'C_ARRAY') {
                $.each(val, function(ind, elt) {
                    if (ind < 2) return;
                    updateCurLayoutAndRecurse(elt);
                });
            } else if (val[0] === 'C_STRUCT') {
                $.each(val, function(ind, kvPair) {
                    if (ind < 3) return;
                    updateCurLayoutAndRecurse(kvPair[1]);
                });
            }
        }

        // iterate through all globals and ordered stack frames and call updateCurLayout
        $.each(curEntry.ordered_globals, function(i, varname) {
            var val = curEntry.globals[varname];
            if (val !== undefined) { // might not be defined at this line, which is OKAY!
                // TODO: try to unify this behavior between C/C++ and other languages:
                if (myViz.isCppMode()) {
                    updateCurLayoutAndRecurse(val);
                } else {
                    if (!myViz.isPrimitiveType(val)) {
                        var id = getRefID(val);
                        updateCurLayout(id, null, []);
                    }
                }
            }
        });

        $.each(curEntry.stack_to_render, function(i, frame) {
            $.each(frame.ordered_varnames, function(xxx, varname) {
                var val = frame.encoded_locals[varname];
                // TODO: try to unify this behavior between C/C++ and other languages:
                if (myViz.isCppMode()) {
                    updateCurLayoutAndRecurse(val);
                } else {
                    if (!myViz.isPrimitiveType(val)) {
                        var id = getRefID(val);
                        if (id != 'VOID') {
                            updateCurLayout(id, null, []);
                        }
                    }
                }
            });
        });

        // Needed to show "temporarily lost" refs (when they are returned).
        if (curEntry.last_return_value) {
            var val = curEntry.last_return_value;
            var type = val[0];
            if (type == 'REF') {
                var refId = val[1];
                updateCurLayoutAndRecurse(val);
            }
        }

        // iterate through remaining elements of idsToRemove and REMOVE them from curLayout
        idsToRemove.forEach(function(id, xxx) {
            id = Number(id); // keys are stored as strings, so convert!!!
            $.each(curLayout, function(rownum, row) {
                var ind = row.indexOf(id);
                if (ind > 0) { // remember that index 0 of the row is the row ID tag
                    row.splice(ind, 1);
                }
            });
        });

        // now remove empty rows (i.e., those with only a row ID tag) from curLayout
        curLayout = curLayout.filter(function(row) {return row.length > 1});

        myViz.curTraceLayouts.push(curLayout);
    });

    this.curTraceLayouts.splice(0, 1); // remove seeded empty sentinel element
    assert (this.curTrace.length == this.curTraceLayouts.length);
}


var heapPtrSrcRE = /__heap_pointer_src_/;


var rightwardNudgeHack = true; // suggested by John DeNero, toggle with global

// This is the main event here!!!
//
// The "4.0" version of renderDataStructures was refactored to be much
// less monolithic and more modular. It was made possible by first
// creating a suite of frontend JS regression tests so that I felt more
// comfortable mucking around with the super-brittle code in this
// function. This version was created in April 2014. For reference,
// before refactoring, this function was 1,030 lines of convoluted code!
//
// (Also added the rightward nudge hack to make tree-like structures
// look more sane without any sophisticated graph rendering code. Thanks
// to John DeNero for this suggestion all the way back in Fall 2012.)
//
// The "3.0" version of renderDataStructures renders variables in
// a stack, values in a separate heap, and draws line connectors
// to represent both stack->heap object references and, more importantly,
// heap->heap references. This version was created in August 2012.
//
// The "2.0" version of renderDataStructures renders variables in
// a stack and values in a separate heap, with data structure aliasing
// explicitly represented via line connectors (thanks to jsPlumb lib).
// This version was created in September 2011.
//
// The ORIGINAL "1.0" version of renderDataStructures
// was created in January 2010 and rendered variables and values
// INLINE within each stack frame without any explicit representation
// of data structure aliasing. That is, aliased objects were rendered
// multiple times, and a unique ID label was used to identify aliases.
ExecutionVisualizer.prototype.renderDataStructures = function(curEntry, curToplevelLayout) {
    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    myViz.resetJsPlumbManager(); // very important!!!

    // for simplicity (but sacrificing some performance), delete all
    // connectors and redraw them from scratch. doing so avoids mysterious
    // jsPlumb connector alignment issues when the visualizer's enclosing
    // div contains, say, a "position: relative;" CSS tag
    // (which happens in the IPython Notebook)
    var existingConnectionEndpointIDs = d3.map();
    myViz.jsPlumbInstance.select({scope: 'varValuePointer'}).each(function(c) {
        // This is VERY crude, but to prevent multiple redundant HEAP->HEAP
        // connectors from being drawn with the same source and origin, we need to first
        // DELETE ALL existing HEAP->HEAP connections, and then re-render all of
        // them in each call to this function. The reason why we can't safely
        // hold onto them is because there's no way to guarantee that the
        // *__heap_pointer_src_<src id> IDs are consistent across execution points.
        //
        // thus, only add to existingConnectionEndpointIDs if this is NOT heap->heap
        if (!c.sourceId.match(heapPtrSrcRE)) {
            existingConnectionEndpointIDs.set(c.sourceId, c.targetId);
        }
    });

    var existingParentPointerConnectionEndpointIDs = d3.map();
    myViz.jsPlumbInstance.select({scope: 'frameParentPointer'}).each(function(c) {
        existingParentPointerConnectionEndpointIDs.set(c.sourceId, c.targetId);
    });


    // Heap object rendering phase:

    // count everything in curToplevelLayout as already rendered since we will render them
    // in d3 .each() statements
    $.each(curToplevelLayout, function(xxx, row) {
        for (var i = 0; i < row.length; i++) {
            var objID = row[i];
            var heapObjID = myViz.generateHeapObjID(objID, myViz.curInstr);
            myViz.jsPlumbManager.renderedHeapObjectIDs.set(heapObjID, 1);
        }
    });



    // use d3 to render the heap by mapping curToplevelLayout into <table class="heapRow">
    // and <td class="toplevelHeapObject"> elements

    // for simplicity, CLEAR this entire div every time, which totally
    // gets rid of the incremental benefits of using d3 for, say,
    // transitions or efficient updates. but it provides more
    // deterministic and predictable output for other functions. sigh, i'm
    // not really using d3 to the fullest, but oh wells!
    myViz.domRoot.find('#heap')
        .empty()
        .html('<div id="heapHeader">Objects</div>');


    var heapRows = myViz.domRootD3.select('#heap')
        .selectAll('table.heapRow')
        .attr('id', function(d, i){ return 'heapRow' + i; }) // add unique ID
        .data(curToplevelLayout, function(objLst) {
            return objLst[0]; // return first element, which is the row ID tag
        });


    // insert new heap rows
    heapRows.enter().append('table')
        //.each(function(objLst, i) {console.log('NEW ROW:', objLst, i);})
        .attr('id', function(d, i){ return 'heapRow' + i; }) // add unique ID
        .attr('class', 'heapRow');

    // delete a heap row
    var hrExit = heapRows.exit();
    hrExit
        .each(function(d, idx) {
            //console.log('DEL ROW:', d, idx);
            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();


    // update an existing heap row
    var toplevelHeapObjects = heapRows
        //.each(function(objLst, i) { console.log('UPDATE ROW:', objLst, i); })
        .selectAll('td.toplevelHeapObject')
        .data(function(d, i) {return d.slice(1, d.length);}, /* map over each row, skipping row ID tag */
                function(objID) {return objID;} /* each object ID is unique for constancy */);

    // insert a new toplevelHeapObject
    var tlhEnter = toplevelHeapObjects.enter().append('td')
        .attr('class', 'toplevelHeapObject')
        .attr('id', function(d, i) {return 'toplevel_heap_object_' + d;});

    // remember that the enter selection is added to the update
    // selection so that we can process it later ...

    // update a toplevelHeapObject
    toplevelHeapObjects
        .order() // VERY IMPORTANT to put in the order corresponding to data elements
        .each(function(objID, i) {
            //console.log('NEW/UPDATE ELT', objID);

            // TODO: add a smoother transition in the future
            // Right now, just delete the old element and render a new one in its place
            $(this).empty();

            if (myViz.isCppMode()) {
                // TODO: why might this be undefined?!? because the object
                // disappeared from the heap all of a sudden?!?
                if (curEntry.heap[objID] !== undefined) {
                    myViz.renderCompoundObject(objID, myViz.curInstr, $(this), true);
                }
            } else {
                myViz.renderCompoundObject(objID, myViz.curInstr, $(this), true);
            }
        });

    // delete a toplevelHeapObject
    var tlhExit = toplevelHeapObjects.exit();
    tlhExit
        .each(function(d, idx) {
            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();


    // Render globals and then stack frames using d3:


    // TODO: this sometimes seems buggy on Safari, so nix it for now:
    function highlightAliasedConnectors(d, i) {
        // if this row contains a stack pointer, then highlight its arrow and
        // ALL aliases that also point to the same heap object
        var stackPtrId = $(this).find('div.stack_pointer').attr('id');
        if (stackPtrId) {
            var foundTargetId = null;
            myViz.jsPlumbInstance.select({source: stackPtrId}).each(function(c) {foundTargetId = c.targetId;});

            // use foundTargetId to highlight ALL ALIASES
            myViz.jsPlumbInstance.select().each(function(c) {
                if (c.targetId == foundTargetId) {
                    c.setHover(true);
                    $(c.canvas).css("z-index", 2000); // ... and move it to the VERY FRONT
                }
                else {
                    c.setHover(false);
                }
            });
        }
    }

    function unhighlightAllConnectors(d, i) {
        myViz.jsPlumbInstance.select().each(function(c) {
            c.setHover(false);
        });
    }



    // TODO: coalesce code for rendering globals and stack frames,
    // since there's so much copy-and-paste grossness right now

    // render all global variables IN THE ORDER they were created by the program,
    // in order to ensure continuity:

    // Derive a list where each element contains varname
    // as long as value is NOT undefined.
    // (Sometimes entries in curEntry.ordered_globals are undefined,
    // so filter those out.)
    var realGlobalsLst = [];
    $.each(curEntry.ordered_globals, function(i, varname) {
        var val = curEntry.globals[varname];

        // (use '!==' to do an EXACT match against undefined)
        if (val !== undefined) { // might not be defined at this line, which is OKAY!
            realGlobalsLst.push(varname);
        }
    });

    var globalsID = myViz.generateID('globals');
    var globalTblID = myViz.generateID('global_table');

    if (realGlobalsLst.length == 0) {
        this.domRoot.find("#globals_area").hide();
    } else {
        this.domRoot.find("#globals_area").show();
    }

    var globalVarTable = myViz.domRootD3.select('#' + globalTblID)
        .selectAll('tr')
        .data(realGlobalsLst,
                function(d) {return d;} // use variable name as key
             );

    globalVarTable
        .enter()
        .append('tr')
        .attr('class', 'variableTr')
        .attr('id', function(d, i) {
            return myViz.generateID(varnameToCssID('global__' + d + '_tr')); // make globally unique (within the page)
        });


    var globalVarTableCells = globalVarTable
        .selectAll('td.stackFrameVar,td.stackFrameValue')
        .data(function(d, i){return [d, d];}) /* map varname down both columns */

        globalVarTableCells.enter()
        .append('td')
        .attr('class', function(d, i) {return (i == 0) ? 'stackFrameVar' : 'stackFrameValue';});

    // remember that the enter selection is added to the update
    // selection so that we can process it later ...

    // UPDATE
    globalVarTableCells
        .order() // VERY IMPORTANT to put in the order corresponding to data elements
        .each(function(varname, i) {
            if (i == 0) {
                $(this).html(varname);
            }
            else {
                // always delete and re-render the global var ...
                // NB: trying to cache and compare the old value using,
                // say -- $(this).attr('data-curvalue', valStringRepr) -- leads to
                // a mysterious and killer memory leak that I can't figure out yet
                $(this).empty();

                // make sure varname doesn't contain any weird
                // characters that are illegal for CSS ID's ...
                var varDivID = myViz.generateID('global__' + varnameToCssID(varname));

                // need to get rid of the old connector in preparation for rendering a new one:
                existingConnectionEndpointIDs.remove(varDivID);

                var val = curEntry.globals[varname];
                if (myViz.isPrimitiveType(val)) {
                    myViz.renderPrimitiveObject(val, $(this));
                }
                else if (val[0] === 'C_STRUCT' || val[0] === 'C_ARRAY') {
                    // C structs and arrays can be inlined in frames
                    myViz.renderCStructArray(val, myViz.curInstr, $(this));
                }
                else {
                    var heapObjID = myViz.generateHeapObjID(getRefID(val), myViz.curInstr);

                    if (myViz.textualMemoryLabels) {
                        var labelID = varDivID + '_text_label';
                        $(this).append('<div class="objectIdLabel" id="' + labelID + '">id' + getRefID(val) + '</div>');
                        $(this).find('div#' + labelID).hover(
                                function() {
                                    myViz.jsPlumbInstance.connect({source: labelID, target: heapObjID,
                                        scope: 'varValuePointer'});
                                },
                                function() {
                                    myViz.jsPlumbInstance.select({source: labelID}).detach();
                                });
                    }
                    else {
                        // add a stub so that we can connect it with a connector later.
                        // IE needs this div to be NON-EMPTY in order to properly
                        // render jsPlumb endpoints, so that's why we add an "&nbsp;"!
                        $(this).append('<div class="stack_pointer" id="' + varDivID + '">&nbsp;</div>');

                        assert(!myViz.jsPlumbManager.connectionEndpointIDs.has(varDivID));
                        myViz.jsPlumbManager.connectionEndpointIDs.set(varDivID, heapObjID);
                        //console.log('STACK->HEAP', varDivID, heapObjID);
                    }
                }
            }
        });



    globalVarTableCells.exit()
        .each(function(d, idx) {
            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();

    globalVarTable.exit()
        .each(function(d, i) {
            // detach all stack_pointer connectors for divs that are being removed
            $(this).find('.stack_pointer').each(function(i, sp) {
                existingConnectionEndpointIDs.remove($(sp).attr('id'));
            });

            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();


    // for aesthetics, hide globals if there aren't any globals to display
    if (curEntry.ordered_globals.length == 0) {
        this.domRoot.find('#' + globalsID).hide();
    }
    else {
        this.domRoot.find('#' + globalsID).show();
    }


    // holy cow, the d3 code for stack rendering is ABSOLUTELY NUTS!

    var stackDiv = myViz.domRootD3.select('#stack');

    // VERY IMPORTANT for selectAll selector to be SUPER specific here!
    var stackFrameDiv = stackDiv.selectAll('div.stackFrame,div.zombieStackFrame')
        .data(curEntry.stack_to_render, function(frame) {
            // VERY VERY VERY IMPORTANT for properly handling closures and nested functions
            // (see the backend code for more details)
            return frame.unique_hash;
        });

    var sfdEnter = stackFrameDiv.enter()
        .append('div')
        .attr('class', function(d, i) {return d.is_zombie ? 'zombieStackFrame' : 'stackFrame';})
        .attr('id', function(d, i) {return d.is_zombie ? myViz.generateID("zombie_stack" + i)
            : myViz.generateID("stack" + i);
        })
    // HTML5 custom data attributes
    .attr('data-frame_id', function(frame, i) {return frame.frame_id;})
        .attr('data-parent_frame_id', function(frame, i) {
            return (frame.parent_frame_id_list.length > 0) ? frame.parent_frame_id_list[0] : null;
        })
    .each(function(frame, i) {
        if ( ! myViz.drawParentPointers) {
            return;
        }
        // only run if myViz.drawParentPointers is true ...

        var my_CSS_id = $(this).attr('id');

        //console.log(my_CSS_id, 'ENTER');

        // render a parent pointer whose SOURCE node is this frame
        // i.e., connect this frame to p, where this.parent_frame_id == p.frame_id
        // (if this.parent_frame_id is null, then p is the global frame)
        if (frame.parent_frame_id_list.length > 0) {
            var parent_frame_id = frame.parent_frame_id_list[0];
            // tricky turkey!
            // ok this hack just HAPPENS to work by luck ... usually there will only be ONE frame
            // that matches this selector, but sometimes multiple frames match, in which case the
            // FINAL frame wins out (since parentPointerConnectionEndpointIDs is a map where each
            // key can be mapped to only ONE value). it so happens that the final frame winning
            // out looks "desirable" for some of the closure test cases that I've tried. but
            // this code is quite brittle :(
            myViz.domRoot.find('div#stack [data-frame_id=' + parent_frame_id + ']').each(function(i, e) {
                var parent_CSS_id = $(this).attr('id');
                //console.log('connect', my_CSS_id, parent_CSS_id);
                myViz.jsPlumbManager.parentPointerConnectionEndpointIDs.set(my_CSS_id, parent_CSS_id);
            });
        }
        else {
            // render a parent pointer to the global frame
            //console.log('connect', my_CSS_id, globalsID);
            // only do this if there are actually some global variables to display ...
            if (curEntry.ordered_globals.length > 0) {
                myViz.jsPlumbManager.parentPointerConnectionEndpointIDs.set(my_CSS_id, globalsID);
            }
        }

        // tricky turkey: render parent pointers whose TARGET node is this frame.
        // i.e., for all frames f such that f.parent_frame_id == my_frame_id,
        // connect f to this frame.
        // (make sure not to confuse frame IDs with CSS IDs!!!)
        var my_frame_id = frame.frame_id;
        myViz.domRoot.find('div#stack [data-parent_frame_id=' + my_frame_id + ']').each(function(i, e) {
            var child_CSS_id = $(this).attr('id');
            //console.log('connect', child_CSS_id, my_CSS_id);
            myViz.jsPlumbManager.parentPointerConnectionEndpointIDs.set(child_CSS_id, my_CSS_id);
        });
    });

    sfdEnter
        .append('div')
        .attr('class', 'stackFrameHeader')
        .html(function(frame, i) {

            // pretty-print lambdas and display other weird characters
            // (might contain '<' or '>' for weird names like <genexpr>)
            var funcName = htmlspecialchars(frame.func_name).replace('&lt;lambda&gt;', '\u03bb')
                .replace('\n', '<br/>');

            var headerLabel = funcName;

            // only display if you're someone's parent (unless showAllFrameLabels)
            if (frame.is_parent || myViz.showAllFrameLabels) {
                headerLabel = 'f' + frame.frame_id + ': ' + headerLabel;
            }

            // optional (btw, this isn't a CSS id)
            if (frame.parent_frame_id_list.length > 0) {
                var parentFrameID = frame.parent_frame_id_list[0];
                headerLabel = headerLabel + ' [parent=f' + parentFrameID + ']';
            }
            else if (myViz.showAllFrameLabels) {
                headerLabel = headerLabel + ' [parent=Global]';
            }

            return headerLabel;
        });

    sfdEnter
        .append('table')
        .attr('class', 'stackFrameVarTable');


    var stackVarTable = stackFrameDiv
        .order() // VERY IMPORTANT to put in the order corresponding to data elements
        .select('table').selectAll('tr')
        .data(function(frame) {
            // each list element contains a reference to the entire frame
            // object as well as the variable name
            // TODO: look into whether we can use d3 parent nodes to avoid
            // this hack ... http://bost.ocks.org/mike/nest/
            return frame.ordered_varnames.map(function(varname) {return {varname:varname, frame:frame};});
        },
        function(d) {
            // TODO: why would d ever be null?!? weird
            if (d) {
                return d.varname; // use variable name as key
            }
        }
        );

    stackVarTable
        .enter()
        .append('tr')
        .attr('class', 'variableTr')
        .attr('id', function(d, i) {
            return myViz.generateID(varnameToCssID(d.frame.unique_hash + '__' + d.varname + '_tr')); // make globally unique (within the page)
        });


    var stackVarTableCells = stackVarTable
        .selectAll('td.stackFrameVar,td.stackFrameValue')
        .data(function(d, i) {return [d, d] /* map identical data down both columns */;});

    stackVarTableCells.enter()
        .append('td')
        .attr('class', function(d, i) {return (i == 0) ? 'stackFrameVar' : 'stackFrameValue';});

    stackVarTableCells
        .order() // VERY IMPORTANT to put in the order corresponding to data elements
        .each(function(d, i) {
            var varname = d.varname;
            var frame = d.frame;

            if (i == 0) {
                if (varname == '__return__')
                    $(this).html('<span class="retval">Return<br/>value</span>');
                else
                    $(this).html(varname);
            }
            else {
                // always delete and re-render the stack var ...
                // NB: trying to cache and compare the old value using,
                // say -- $(this).attr('data-curvalue', valStringRepr) -- leads to
                // a mysterious and killer memory leak that I can't figure out yet
                $(this).empty();

                // make sure varname and frame.unique_hash don't contain any weird
                // characters that are illegal for CSS ID's ...
                var varDivID = myViz.generateID(varnameToCssID(frame.unique_hash + '__' + varname));

                // need to get rid of the old connector in preparation for rendering a new one:
                existingConnectionEndpointIDs.remove(varDivID);

                var val = frame.encoded_locals[varname];
                if (myViz.isPrimitiveType(val)) {
                    myViz.renderPrimitiveObject(val, $(this));
                }
                else if (val[0] === 'C_STRUCT' || val[0] === 'C_ARRAY') {

                    // C structs and arrays can be inlined in frames
                    myViz.renderCStructArray(val, myViz.curInstr, $(this));
                }
                else {
                    var heapObjID = myViz.generateHeapObjID(getRefID(val), myViz.curInstr);
                    if (myViz.textualMemoryLabels) {
                        var labelID = varDivID + '_text_label';
                        $(this).append('<div class="objectIdLabel" id="' + labelID + '">id' + getRefID(val) + '</div>');
                        $(this).find('div#' + labelID).hover(
                                function() {
                                    myViz.jsPlumbInstance.connect({source: labelID, target: heapObjID,
                                        scope: 'varValuePointer'});
                                },
                                function() {
                                    myViz.jsPlumbInstance.select({source: labelID}).detach();
                                });
                    }
                    else {
                        // add a stub so that we can connect it with a connector later.
                        // IE needs this div to be NON-EMPTY in order to properly
                        // render jsPlumb endpoints, so that's why we add an "&nbsp;"!
                        $(this).append('<div class="stack_pointer" id="' + varDivID + '">&nbsp;</div>');

                        assert(!myViz.jsPlumbManager.connectionEndpointIDs.has(varDivID));
                        myViz.jsPlumbManager.connectionEndpointIDs.set(varDivID, heapObjID);
                        //console.log('STACK->HEAP', varDivID, heapObjID);
                    }
                }
            }
        });


    stackVarTableCells.exit()
        .each(function(d, idx) {
            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();

    stackVarTable.exit()
        .each(function(d, i) {
            $(this).find('.stack_pointer').each(function(i, sp) {
                // detach all stack_pointer connectors for divs that are being removed
                existingConnectionEndpointIDs.remove($(sp).attr('id'));
            });

            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();

    stackFrameDiv.exit()
        .each(function(frame, i) {
            $(this).find('.stack_pointer').each(function(i, sp) {
                // detach all stack_pointer connectors for divs that are being removed
                existingConnectionEndpointIDs.remove($(sp).attr('id'));
            });

            var my_CSS_id = $(this).attr('id');

            //console.log(my_CSS_id, 'EXIT');

            // Remove all pointers where either the source or destination end is my_CSS_id
            existingParentPointerConnectionEndpointIDs.forEach(function(k, v) {
                if (k == my_CSS_id || v == my_CSS_id) {
                    //console.log('remove EPP', k, v);
                    existingParentPointerConnectionEndpointIDs.remove(k);
                }
            });

            $(this).empty(); // crucial for garbage collecting jsPlumb connectors!
        })
    .remove();


    // Rightward nudge hack to make tree-like structures look more sane
    // without any sophisticated graph rendering code. Thanks to John
    // DeNero for this suggestion in Fall 2012.
    //
    // This hack tries to ensure that all pointers that span different
    // rows point RIGHTWARD (as much as possible), which makes tree-like
    // structures look decent. e.g.,:
    //
    // t = [[['a', 'b'], ['c', 'd']], [[1,2], [3,4]]]
    //
    // Do it here since all of the divs have been rendered by now, but no
    // jsPlumb arrows have been rendered yet.
    if (rightwardNudgeHack) {
        // Basic idea: keep a set of all nudged ROWS for each nudger row, so
        // that when you get nudged, you can, in turn, nudge all of the rows
        // that you've nudged. this algorithm nicely takes care of the fact
        // that there might not be cycles in objects that you've nudged, but
        // there are cycles in entire rows.
        //
        // Key:   ID of .heapRow object that did the nudging
        // Value: set of .heapRow ID that were (transitively) nudged by this element
        //        (represented as a d3.map)
        var nudger_to_nudged_rows = {};

        // VERY IMPORTANT to sort these connector IDs in ascending order,
        // since I think they're rendered left-to-right, top-to-bottom in ID
        // order, so we want to run the nudging algorithm in that same order.
        var srcHeapConnectorIDs = myViz.jsPlumbManager.heapConnectionEndpointIDs.keys();
        srcHeapConnectorIDs.sort();

        $.each(srcHeapConnectorIDs, function(i, srcID) {
            var dstID = myViz.jsPlumbManager.heapConnectionEndpointIDs.get(srcID);

            var srcAnchorObject = myViz.domRoot.find('#' + srcID);
            var srcHeapObject = srcAnchorObject.closest('.heapObject');
            var dstHeapObject = myViz.domRoot.find('#' + dstID);
            assert(dstHeapObject.attr('class') == 'heapObject');

            var srcHeapRow = srcHeapObject.closest('.heapRow');
            var dstHeapRow = dstHeapObject.closest('.heapRow');

            var srcRowID = srcHeapRow.attr('id');
            var dstRowID = dstHeapRow.attr('id');

            // only consider nudging if srcID and dstID are on different rows
            if (srcRowID != dstRowID) {
                var srcAnchorLeft = srcAnchorObject.offset().left;
                var srcHeapObjectLeft = srcHeapObject.offset().left;
                var dstHeapObjectLeft = dstHeapObject.offset().left;

                // if srcAnchorObject is to the RIGHT of dstHeapObject, then nudge
                // dstHeapObject to the right
                if (srcAnchorLeft > dstHeapObjectLeft) {
                    // an extra nudge of 32px matches up pretty well with the
                    // current CSS padding around .toplevelHeapObject
                    var delta = (srcAnchorLeft - dstHeapObjectLeft) + 32;

                    // set margin rather than padding so that arrows tips still end
                    // at the left edge of the element.
                    // whoa, set relative CSS using +=, nice!
                    dstHeapObject.css('margin-left', '+=' + delta);

                    //console.log(srcRowID, 'nudged', dstRowID, 'by', delta);

                    var cur_nudgee_set = nudger_to_nudged_rows[srcRowID];
                    if (cur_nudgee_set === undefined) {
                        cur_nudgee_set = d3.map();
                        nudger_to_nudged_rows[srcRowID] = cur_nudgee_set;
                    }
                    cur_nudgee_set.set(dstRowID, 1 /* useless value */);

                    // now if dstRowID itself nudged some other nodes, then nudge
                    // all of its nudgees by delta as well
                    var dst_nudgee_set = nudger_to_nudged_rows[dstRowID];
                    if (dst_nudgee_set) {
                        dst_nudgee_set.forEach(function(k, v) {
                            // don't nudge if it's yourself, to make cycles look
                            // somewhat reasonable (although still not ideal). e.g.,:
                            //   x = [1,2]
                            //   y = [3,x]
                            //   x[1] = y
                            if (k != srcRowID) {
                                // nudge this entire ROW by delta as well
                                myViz.domRoot.find('#' + k).css('margin-left', '+=' + delta);

                                // then transitively add to entry for srcRowID
                                cur_nudgee_set.set(k, 1 /* useless value */);
                            }
                        });
                    }
                }
            }
        });
    }


    // NB: ugh, I'm not very happy about this hack, but it seems necessary
    // for embedding within sophisticated webpages such as IPython Notebook

    // delete all connectors. do this AS LATE AS POSSIBLE so that
    // (presumably) the calls to $(this).empty() earlier in this function
    // will properly garbage collect the connectors
    //
    // WARNING: for environment parent pointers, garbage collection doesn't seem to
    // be working as intended :(
    //
    // I suspect that this is due to the fact that parent pointers are SIBLINGS
    // of stackFrame divs and not children, so when stackFrame divs get destroyed,
    // their associated parent pointers do NOT.)
    myViz.jsPlumbInstance.reset();


    // use jsPlumb scopes to keep the different kinds of pointers separated
    function renderVarValueConnector(varID, valueID) {
        myViz.jsPlumbInstance.connect({source: varID, target: valueID, scope: 'varValuePointer'});
    }


    var totalParentPointersRendered = 0;

    function renderParentPointerConnector(srcID, dstID) {
        // SUPER-DUPER-ugly hack since I can't figure out a cleaner solution for now:
        // if either srcID or dstID no longer exists, then SKIP rendering ...
        if ((myViz.domRoot.find('#' + srcID).length == 0) ||
                (myViz.domRoot.find('#' + dstID).length == 0)) {
            return;
        }

        //console.log('renderParentPointerConnector:', srcID, dstID);

        myViz.jsPlumbInstance.connect({source: srcID, target: dstID,
            anchors: ["LeftMiddle", "LeftMiddle"],

            // 'horizontally offset' the parent pointers up so that they don't look as ugly ...
            //connector: ["Flowchart", { stub: 9 + (6 * (totalParentPointersRendered + 1)) }],

            // actually let's try a bezier curve ...
            connector: [ "Bezier", { curviness: 45 }],

            endpoint: ["Dot", {radius: 4}],
                //hoverPaintStyle: {lineWidth: 1, strokeStyle: connectorInactiveColor}, // no hover colors
            scope: 'frameParentPointer'});
        totalParentPointersRendered++;
    }

    if ( ! myViz.textualMemoryLabels) {
        // re-render existing connectors and then ...
        existingConnectionEndpointIDs.forEach(renderVarValueConnector);
        // add all the NEW connectors that have arisen in this call to renderDataStructures
        myViz.jsPlumbManager.connectionEndpointIDs.forEach(renderVarValueConnector);
    }
    // do the same for environment parent pointers
    if (myViz.drawParentPointers) {
        existingParentPointerConnectionEndpointIDs.forEach(renderParentPointerConnector);
        myViz.jsPlumbManager.parentPointerConnectionEndpointIDs.forEach(renderParentPointerConnector);
    }

    /*
       myViz.jsPlumbInstance.select().each(function(c) {
       console.log('CONN:', c.sourceId, c.targetId);
       });
       */
    //console.log('---', myViz.jsPlumbInstance.select().length, '---');


    function highlight_frame(frameID) {
        myViz.jsPlumbInstance.select().each(function(c) {
            // find the enclosing .stackFrame ...
            var stackFrameDiv = c.source.closest('.stackFrame');

            // if this connector starts in the selected stack frame ...
            if (stackFrameDiv.attr('id') == frameID) {
                // then HIGHLIGHT IT!
                c.setPaintStyle({lineWidth:1, strokeStyle: connectorBaseColor});
                c.endpoints[0].setPaintStyle({fillStyle: connectorBaseColor});
                //c.endpoints[1].setVisible(false, true, true); // JUST set right endpoint to be invisible

                $(c.canvas).css("z-index", 1000); // ... and move it to the VERY FRONT
            }
            // for heap->heap connectors
            else if (myViz.jsPlumbManager.heapConnectionEndpointIDs.has(c.endpoints[0].elementId)) {
                // NOP since it's already the color and style we set by default
            }
            // TODO: maybe this needs special consideration for C/C++ code? dunno
            else if (stackFrameDiv.length > 0) {
                // else unhighlight it
                // (only if c.source actually belongs to a stackFrameDiv (i.e.,
                //  it originated from the stack). for instance, in C there are
                //  heap pointers, but we doen't use heapConnectionEndpointIDs)
                c.setPaintStyle({lineWidth:1, strokeStyle: connectorInactiveColor});
                c.endpoints[0].setPaintStyle({fillStyle: connectorInactiveColor});
                //c.endpoints[1].setVisible(false, true, true); // JUST set right endpoint to be invisible

                $(c.canvas).css("z-index", 0);
            }
        });


        // clear everything, then just activate this one ...
        myViz.domRoot.find(".stackFrame").removeClass("highlightedStackFrame");
        myViz.domRoot.find('#' + frameID).addClass("highlightedStackFrame");
    }


    // highlight the top-most non-zombie stack frame or, if not available, globals
    var frame_already_highlighted = false;
    $.each(curEntry.stack_to_render, function(i, e) {
        if (e.is_highlighted) {
            highlight_frame(myViz.generateID('stack' + i));
            frame_already_highlighted = true;
        }
    });

    if (!frame_already_highlighted) {
        highlight_frame(myViz.generateID('globals'));
    }

    myViz.try_hook("end_renderDataStructures", {myViz:myViz});
}


// render a tabular visualization where each row is an execution step,
// and each column is a variable
ExecutionVisualizer.prototype.renderTabularView = function() {
    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    myViz.resetJsPlumbManager(); // very important!!!

    var allGlobalVars = [];
    // Key: function name
    // Value: list of ordered variables for function
    var funcNameToOrderedVars = {};
    var orderedFuncNames = []; // function names in order of appearance

    // iterate through the entire trace and find all global variables, and
    // all local variables in all functions, in order of appearance in the trace
    $.each(myViz.curTrace, function(i, elt) {
        $.each(elt.ordered_globals, function(i, g) {
            // don't add duplicates into this list,
            // but need to use a list to maintain ORDERING
            if ($.inArray(g, allGlobalVars) === -1) {
                allGlobalVars.push(g);
            }
        });

        $.each(elt.stack_to_render, function(i, sf) {
            var funcVarsList = funcNameToOrderedVars[sf.func_name];
            if (funcVarsList === undefined) {
                funcVarsList = [];
                funcNameToOrderedVars[sf.func_name] = funcVarsList;
                orderedFuncNames.push(sf.func_name);
            }
            $.each(sf.ordered_varnames, function(i, v) {
                // don't add duplicates into this list,
                // but need to use a list to maintain ORDERING
                // (ignore the special __return__ value)
                if ($.inArray(v, funcVarsList) === -1 && v !== '__return__') {
                    funcVarsList.push(v);
                }
            });
        });
    });

    /*
       console.log("allGlobalVars:", allGlobalVars);
       console.log("orderedFuncNames:", orderedFuncNames);
       $.each(funcNameToOrderedVars, function(k, v) {
       console.log("funcNameToOrderedVars[", k, "] =", v);
       });
       */

    var allVarNames = ['Step'];

    $.each(allGlobalVars, function(i, e) {
        allVarNames.push(e);
    });
    $.each(orderedFuncNames, function(i, funcName) {
        $.each(funcNameToOrderedVars[funcName], function(i, v) {
            allVarNames.push(funcName + ':' + v);
        });
    });

    // get the values of all objects in trace entry e
    function getAllOrderedValues(curEntry) {
        // HACK! start with a blank sentinel since the first column of the
        // table is the step number
        var allVarValues = [''];

        $.each(allGlobalVars, function(i, e) {
            allVarValues.push(curEntry.globals[e]);
        });

        // for local variables, grab only the values in the highlighted
        // frame (if any)
        var highlightedFrame = null;
        $.each(curEntry.stack_to_render, function(i, sf) {
            if (sf.is_highlighted) {
                highlightedFrame = sf;
            }
        });

        $.each(orderedFuncNames, function(i, funcName) {
            $.each(funcNameToOrderedVars[funcName], function(i, v) {
                var found = false;
                if (highlightedFrame && funcName == highlightedFrame.func_name) {
                    var obj = highlightedFrame.encoded_locals[v];
                    if (obj) {
                        allVarValues.push(obj);
                        found = true;
                    }
                }

                // push an empty value if not found since we want everything to
                // align with allVarNames
                if (!found) {
                    allVarValues.push(undefined);
                }
            });
        });

        // TODO: also walk up parent pointers to also display variable
        // values in enclosing frames

        return allVarValues;
    }


    var tblRoot = myViz.domRootD3.select("#optTabularView");
    var tbl = tblRoot.append("table");
    tbl.attr('id', 'optTable');

    var tHead = tbl.append('thead').attr('class', 'stepTableThead').append('tr');
    tHead.attr('class', 'stepTableTr');
    tHead.selectAll('thead td')
        .data(allVarNames)
        .enter()
        .append('td')
        .attr('class', 'stepTableTd')
        .html(function(d) { return d; })

        var tBody = tbl.append('tbody');
    tBody.attr('class', 'stepTableTbody');

    var stepsAndTraceEntries = [];
    $.each(myViz.curTrace, function(i, e) {
        stepsAndTraceEntries.push([i, e]);
    });

    var tr = tBody.selectAll('tbody tr')
        .data(stepsAndTraceEntries)
        .enter()
        .append("tr")
        .attr("step", function(d, i) { return i; })
        .attr("class", 'stepTableTr');

    var td = tr.selectAll("td")
        .data(function(e) { return getAllOrderedValues(e[1]); })
        .enter()
        .append("td")
        .attr('class', 'stepTableTd')
        .each(function(obj, i) {
            $(this).empty();

            // TODO: fixme -- this is super kludgy; must be a better way
            var step = parseInt($(this).closest('tr').attr('step'));

            if (i == 0) {
                $(this).html(step + 1); // one-indexed for readability
            }
            else {
                if (obj === undefined) {
                    // keep this table cell EMPTY
                }
                else {
                    myViz.renderNestedObject(obj, step, $(this), 'tabular');
                }
            }
        });


    myViz.jsPlumbInstance.reset();

    function renderTableVarValueConnector(varID, valueID) {
        myViz.jsPlumbInstance.connect({source: varID, target: valueID,
            scope: 'varValuePointer',
            // make it look more aesthetically pleasing:
            anchors: ['TopCenter', 'LeftMiddle']});
    }

    myViz.jsPlumbManager.connectionEndpointIDs.forEach(renderTableVarValueConnector);
}


// rendering functions, which all take a d3 dom element to anchor the
// new element to render
ExecutionVisualizer.prototype.renderPrimitiveObject = function(obj, d3DomElement) {
    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    if (this.try_hook("renderPrimitiveObject", {obj:obj, d3DomElement:d3DomElement})[0])
        return;

    var typ = typeof obj;

    if (obj == null) {
        d3DomElement.append('<span class="nullObj">' + this.getRealLabel('None') + '</span>');
    }
    else if (typ == "number") {
        d3DomElement.append('<span class="numberObj">' + obj + '</span>');
    }
    else if (typ == "boolean") {
        if (obj) {
            d3DomElement.append('<span class="boolObj">' + this.getRealLabel('True') + '</span>');
        }
        else {
            d3DomElement.append('<span class="boolObj">' + this.getRealLabel('False') + '</span>');
        }
    }
    else if (typ == "string") {
        // We have to manually since some other objects overflow the modal
        // Use the heap offset since it is the furthest left this object can go
        var heapTdOffset = $('#heap_td').offset().left;
        var rootWidth = this.domRoot.width();
        var maxWidth = parseInt(rootWidth - heapTdOffset);

        var $stringObj = this.generateStringObj(obj, maxWidth);
        d3DomElement.append($stringObj);
    }
    else if (typ == "object") {
        if (obj[0] == 'C_DATA') {
            var typeName = obj[2];
            // special cases for brevity:
            if (typeName === 'short int') {
                typeName = 'short';
            } else if (typeName === 'short unsigned int') {
                typeName = 'unsigned short';
            } else if (typeName === 'long int') {
                typeName = 'long';
            } else if (typeName === 'long long int') {
                typeName = 'long long';
            } else if (typeName === 'long unsigned int') {
                typeName = 'unsigned long';
            } else if (typeName === 'long long unsigned int') {
                typeName = 'unsigned long long int';
            }

            var isValidPtr = ((typeName === 'pointer') &&
                    (obj[3] !== '<UNINITIALIZED>') &&
                    (obj[3] !== '<UNALLOCATED>'));

            var addr = obj[1];
            var leader = '';
            if (myViz.debugMode) {
                leader = addr + '<br/>'; // prepend address
            }

            // prefix with 'cdata_' so that we can distinguish this from a
            // top-level heap ID generated by generateHeapObjID
            var cdataId = myViz.generateHeapObjID('cdata_' + addr, myViz.curInstr);

            if (isValidPtr) {
                // for pointers, put cdataId in the header
                d3DomElement.append('<div id="' + cdataId + '" class="cdataHeader">' + leader + typeName + '</div>');

                var ptrVal = obj[3];

                // add a stub so that we can connect it with a connector later.
                // IE needs this div to be NON-EMPTY in order to properly
                // render jsPlumb endpoints, so that's why we add an "&nbsp;"!
                var ptrSrcId = myViz.generateHeapObjID('ptrSrc_' + addr, myViz.curInstr);
                var ptrTargetId = myViz.generateHeapObjID('cdata_' + ptrVal, myViz.curInstr); // don't forget cdata_ prefix!

                var debugInfo = '';
                if (myViz.debugMode) {
                    debugInfo = ptrTargetId;
                }

                // make it really narrow so that the div doesn't STRETCH too wide
                d3DomElement.append('<div style="width: 10px;" id="' + ptrSrcId + '" class="cdataElt">&nbsp;' + debugInfo + '</div>');

                assert(!myViz.jsPlumbManager.connectionEndpointIDs.has(ptrSrcId));
                myViz.jsPlumbManager.connectionEndpointIDs.set(ptrSrcId, ptrTargetId);
                //console.log(ptrSrcId, '->', ptrTargetId);
            } else {
                // for non-pointers, put cdataId on the element itself, so that
                // pointers can point directly at the element, not the header
                d3DomElement.append('<div class="cdataHeader">' + leader + typeName + '</div>');

                var rep = '';
                if (typeof obj[3] === 'string') {
                    var literalStr = obj[3];
                    if (literalStr === '<UNINITIALIZED>') {
                        rep = '<span class="cdataUninit">?</span>';
                        //rep = '\uD83D\uDCA9'; // pile of poo emoji
                    } else if (literalStr == '<UNALLOCATED>') {
                        rep = '\uD83D\uDC80'; // skull emoji
                    } else {
                        // a regular string
                        literalStr = literalStr.replace(new RegExp("\n", 'g'), '\\n'); // replace ALL
                        literalStr = literalStr.replace(new RegExp("\t", 'g'), '\\t'); // replace ALL
                        literalStr = literalStr.replace(new RegExp('\"', 'g'), '\\"'); // replace ALL

                            // print as a SINGLE-quoted string literal (to emulate C-style chars)
                            literalStr = "'" + literalStr + "'";
                        rep = htmlspecialchars(literalStr);
                    }
                } else {
                    rep = htmlspecialchars(obj[3]);
                }

                d3DomElement.append('<div id="' + cdataId + '" class="cdataElt">' + rep + '</div>');
            }
        } else {
            assert(obj[0] == 'SPECIAL_FLOAT' || obj[0] == 'JS_SPECIAL_VAL');
            d3DomElement.append('<span class="numberObj">' + obj[1] + '</span>');
        }
    }
    else {
        assert(false);
    }
}

/**
 * @param {string} str The string to generate the element from.
 * @param {number} width The width of this object
 * @return {jQuery} A nicely formatted string element.
 */
ExecutionVisualizer.prototype.generateStringObj = function(str, width) {
    // Prevent HTML/script injection
    var literalStr = htmlsanitize(str);
    literalStr = literalStr.replace(/"/g, '\\"');

    literalStr = literalStr.replace(/\n/g, '\\n');
    literalStr = literalStr.replace(/\t/g, '\\t');
    literalStr = literalStr.replace(/\r/g, '\\r');
    literalStr = literalStr.replace(/\\./g, function(match) {
        // Highlight whitespace escape characters nicely
        return '<span class="characterEscape">' + match + '</span>';
    });

    return $('<span class="stringObj"></span>')
        .attr('style', 'max-width: ' + width + 'px;')
        // print as a double-quoted string literal
        .html('"' + literalStr + '"');
}

ExecutionVisualizer.prototype.renderNestedObject = function(obj, stepNum, d3DomElement) {
    if (this.isPrimitiveType(obj)) {
        this.renderPrimitiveObject(obj, d3DomElement);
    }
    else {
        if (obj[0] === 'REF') {
            // obj is a ["REF", <int>] so dereference the 'pointer' to render that object
            this.renderCompoundObject(getRefID(obj), stepNum, d3DomElement, false);
        } else {
            assert(obj[0] === 'C_STRUCT' || obj[0] === 'C_ARRAY');
            this.renderCStructArray(obj, stepNum, d3DomElement);
        }
    }
}

ExecutionVisualizer.prototype.renderCompoundObject =
        function(objID, stepNum, d3DomElement, isTopLevel) {
    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    var heapObjID = this.generateHeapObjID(objID, stepNum);

    var hasAlreadyRendered = ! isTopLevel &&
        this.jsPlumbManager.renderedHeapObjectIDs.has(heapObjID);
    if (hasAlreadyRendered) {
        this.renderCompoundJsPlumbArrows(objID, heapObjID, d3DomElement);
        return;
    }

    // wrap ALL compound objects in a heapObject div so that jsPlumb
    // connectors can point to it:
    d3DomElement.append('<div class="heapObject" id="' + heapObjID + '"></div>');
    d3DomElement = myViz.domRoot.find('#' + heapObjID); // TODO: maybe inefficient

    myViz.jsPlumbManager.renderedHeapObjectIDs.set(heapObjID, 1);

    var curHeap = myViz.curTrace[stepNum].heap;
    var obj = curHeap[objID];
    assert($.isArray(obj));

    // prepend the type label with a memory address label
    var typeLabelPrefix = '';
    if (myViz.textualMemoryLabels) {
        if (this.heapObjectIsFromReturn(objID)) {
            typeLabelPrefix += '(returned) ';
        }
        typeLabelPrefix += 'id' + objID + ':';
    }

    var hook_result = myViz.try_hook("renderCompoundObject", {
        objID:objID,
        d3DomElement:d3DomElement,
        isTopLevel:isTopLevel,
        obj:obj,
        typeLabelPrefix:typeLabelPrefix,
        stepNum:stepNum,
        myViz:myViz
    });
    if (hook_result[0]) return;

    if (obj[0] == 'LIST' || obj[0] == 'TUPLE' || obj[0] == 'SET' || obj[0] == 'DICT') {
        this.renderCompoundCollection(obj, stepNum, typeLabelPrefix, d3DomElement);
    } else if (obj[0] == 'INSTANCE' || obj[0] == 'CLASS') {
        this.renderCompoundClassInstance(obj, stepNum, typeLabelPrefix, d3DomElement);
    } else if (obj[0] == 'INSTANCE_PPRINT') {
        d3DomElement.append('<div class="typeLabel">' + typeLabelPrefix + obj[1] + ' instance</div>');

        strRepr = htmlspecialchars(obj[2]); // escape strings!
        d3DomElement.append('<table class="customObjTbl"><tr><td class="customObjElt">' + strRepr + '</td></tr></table>');
    } else if (obj[0] == 'FUNCTION') {
        this.renderCompoundFunction(obj, typeLabelPrefix, d3DomElement);
    } else if (obj[0] == 'JS_FUNCTION') {
        this.renderCompoundJsFunction(obj, stepNum, typeLabelPrefix, d3DomElement);
    } else if (obj[0] == 'HEAP_PRIMITIVE') {
        this.renderCompoundHeapPrimitive(obj, typeLabelPrefix, d3DomElement);
    } else if (obj[0] == 'C_STRUCT' || obj[0] == 'C_ARRAY') {
        myViz.renderCStructArray(obj, stepNum, d3DomElement);
    } else {
        // render custom data type
        assert(obj.length == 2);

        var typeName = obj[0];
        var strRepr = obj[1];

        strRepr = htmlspecialchars(strRepr); // escape strings!

        d3DomElement.append('<div class="typeLabel">' + typeLabelPrefix + typeName + '</div>');
        d3DomElement.append('<table class="customObjTbl"><tr><td class="customObjElt">' + strRepr + '</td></tr></table>');
    }
}

ExecutionVisualizer.prototype.renderCompoundCollection = function(
        obj, stepNum, typeLabelPrefix, $element) {
    var label = obj[0].toLowerCase();

    assert(obj.length >= 1);
    if (obj.length == 1) {
        $element.append('<div class="typeLabel">' + typeLabelPrefix + ' empty ' + myViz.getRealLabel(label) + '</div>');
        return;
    }

    $element.append('<div class="typeLabel">' + typeLabelPrefix + myViz.getRealLabel(label) + '</div>');
    $element.append('<table class="' + label + 'Tbl"></table>');
    var tbl = $element.children('table');

    if (obj[0] == 'LIST' || obj[0] == 'TUPLE') {
        tbl.append('<tr></tr><tr></tr>');
        var headerTr = tbl.find('tr:first');
        var contentTr = tbl.find('tr:last');
        var myViz = this;
        $.each(obj, function(ind, val) {
            if (ind < 1) return; // skip type tag and ID entry

            // add a new column and then pass in that newly-added column
            // as $element to the recursive call to child:
            headerTr.append('<td class="' + label + 'Header"></td>');
            headerTr.find('td:last').append(ind - 1);

            contentTr.append('<td class="'+ label + 'Elt"></td>');
            myViz.renderNestedObject(val, stepNum, contentTr.find('td:last'));
        });
    } else if (obj[0] == 'SET') {
        // create an R x C matrix:
        var numElts = obj.length - 1;

        // gives roughly a 3x5 rectangular ratio, square is too, err,
        // 'square' and boring
        var numRows = Math.round(Math.sqrt(numElts));
        if (numRows > 3) {
            numRows -= 1;
        }

        var numCols = Math.round(numElts / numRows);
        // round up if not a perfect multiple:
        if (numElts % numRows) {
            numCols += 1;
        }

        var myViz = this;
        jQuery.each(obj, function(ind, val) {
            if (ind < 1) return; // skip 'SET' tag

            if (((ind - 1) % numCols) == 0) {
                tbl.append('<tr></tr>');
            }

            var curTr = tbl.find('tr:last');
            curTr.append('<td class="setElt"></td>');
            myViz.renderNestedObject(val, stepNum, curTr.find('td:last'));
        });
    } else if (obj[0] == 'DICT') {
        var myViz = this;
        $.each(obj, function(ind, kvPair) {
            if (ind < 1) return; // skip 'DICT' tag

            tbl.append('<tr class="dictEntry"><td class="dictKey"></td><td class="dictVal"></td></tr>');
            var newRow = tbl.find('tr:last');
            var keyTd = newRow.find('td:first');
            var valTd = newRow.find('td:last');

            var key = kvPair[0];
            var val = kvPair[1];

            myViz.renderNestedObject(key, stepNum, keyTd);
            myViz.renderNestedObject(val, stepNum, valTd);
        });
    }
}

ExecutionVisualizer.prototype.renderCompoundClassInstance = function(
        obj, stepNum, typeLabelPrefix, $element) {
    var isInstance = (obj[0] == 'INSTANCE');
    var headerLength = isInstance ? 2 : 3;

    assert(obj.length >= headerLength);

    if (isInstance) {
        $element.append('<div class="typeLabel">' + typeLabelPrefix + obj[1] + ' ' + this.getRealLabel('instance') + '</div>');
    } else {
        var superclassStr = '';
        if (obj[2].length > 0) {
            superclassStr += ('[extends ' + obj[2].join(', ') + '] ');
        }
        $element.append('<div class="typeLabel">' + typeLabelPrefix + obj[1] + ' class ' + superclassStr +
                '<br/>' + '<a href="#" id="attrToggleLink">hide attributes</a>' + '</div>');
    }

    // right now, let's NOT display class members, since that clutters
    // up the display too much. in the future, consider displaying
    // class members in a pop-up pane on mouseover or mouseclick
    // actually nix what i just said above ...
    //if (!isInstance) return;

    if (obj.length > headerLength) {
        var lab = isInstance ? 'inst' : 'class';
        $element.append('<table class="' + lab + 'Tbl"></table>');

        var tbl = $element.children('table');

        var myViz = this;
        $.each(obj, function(ind, kvPair) {
            if (ind < headerLength) return; // skip header tags

            tbl.append('<tr class="' + lab + 'Entry"><td class="' + lab + 'Key"></td><td class="' + lab + 'Val"></td></tr>');

            var newRow = tbl.find('tr:last');
            var keyTd = newRow.find('td:first');
            var valTd = newRow.find('td:last');

            // the keys should always be strings, so render them directly (and without quotes):
            // (actually this isn't the case when strings are rendered on the heap)
            if (typeof kvPair[0] == "string") {
                // common case ...
                var attrnameStr = htmlspecialchars(kvPair[0]);
                keyTd.append('<span class="keyObj">' + attrnameStr + '</span>');
            } else {
                // when strings are rendered as heap objects ...
                myViz.renderNestedObject(kvPair[0], stepNum, keyTd);
            }

            // values can be arbitrary objects, so recurse:
            myViz.renderNestedObject(kvPair[1], stepNum, valTd);
        });
    }

    // class attributes can be displayed or hidden, so as not to
    // CLUTTER UP the display with a ton of attributes, especially
    // from imported modules and custom types created from, say,
    // collections.namedtuple
    if ( ! isInstance) {
        // super kludgy! use a global selector $ to get at the DOM
        // element, which should be okay since IDs should be globally
        // unique on a page, even with multiple ExecutionVisualizer
        // instances ... but still feels dirty to me since it violates
        // my "no using raw $(__) selectors for jQuery" convention :/
        var myViz = this;
        $($element.selector + ' .typeLabel #attrToggleLink').click(function() {
            var elt = $($element.selector + ' .classTbl');
            elt.toggle();
            $(this).html((elt.is(':visible') ? 'hide' : 'show') + ' attributes');

            if (elt.is(':visible')) {
                myViz.classAttrsHidden[$element.selector] = false;
                $(this).html('hide attributes');
            }
            else {
                myViz.classAttrsHidden[$element.selector] = true;
                $(this).html('show attributes');
            }

            myViz.redrawConnectors(); // redraw all arrows!

            return false; // so that the <a href="#"> doesn't reload the page
        });

        // "remember" whether this was hidden earlier during this
        // visualization session
        if (myViz.classAttrsHidden[$element.selector]) {
            $($element.selector + ' .classTbl').hide();
            $($element.selector + ' .typeLabel #attrToggleLink').html('show attributes');
        }
    }
}

ExecutionVisualizer.prototype.renderCompoundFunction = function(
        obj, typeLabelPrefix, $element) {
    assert(obj.length == 3);

    // pretty-print lambdas and display other weird characters:
    var funcName = htmlspecialchars(obj[1]).replace('&lt;lambda&gt;', '\u03bb');
    var parentFrameID = obj[2]; // optional

    if ( ! this.compactFuncLabels) {
        var label = typeLabelPrefix + this.getRealLabel('function');
        $element.append('<div class="typeLabel">' + label + '</div>');
    }

    var funcPrefix = this.compactFuncLabels ? 'func' : '';

    if (parentFrameID) {
        $element.append('<div class="funcObj">' + funcPrefix + ' ' + funcName + ' [parent=f'+ parentFrameID + ']</div>');
    } else if (this.showAllFrameLabels) {
        $element.append('<div class="funcObj">' + funcPrefix + ' ' + funcName + ' [parent=Global]</div>');
    } else {
        $element.append('<div class="funcObj">' + funcPrefix + ' ' + funcName + '</div>');
    }
}

ExecutionVisualizer.prototype.renderCompoundJsFunction = function(
        obj, stepNum, typeLabelPrefix, $element) {
    // JavaScript function
    assert(obj.length == 5);
    var funcName = htmlspecialchars(obj[1]);
    var funcCode = typeLabelPrefix + htmlspecialchars(obj[2]);
    var parentFrameID = obj[4];

    // Either null or a non-empty list of key-value pairs
    var funcProperties = obj[3];

    if ( ! funcProperties && ! parentFrameID && ! this.showAllFrameLabels) {
        // compact form:
        $element.append('<pre class="funcCode">' + funcCode + '</pre>');
        return;
    }

    $element.append('<table class="classTbl"></table>');
    var tbl = $element.children('table');
    tbl.append('<tr><td class="funcCod" colspan="2"><pre class="funcCode">' + funcCode + '</pre>' + '</td></tr>');

    if (funcProperties) {
        assert(funcProperties.length > 0);
        var that = this;
        $.each(funcProperties, function(ind, kvPair) {
            tbl.append('<tr class="classEntry"><td class="classKey"></td><td class="classVal"></td></tr>');
            var newRow = tbl.find('tr:last');
            var keyTd = newRow.find('td:first');
            var valTd = newRow.find('td:last');
            keyTd.append('<span class="keyObj">' + htmlspecialchars(kvPair[0]) + '</span>');
            that.renderNestedObject(kvPair[1], stepNum, valTd);
        });
    }

    if (parentFrameID) {
        tbl.append('<tr class="classEntry"><td class="classKey">parent</td><td class="classVal">' + 'f' + parentFrameID + '</td></tr>');
    } else if (this.showAllFrameLabels) {
        tbl.append('<tr class="classEntry"><td class="classKey">parent</td><td class="classVal">' + 'global' + '</td></tr>');
    }
}

ExecutionVisualizer.prototype.renderCompoundHeapPrimitive = function(
        obj, typeLabelPrefix, $element) {
    assert(obj.length == 3);

    var typeName = obj[1];
    var primitiveVal = obj[2];

    // add a bit of padding to heap primitives, for aesthetics
    $element.append('<div class="heapPrimitive"></div>');
    $element.find('div.heapPrimitive')
        .append('<div class="typeLabel">' + typeLabelPrefix + typeName + '</div>');
    this.renderPrimitiveObject(primitiveVal, $element.find('div.heapPrimitive'));
}

/**
 * @param {number} objID The JVM object ID.
 * @param {number} heapObjID The JVM object ID.
 * @see generateHeapObjID for heapObjID info
 * @param {jQuery} $element The element to render to.
 */
ExecutionVisualizer.prototype.renderCompoundJsPlumbArrows = function(
        objID, heapObjID, $element) {
    var srcDivID = this.generateID('heap_pointer_src_' +
        this.jsPlumbManager.heap_pointer_src_id);

    // just make sure each source has a UNIQUE ID
    this.jsPlumbManager.heap_pointer_src_id++;

    if (this.textualMemoryLabels) {
        var labelID = srcDivID + '_text_label';
        $element.append($('<div class="objectIdLabel"></div>')
            .attr('id', labelID)
            .text('id' + objID));

        var that = this;
        this.domRoot.find('div#' + labelID).hover(function() {
            that.jsPlumbInstance.connect({
                source: labelID,
                target: heapObjID,
                scope: 'varValuePointer',
            });
        }, function() {
            that.jsPlumbInstance.select({
                source: labelID,
            }).detach();
        });
    } else {
        /*
         * Render jsPlumb arrow source since this heap object has already
         * been rendered (or will be rendered soon)
         */

        /*
         * Add a stub so that we can connect it with a connector later.
         * IE needs this div to be NON-EMPTY in order to properly
         * render jsPlumb endpoints, so that's why we add an "&nbsp;"!
         */
        $element.append('<div id="' + srcDivID + '">&nbsp;</div>');

        assert( ! this.jsPlumbManager.connectionEndpointIDs.has(srcDivID));
        this.jsPlumbManager.connectionEndpointIDs.set(srcDivID, heapObjID);
        //console.log('HEAP->HEAP', srcDivID, heapObjID);

        assert( ! this.jsPlumbManager.heapConnectionEndpointIDs.has(srcDivID));
        this.jsPlumbManager.heapConnectionEndpointIDs.set(srcDivID, heapObjID);
    }
}

/**
 * If the given object was freshly returned from a method.
 * If so, it will not be assigned to a variable yet.
 *
 * @param {number} objID The object ID to check for
 */
ExecutionVisualizer.prototype.heapObjectIsFromReturn = function(objID) {
    var curEntry = this.curTrace[this.curInstr];
    if (curEntry.last_return_value) {
        var val = curEntry.last_return_value;
        var type = val[0];
        if (type == 'REF' && val[1] == objID) {
            return true;
        }
    }
    return false;
}

ExecutionVisualizer.prototype.renderCStructArray = function(obj, stepNum, d3DomElement) {
    var myViz = this; // to prevent confusion of 'this' inside of nested functions

    if (obj[0] == 'C_STRUCT') {
        assert(obj.length >= 3);
        var addr = obj[1];
        var typename = obj[2];

        var leader = '';
        if (myViz.debugMode) {
            leader = addr + '<br/>';
        }
        if (myViz.params.lang === 'cpp') {
            // call it 'object' instead of 'struct'
            d3DomElement.append('<div class="typeLabel">' + leader + 'object ' + typename + '</div>');
        } else {
            d3DomElement.append('<div class="typeLabel">' + leader + 'struct ' + typename + '</div>');
        }

        if (obj.length > 3) {
            d3DomElement.append('<table class="instTbl"></table>');

            var tbl = d3DomElement.children('table');

            $.each(obj, function(ind, kvPair) {
                if (ind < 3) return; // skip header tags

                tbl.append('<tr class="instEntry"><td class="instKey"></td><td class="instVal"></td></tr>');

                var newRow = tbl.find('tr:last');
                var keyTd = newRow.find('td:first');
                var valTd = newRow.find('td:last');

                // the keys should always be strings, so render them directly (and without quotes):
                // (actually this isn't the case when strings are rendered on the heap)
                assert(typeof kvPair[0] == "string");
                // common case ...
                var attrnameStr = htmlspecialchars(kvPair[0]);
                keyTd.append('<span class="keyObj">' + attrnameStr + '</span>');

                // values can be arbitrary objects, so recurse:
                myViz.renderNestedObject(kvPair[1], stepNum, valTd);
            });
        }
    } else {
        assert(obj[0] == 'C_ARRAY');
        assert(obj.length >= 2);
        var addr = obj[1];

        var leader = '';
        if (myViz.debugMode) {
            leader = addr + '<br/>';
        }
        d3DomElement.append('<div class="typeLabel">' + leader + 'array</div>');
        d3DomElement.append('<table class="cArrayTbl"></table>');
        var tbl = d3DomElement.children('table');

        tbl.append('<tr></tr><tr></tr>');
        var headerTr = tbl.find('tr:first');
        var contentTr = tbl.find('tr:last');
        $.each(obj, function(ind, val) {
            if (ind < 2) return; // skip 'C_ARRAY' and addr

            // add a new column and then pass in that newly-added column
            // as d3DomElement to the recursive call to child:
            headerTr.append('<td class="cArrayHeader"></td>');
            headerTr.find('td:last').append(ind - 2 /* adjust */);

            contentTr.append('<td class="cArrayElt"></td>');
            myViz.renderNestedObject(val, stepNum, contentTr.find('td:last'));
        });
    }
}

ExecutionVisualizer.prototype.redrawConnectors = function() {
    this.jsPlumbInstance.repaintEverything();
}


ExecutionVisualizer.prototype.getRealLabel = function(label) {
    if (this.params.lang === 'js' || this.params.lang === 'ts' ||
            this.params.lang === 'ruby' || this.params.lang === 'java') {
        if (label === 'list') {
            return 'array';
        } else if (label === 'instance') {
            return 'object';
        } else if (label === 'True') {
            return 'true';
        } else if (label === 'False') {
            return 'false';
        }
    }

    if (this.params.lang === 'js') {
        if (label === 'dict') {
            return 'Map';
        } else if (label === 'set') {
            return 'Set';
        }
    }

    if (this.params.lang === 'ruby') {
        if (label === 'dict') {
            return 'hash';
        } else if (label === 'set') {
            return 'Set'; // the Ruby Set class is capitalized
        } else if (label === 'function') {
            return 'method';
        } else if (label === 'None') {
            return 'nil';
        } else if (label === 'Global frame') {
            return 'Global Object';
        }
    }

    if (this.params.lang === 'java') {
        if (label === 'None') {
            return 'null';
        }
    }

    // default fallthrough case
    return label;
};


// Utilities

/* colors - see pytutor.css for more colors */

var brightRed = '#e93f34';

var connectorBaseColor = '#005583';
var connectorHighlightColor = brightRed;
var connectorInactiveColor = '#cccccc';

var breakpointColor = brightRed;

// Unicode arrow types: '\u21d2', '\u21f0', '\u2907'
var nextArrowColor = brightRed;
var prevArrowColor = '#3f3fe9';

function assert(cond) {
    if (!cond) {
        alert("Assertion Failure (see console log for backtrace)");
        throw 'Assertion Failure';
    }
}

// taken from http://www.toao.net/32-my-htmlspecialchars-function-for-javascript
function htmlspecialchars(str) {
    if (typeof(str) == "string") {
        str = str.replace(/&/g, "&amp;"); /* must do &amp; first */

        // ignore these for now ...
        //str = str.replace(/"/g, "&quot;");
        //str = str.replace(/'/g, "&#039;");

        str = str.replace(/</g, "&lt;");
        str = str.replace(/>/g, "&gt;");

        // replace spaces:
        str = str.replace(/ /g, "&nbsp;");

        // replace tab as four spaces:
        str = str.replace(/\t/g, "&nbsp;&nbsp;&nbsp;&nbsp;");
    }
    return str;
}


// same as htmlspecialchars except don't worry about expanding spaces or
// tabs since we want proper word wrapping in divs.
function htmlsanitize(str) {
    if (typeof(str) == "string") {
        str = str.replace(/&/g, "&amp;"); /* must do &amp; first */

        str = str.replace(/</g, "&lt;");
        str = str.replace(/>/g, "&gt;");
    }
    return str;
}


// make sure varname doesn't contain any weird
// characters that are illegal for CSS ID's ...
//
// I know for a fact that iterator tmp variables named '_[1]'
// are NOT legal names for CSS ID's.
// I also threw in '{', '}', '(', ')', '<', '>' as illegal characters.
//
// also some variable names are like '.0' (for generator expressions),
// and '.' seems to be illegal.
//
// also '=', '!', and '?' are common in Ruby names, so escape those as well
//
// also spaces are illegal, so convert to '_'
// TODO: what other characters are illegal???
var lbRE = new RegExp('\\[|{|\\(|<', 'g');
    var rbRE = new RegExp('\\]|}|\\)|>', 'g');
function varnameToCssID(varname) {
    // make sure to REPLACE ALL (using the 'g' option)
    // rather than just replacing the first entry
    return varname.replace(lbRE, 'LeftB_')
        .replace(rbRE, '_RightB')
        .replace(/[!]/g, '_BANG_')
        .replace(/[?]/g, '_QUES_')
        .replace(/[:]/g, '_COLON_')
        .replace(/[=]/g, '_EQ_')
        .replace(/[.]/g, '_DOT_')
        .replace(/ /g, '_');
}


// compare two JSON-encoded compound objects for structural equivalence:
ExecutionVisualizer.prototype.structurallyEquivalent = function(obj1, obj2) {
    // punt if either isn't a compound type
    if (this.isPrimitiveType(obj1) || this.isPrimitiveType(obj2)) {
        return false;
    }

    // must be the same compound type
    if (obj1[0] != obj2[0]) {
        return false;
    }

    // must have the same number of elements or fields
    if (obj1.length != obj2.length) {
        return false;
    }

    // for a list or tuple, same size (e.g., a cons cell is a list/tuple of size 2)
    if (obj1[0] == 'LIST' || obj1[0] == 'TUPLE') {
        return true;
    }
    else {
        var startingInd = -1;

        if (obj1[0] == 'DICT') {
            startingInd = 2;
        }
        else if (obj1[0] == 'INSTANCE') {
            startingInd = 3;
        }
        else {
            return false; // punt on all other types
        }

        var obj1fields = d3.map();

        // for a dict or object instance, same names of fields (ordering doesn't matter)
        for (var i = startingInd; i < obj1.length; i++) {
            obj1fields.set(obj1[i][0], 1); // use as a set
        }

        for (var i = startingInd; i < obj2.length; i++) {
            if (!obj1fields.has(obj2[i][0])) {
                return false;
            }
        }

        return true;
    }
}


ExecutionVisualizer.prototype.isPrimitiveType = function(obj) {
    var hook_result = this.try_hook("isPrimitiveType", {obj:obj});
    if (hook_result[0]) return hook_result[1];

    // null is a primitive
    if (obj === null) {
        return true;
    }

    if (typeof obj == "object") {
        // kludge: only 'SPECIAL_FLOAT' objects count as primitives
        return (obj[0] == 'SPECIAL_FLOAT' || obj[0] == 'JS_SPECIAL_VAL' ||
                obj[0] == 'C_DATA' /* TODO: is this right?!? */);
    }
    else {
        // non-objects are primitives
        return true;
    }
}

function isHeapRef(obj, heap) {
    // ordinary REF
    if (obj[0] === 'REF') {
        return (heap[obj[1]] !== undefined);
    } else if (obj[0] === 'C_DATA' && obj[2] === 'pointer') {
        // C-style pointer that has a valid value
        if (obj[3] != '<UNINITIALIZED>' && obj[3] != '<UNALLOCATED>') {
            return (heap[obj[3]] !== undefined);
        }
    }

    return false;
}

function getRefID(obj) {
    if (obj[0] == 'REF') {
        return obj[1];
    } else if (obj[0] == 'VOID') {
        return 'VOID';
    } else {
        assert (obj[0] === 'C_DATA' && obj[2] === 'pointer');
        assert (obj[3] != '<UNINITIALIZED>' && obj[3] != '<UNALLOCATED>');
        return obj[3]; // pointed-to address
    }
}

// All of the Java frontend code in this function was written by David
// Pritchard and Will Gwozdz, and integrated by Philip Guo
ExecutionVisualizer.prototype.activateJavaFrontend = function() {
    // super hack by Philip that reverses the direction of the stack so
    // that it grows DOWN and renders the same way as the Python and JS
    // visualizer stacks
    this.curTrace.forEach(function(e, i) {
        if (e.stack_to_render !== undefined) {
            e.stack_to_render.reverse();
        }
    });

    this.add_pytutor_hook(
            "renderPrimitiveObject",
            function(args) {
                var obj = args.obj, d3DomElement = args.d3DomElement;
                var typ = typeof obj;
                if (obj == null)
                    d3DomElement.append('<span class="nullObj">null</span>');
                else if (typ == "number")
                    d3DomElement.append('<span class="numberObj">' + obj + '</span>');
                else if (typ == "boolean") {
                    if (obj)
                        d3DomElement.append('<span class="boolObj">true</span>');
                    else
                        d3DomElement.append('<span class="boolObj">false</span>');
                }
                else if (obj instanceof Array && obj[0] == "VOID") {
                    d3DomElement.append('<span class="voidObj">void</span>');
                }
                else if (obj instanceof Array && obj[0] == "NUMBER-LITERAL") {
                    // actually transmitted as a string
                    d3DomElement.append('<span class="numberObj">' + obj[1] + '</span>');
                }
                else if (obj instanceof Array && obj[0] == "CHAR-LITERAL") {
                    var asc = obj[1].charCodeAt(0);
                    var ch = obj[1];

                    // default
                    var show = asc.toString(16);
                    while (show.length < 4) show = "0" + show;
                    show = "\\u" + show;

                    if (ch == "\n") show = "\\n";
                    else if (ch == "\r") show = "\\r";
                    else if (ch == "\t") show = "\\t";
                    else if (ch == "\b") show = "\\b";
                    else if (ch == "\f") show = "\\f";
                    else if (ch == "\'") show = "\\\'";
                    else if (ch == "\"") show = "\\\"";
                    else if (ch == "\\") show = "\\\\";
                    else if (asc >= 32) show = ch;

                    // stringObj to make monospace
                    d3DomElement.append('<span class="stringObj">\'' + show + '\'</span>');
                }
                else
                    return [false]; // we didn't handle it
                return [true]; // we handled it
            });

    this.add_pytutor_hook(
            "isPrimitiveType",
            function(args) {
                var obj = args.obj;
                if ((obj instanceof Array && obj[0] == "VOID")
                        || (obj instanceof Array && obj[0] == "NUMBER-LITERAL")
                        || (obj instanceof Array && obj[0] == "CHAR-LITERAL")
                        || (obj instanceof Array && obj[0] == "ELIDE"))
                    return [true, true]; // we handled it, it's primitive
                return [false]; // didn't handle it
            });

    this.add_pytutor_hook(
            "end_updateOutput",
            function(args) {
                var myViz = args.myViz;
                var curEntry = myViz.curTrace[myViz.curInstr];
                if (myViz.params.stdin && myViz.params.stdin != "") {
                    var stdinPosition = curEntry.stdinPosition || 0;
                    var stdinContent =
                        '<span style="color:lightgray;text-decoration: line-through">'+
                        escapeHtml(myViz.params.stdin.substr(0, stdinPosition))+
                        '</span>'+
                        escapeHtml(myViz.params.stdin.substr(stdinPosition));
                    myViz.domRoot.find('#stdinShow').html(stdinContent);
                }
                return [false];
            });

    this.add_pytutor_hook(
            "end_constructor",
            function(args) {
                var myViz = args.myViz;
                if ((myViz.curTrace.length > 0)
                        && myViz.curTrace[myViz.curTrace.length-1]
                        && myViz.curTrace[myViz.curTrace.length-1].stdout) {
                    myViz.hasStdout = true;
                    myViz.stdoutLines = myViz.curTrace[myViz.curTrace.length-1].stdout.split("\n").length;
                }
                // if last frame is a step limit
                else if ((myViz.curTrace.length > 1)
                        && myViz.curTrace[myViz.curTrace.length-2]
                        && myViz.curTrace[myViz.curTrace.length-2].stdout) {
                    myViz.hasStdout = true;
                    myViz.stdoutLines = myViz.curTrace[myViz.curTrace.length-2].stdout.split("\n").length;
                }
                else {
                    myViz.stdoutLines = -1;
                }
                if (myViz.hasStdout)
                    for (var i=0; i<myViz.curTrace.length; i++)
                        if (!(myViz.curTrace[i].stdout))
                            myViz.curTrace[i].stdout=" "; // always show it, if it's ever used
            });

    this.add_pytutor_hook(
            "end_render",
            function(args) {
                var myViz = args.myViz;

                if (myViz.params.stdin && myViz.params.stdin != "") {
                    var stdinHTML = '<div id="stdinWrap">stdin:<pre id="stdinShow" style="border:1px solid gray"></pre></div>';
                    myViz.domRoot.find('#dataViz').append(stdinHTML);
                }

                myViz.domRoot.find('#'+myViz.generateID('globals_header')).html("Static fields");
            });

    this.add_pytutor_hook(
            "isLinearObject",
            function(args) {
                var heapObj = args.heapObj;
                if (heapObj[0]=='STACK' || heapObj[0]=='QUEUE')
                    return ['true', 'true'];
                return ['false'];
            });

    this.add_pytutor_hook(
            "renderCompoundObject",
            function(args) {
                var objID = args.objID;
                var d3DomElement = args.d3DomElement;
                var obj = args.obj;
                var typeLabelPrefix = args.typeLabelPrefix;
                var myViz = args.myViz;
                var stepNum = args.stepNum;

                if (!(obj[0] == 'LIST' || obj[0] == 'QUEUE' || obj[0] == 'STACK'))
                    return [false]; // didn't handle

                var label = obj[0].toLowerCase();
                var visibleLabel = {list:'array', queue:'queue', stack:'stack'}[label];

                if (obj.length == 1) {
                    d3DomElement.append('<div class="typeLabel">' + typeLabelPrefix + 'empty ' + visibleLabel + '</div>');
                    return [true]; //handled
                }

                d3DomElement.append('<div class="typeLabel">' + typeLabelPrefix + visibleLabel + '</div>');
                d3DomElement.append('<table class="' + label + 'Tbl"></table>');
                var tbl = d3DomElement.children('table');

                if (obj[0] == 'LIST') {
                    tbl.append('<tr></tr><tr></tr>');
                    var headerTr = tbl.find('tr:first');
                    var contentTr = tbl.find('tr:last');

                    // i: actual index in json object; ind: apparent index
                    for (var i=1, ind=0; i<obj.length; i++) {
                        var val = obj[i];
                        var elide = val instanceof Array && val[0] == 'ELIDE';

                        // add a new column and then pass in that newly-added column
                        // as d3DomElement to the recursive call to child:
                        headerTr.append('<td class="' + label + 'Header"></td>');
                        headerTr.find('td:last').append(elide ? "&hellip;" : ind);

                        contentTr.append('<td class="'+ label + 'Elt"></td>');
                        if (!elide) {
                            myViz.renderNestedObject(val, stepNum, contentTr.find('td:last'));
                            ind++;
                        }
                        else {
                            contentTr.find('td:last').append("&hellip;");
                            ind += val[1]; // val[1] is the number of cells to skip
                        }
                    }
                } // end of LIST handling

                // Stack and Queue handling code by Will Gwozdz
                /* The table produced for stacks and queues is formed slightly differently than the others,
                   missing the header row. Two rows made the dashed border not line up properly */
                if (obj[0] == 'STACK') {
                    tbl.append('<tr></tr><tr></tr>');
                    var contentTr = tbl.find('tr:last');
                    contentTr.append('<td class="'+ label + 'FElt">'+'<span class="stringObj symbolic">&#8596;</span>'+'</td>');
                    $.each(obj, function(ind, val) {
                        if (ind < 1) return; // skip type tag and ID entry
                        contentTr.append('<td class="'+ label + 'Elt"></td>');
                        myViz.renderNestedObject(val, stepNum, contentTr.find('td:last'));
                    });
                    contentTr.append('<td class="'+ label + 'LElt">'+'</td>');
                }

                if (obj[0] == 'QUEUE') {
                    tbl.append('<tr></tr><tr></tr>');
                    var contentTr = tbl.find('tr:last');
                    // Add arrows showing in/out direction
                    contentTr.append('<td class="'+ label + 'FElt">'+'<span class="stringObj symbolic">&#8592;</span></td>');
                    $.each(obj, function(ind, val) {
                        if (ind < 1) return; // skip type tag and ID entry
                        contentTr.append('<td class="'+ label + 'Elt"></td>');
                        myViz.renderNestedObject(val, stepNum, contentTr.find('td:last'));
                    });
                    contentTr.append('<td class="'+ label + 'LElt">'+'<span class="stringObj symbolic">&#8592;</span></td>');
                }

                return [true]; // did handle
            });

    this.add_pytutor_hook(
            "end_renderDataStructures",
            function(args) {
                var myViz = args.myViz;
                myViz.domRoot.find("td.instKey:contains('___NO_LABEL!___')").hide();
                myViz.domRoot.find(".typeLabel:contains('dict')").each(
                        function(i) {
                            if ($(this).html()=='dict')
                                $(this).html('symbol table');
                            if ($(this).html()=='empty dict')
                                $(this).html('empty symbol table');
                        });
            });

    // java synthetics cause things which javascript doesn't like in an id
    var old_generateID = ExecutionVisualizer.prototype.generateID;
    this.generateID = function(original_id) {
        var sanitized = original_id.replace(
                /[^0-9a-zA-Z_]/g,
                function(match) {return '-'+match.charCodeAt(0)+'-';}
                );
        return old_generateID(sanitized);
    }

    // utility functions
    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
            '"': '&quot;',
            "'": '&#39;',
                "/": '&#x2F;'
    };

    var escapeHtml = function(string) {
        return String(string).replace(/[&<>"'\/]/g, function (s) {
                return entityMap[s];
                });
    };
}

