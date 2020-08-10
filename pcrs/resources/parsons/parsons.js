(function ($, _) { // wrap in anonymous function to not show some helper variables

  // regexp used for trimming
  var trimRegexp = /^\s*(.*?)\s*$/;
  var translations = {
    en: {
      trash_label: 'Drag from here',
      solution_label: 'Construct your solution here',
      order: function() {
        return "Code fragments in your program are wrong, or in wrong order. This can be fixed by moving, removing, or replacing highlighted fragments.";},
      lines_missing: function() {
        return "Your program has too few code fragments.";},
      lines_too_many: function() {
        return "Your program has too many code fragments.";},
      no_matching: function(lineNro) {
        return "Based on language syntax, the highlighted fragment (" + lineNro + ") is not correctly indented."; },
      no_matching_open: function(lineNro, block) {
        return "The " + block + " ended on line " + lineNro + " never started."; },
      no_matching_close: function(lineNro, block) {
        return "Block " + block + " defined on line " + lineNro + " not ended properly";
      },
      block_close_mismatch: function(closeLine, closeBlock, openLine, inBlock) {
        return "Cannot end block " + closeBlock + " on line " + closeLine + " when still inside block " + inBlock + " started on line " + openLine;
      },
      block_structure: function(lineNro) { return "The highlighted fragment " + lineNro + " belongs to a wrong block (i.e. indentation)."; },
      unittest_error: function(errormsg) {
        return "<span class='msg'>Error in parsing/executing your program</span><br/> <span class='errormsg'>" + errormsg + "</span>";
      },
      unittest_output_assertion: function(expected, actual) {
       return "Expected output: <span class='expected output'>" + expected + "</span>" +
             "Output of your program: <span class='actual output'>" + actual + "</span>";
      },
      unittest_assertion: function(expected, actual) {
       return "Expected value: <span class='expected'>" + expected + "</span><br>" +
             "Actual value: <span class='actual'>" + actual + "</span>";
      },
      variabletest_assertion: function(varname, expected, actual) {
       return "Expected value of variable " + varname + ": <span class='expected'>" + expected + "</span><br>" +
             "Actual value: <span class='actual'>" + actual + "</span>";
      }
    }
  };
  var graders = {};

  // The only grader we need, as all evaluation will be in backend, sorry students ;)
  var BackEndGrader = function (parson) {
    this.parson = parson;
  };
  graders.BackEndGrader = BackEndGrader;

  // Create a line object skeleton with only code and indentation from
  // a code string of an assignment definition string (see parseCode)
  var ParsonsCodeline = function (codestring, widget) {
    this.widget = widget;
    this.code = "";
    this.indent = 0;
    this._toggles = [];
    if (codestring) {
      // Consecutive lines to be dragged as a single block of code have strings "\\n" to
      // represent newlines => replace them with actual new line characters "\n"
      this.code = codestring.replace(/#distractor\s*$/, "").replace(trimRegexp, "$1").replace(/\\n/g, "\n");
      this.indent = codestring.length - codestring.replace(/^\s+/, "").length;
    }
  };
  ParsonsCodeline.prototype.elem = function () {
    // the element will change on shuffle, so we should re-fetch it every time
    return $("#" + this.id);
  };
  // expose the type for testing, extending etc
  window.ParsonsCodeline = ParsonsCodeline;

  // Creates a parsons widget. Init must be called after creating an object.
  var ParsonsWidget = function (options) {
    // Contains line objects of the user-draggable code.
    // The order is not meaningful (unchanged from the initial state) but
    // indent property for each line object is updated as the user moves
    // codelines around. (see parseCode for line object description)
    this.modified_lines = [];
    // contains line objects of distractors (see parseCode for line object description)
    this.extra_lines = [];
    // contains line objects (see parseCode for line object description)
    this.model_solution = [];

    //To collect statistics, feedback should not be based on this
    this.user_actions = [];

    //State history for feedback purposes
    this.state_path = [];
    this.states = {};

    var defaults = {
      'incorrectSound': false,
      'x_indent': 50,
      'can_indent': true,
      'feedback_cb': false,
      'first_error_only': true,
      'max_wrong_lines': 10,
      'lang': 'en',
      'toggleSeparator': '::'
    };

    this.options = jQuery.extend({}, defaults, options);
    this.feedback_exists = false;
    this.id_prefix = options['sortableId'] + 'codeline';
    if (translations.hasOwnProperty(this.options.lang)) {
      this.translations = translations[this.options.lang];
    } else {
      this.translations = translations['en'];
    }

    // translate trash_label and solution_label
    if (!this.options.hasOwnProperty("trash_label")) {
      this.options.trash_label = this.translations.trash_label;
    }
    if (!this.options.hasOwnProperty("solution_label")) {
      this.options.solution_label = this.translations.solution_label;
    }
    this.FEEDBACK_STYLES = {
      'correctPosition': 'correctPosition',
      'incorrectPosition': 'incorrectPosition',
      'correctIndent': 'correctIndent',
      'incorrectIndent': 'incorrectIndent'
    };

    // force to backend grader
    this.grader = new BackEndGrader(this);
  };
  ParsonsWidget._graders = graders;

  ////Public methods

  // Parses an assignment definition given as a string and returns and 
  // transforms this into an object defining the assignment with line objects.
  //
  // lines: A string that defines the solution to the assignment and also 
  //   any possible distractors
  // max_distractrors: The number of distractors allowed to be included with
  //   the lines required in the solution
  ParsonsWidget.prototype.parseCode = function (lines, max_distractors) {
    var distractors = [],
      indented = [],
      widgetData = [],
      lineObject,
      errors = [],
      that = this;
    // Create line objects out of each codeline and separate
    // lines belonging to the solution and distractor lines
    // Fields in line objects:
    //   code: a string of the code, may include newline characters and 
    //     thus in fact represents a block of consecutive lines
    //   indent: indentation level, -1 for distractors
    //   distractor: boolean whether this is a distractor
    //   orig: the original index of the line in the assignment definition string,
    //     for distractors this is not meaningful but for lines belonging to the 
    //     solution, this is their expected position
    $.each(lines, function (index, item) {
      lineObject = new ParsonsCodeline(item, that);
      lineObject.orig = index;
      if (item.search(/\[(\/)?(static|inter|group)\]$/) >= 0) {
        // this line contains a tag, ignore it for now
        // TODO: implement these specific cases to allow for custom creation
        return true;
      }
      if (item.search(/#distractor\s*$/) >= 0) {
        // This line is a distractor
        lineObject.indent = -1;
        lineObject.distractor = true;
        if (lineObject.code.length > 0) {
          // The line is non-empty, not just whitespace
          distractors.push(lineObject);
        }
      } else {
        // This line is part of the solution
        // Initialize line object with code and indentation properties
        if (lineObject.code.length > 0) {
          // The line is non-empty, not just whitespace
          lineObject.distractor = false;
          indented.push(lineObject);
        }
      }
    });

    var normalized = this.normalizeIndents(indented);

    $.each(normalized, function (index, item) {
      if (item.indent < 0) {
        // Indentation error
        errors.push(this.translations.no_matching(normalized.orig));
      }
      widgetData.push(item);
    });

    // Remove extra distractors if there are more alternative distrators 
    // than should be shown at a time
    var permutation = this.getRandomPermutation(distractors.length);
    var selected_distractors = [];
    for (var i = 0; i < max_distractors; i++) {
      selected_distractors.push(distractors[permutation[i]]);
      widgetData.push(distractors[permutation[i]]);
    }

    return {
      // an array of line objects specifying  the solution
      solution: $.extend(true, [], normalized),
      // an array of line objects specifying the requested number 
      // of distractors (not all possible alternatives)
      distractors: $.extend(true, [], selected_distractors),
      // an array of line objects specifying the initial code arrangement 
      // given to the user to use in constructing the solution 
      widgetInitial: $.extend(true, [], widgetData),
      errors: errors
    };
  };

  ParsonsWidget.prototype.init = function (text) {
    // TODO: Error handling, parseCode may return errors in an array in property named errors.
    var initial_structures = this.parseCode(text.split("\n"), this.options.max_wrong_lines);
    this.model_solution = initial_structures.solution;
    this.extra_lines = initial_structures.distractors;
    this.modified_lines = initial_structures.widgetInitial;
    var id_prefix = this.id_prefix;

    // Add ids to the line objects in the user-draggable lines
    $.each(this.modified_lines, function (index, item) {
      item.id = id_prefix + index;
      item.indent = 0;
    });
  };

  ParsonsWidget.prototype.getHash = function (searchString) {
    var hash = [],
      ids = $(searchString).sortable('toArray'),
      line;
    for (var i = 0; i < ids.length; i++) {
      line = this.getLineById(ids[i]);
      hash.push(line.orig + "_" + line.indent);
    }
    //prefix with something to handle empty output situations
    if (hash.length === 0) {
      return "-";
    } else {
      return hash.join("-");
    }
  };

  ParsonsWidget.prototype.solutionHash = function () {
    return this.getHash("#ul-" + this.options.sortableId);
  };

  ParsonsWidget.prototype.trashHash = function () {
    return this.getHash("#ul-" + this.options.trashId);
  };

  ParsonsWidget.prototype.whatWeDidPreviously = function () {
    var hash = this.solutionHash();
    var previously = this.states[hash];
    if (!previously) { return undefined; }
    var visits = _.filter(this.state_path, function (state) {
      return state == hash;
    }).length - 1;
    var i, stepsToLast = 0, s,
      outputStepTypes = ['removeOutput', 'addOutput', 'moveOutput'];
    for (i = this.state_path.length - 2; i > 0; i--) {
      s = this.states[this.state_path[i]];
      if (s && outputStepTypes.indexOf(s.type) != -1) {
        stepsToLast++;
      }
      if (hash === this.state_path[i]) { break; }
    }
    return $.extend(false, { 'visits': visits, stepsToLast: stepsToLast }, previously);
  };

  /**
    * Returns states of the toggles for logging purposes
    */
  ParsonsWidget.prototype._getToggleStates = function () {
    var context = $("#" + this.options.sortableId + ", #" + this.options.trashId),
      toggles = $(".jsparson-toggle", context),
      toggleStates = {};
    $("#" + this.options.sortableId + " .jsparson-toggle").each(function () {
      if (!toggleStates.output) {
        toggleStates.output = [];
      }
      toggleStates.output.push($(this).text());
    });
    if (this.options.trashId) {
      toggleStates.input = [];
      $("#" + this.options.trashId + " .jsparson-toggle").each(function () {
        toggleStates.input.push($(this).text());
      });
    }
    if ((toggleStates.output && toggleStates.output.length > 0) ||
      (toggleStates.input && toggleStates.input.length > 0)) {
      return toggleStates;
    } else {
      return undefined;
    }
  };

  ParsonsWidget.prototype.addLogEntry = function (entry) {
    var state, previousState;
    var logData = {
      time: new Date(),
      output: this.solutionHash(),
      type: "action"
    };

    if (this.options.trashId) {
      logData.input = this.trashHash();
    }

    if (entry.target) {
      entry.target = entry.target.replace(this.id_prefix, "");
    }

    // add toggle states to log data if there are toggles
    var toggles = this._getToggleStates();
    if (toggles) {
      logData.toggleStates = toggles;
    }

    state = logData.output;

    jQuery.extend(logData, entry);
    this.user_actions.push(logData);

    //Updating the state history
    if (this.state_path.length > 0) {
      previousState = this.state_path[this.state_path.length - 1];
      this.states[previousState] = logData;
    }

    //Add new item to the state path only if new and previous states are not equal
    if (this.state_path[this.state_path.length - 1] !== state) {
      this.state_path.push(state);
    }
    // callback for reacting to actions
    if ($.isFunction(this.options.action_cb)) {
      this.options.action_cb.call(this, logData);
    }
  };

  /**
   * Update indentation of a line based on new coordinates
   * leftDiff horizontal difference from (before and after drag) in px
   ***/
  ParsonsWidget.prototype.updateIndent = function (leftDiff, id) {

    var code_line = this.getLineById(id);
    var new_indent = this.options.can_indent ? code_line.indent + Math.floor(leftDiff / this.options.x_indent) : 0;
    new_indent = Math.max(0, new_indent);
    code_line.indent = new_indent;

    return new_indent;
  };

  // Get a line object by the full id including id prefix
  // (see parseCode for description of line objects)
  ParsonsWidget.prototype.getLineById = function (id) {
    var index = -1;
    for (var i = 0; i < this.modified_lines.length; i++) {
      if (this.modified_lines[i].id == id) {
        index = i;
        break;
      }
    }
    return this.modified_lines[index];
  };

  // Check and normalize code indentation.
  // Does not use the current object (this) ro make changes to 
  // the parameter.
  // Returns a new array of line objects whose indent fields' values 
  // may be different from the argument. If indentation does not match,
  // i.e. code is malformed, value of indent may be -1.
  // For example, the first line may not be indented.
  ParsonsWidget.prototype.normalizeIndents = function (lines) {

    var normalized = [];
    var new_line;
    var match_indent = function (index) {
      //return line index from the previous lines with matching indentation
      for (var i = index - 1; i >= 0; i--) {
        if (lines[i].indent == lines[index].indent) {
          return normalized[i].indent;
        }
      }
      return -1;
    };
    for (var i = 0; i < lines.length; i++) {
      //create shallow copy from the line object
      new_line = jQuery.extend({}, lines[i]);
      if (i === 0) {
        new_line.indent = 0;
        if (lines[i].indent !== 0) {
          new_line.indent = -1;
        }
      } else if (lines[i].indent == lines[i - 1].indent) {
        new_line.indent = normalized[i - 1].indent;
      } else if (lines[i].indent > lines[i - 1].indent) {
        new_line.indent = normalized[i - 1].indent + 1;
      } else {
        // indentation can be -1 if no matching indentation exists, i.e. IndentationError in Python
        new_line.indent = match_indent(i);
      }
      normalized[i] = new_line;
    }
    return normalized;
  };

  /**
   * Retrieve the code lines based on what is in the DOM
   *
   * TODO(petri) refactor to UI
   * */
  ParsonsWidget.prototype.getModifiedCode = function (search_string) {
    //ids of the the modified code
    var lines_to_return = [],
      solution_ids = $(search_string).sortable('toArray'),
      i, item;
    for (i = 0; i < solution_ids.length; i++) {
      item = this.getLineById(solution_ids[i]);
      lines_to_return.push($.extend(new ParsonsCodeline(), item));
    }
    return lines_to_return;
  };

  ParsonsWidget.prototype.hashToIDList = function (hash) {
    var lines = [];
    var lineValues;
    var lineObject;
    var h;

    if (hash === "-" || hash === "" || hash === null) {
      h = [];
    } else {
      h = hash.split("-");
    }

    var ids = [];
    for (var i = 0; i < h.length; i++) {
      lineValues = h[i].split("_");
      ids.push(this.modified_lines[lineValues[0]].id);
    }
    return ids;
  };

  ParsonsWidget.prototype.updateIndentsFromHash = function (hash) {
    var lineValues;
    var h;

    if (hash === "-" || hash === "" || hash === null) {
      h = [];
    } else {
      h = hash.split("-");
    }

    var ids = [];
    for (var i = 0; i < h.length; i++) {
      lineValues = h[i].split("_");
      this.modified_lines[lineValues[0]].indent = Number(lineValues[1]);
      this.updateHTMLIndent(this.modified_lines[lineValues[0]].id);
    }
    return ids;
  };
  
  /**
   * @return
   * TODO(petri): Separate UI from here
   */
  ParsonsWidget.prototype.getFeedback = function () {
    this.submit();
  };
  ParsonsWidget.prototype.submit = function () {
    var parson = this.grader.parson;
    var elemId = parson.options.sortableId;
    var student_code = parson.normalizeIndents(parson.getModifiedCode("#ul-" + elemId));
    student_code = parson.minimizeSubmission(student_code);
    var postParams = { "csrfmiddlewaretoken": getCookie("csrftoken"), "submission": JSON.stringify(student_code) };
    var problem_pk = window.location.pathname.match(/\d{1,}/g);
    var that = this;
    $('#waitingModal').modal('show');

    $.post(root + '/problems/parsons/' + problem_pk + '/run',
      postParams,
      function (data) {
        $('#waitingModal').modal('hide');
        if (data['past_dead_line']) {
          alert('This submission is past the deadline!');
          $('#' + div_id).find('#deadline_msg').remove();
          $('#' + div_id)
            .find('#alert')
            .after('<div id="deadline_msg" class="red-alert">Submitted after the deadline!<div>');
        }

        var display_element = $('#parsons-' + problem_pk).find('#alert');
        var score = data['score'];
        var max_score = data['max_score'];
        var is_correct = score >= max_score;
        var res;
        if (data['results']){
          res = data['results'];
        } else {
          alert("This should never be hit... like there's literally nothing, you thanos snapped the universe");
          return;
        }
        
        if (is_correct) {
          // if answer is correct, mark it in the UI
          $(display_element)
            .toggleClass('green-alert', is_correct);
          $(display_element)
            .children('icon')
            .toggleClass('ok-icon', is_correct);
          $(display_element)
            .children('span')
            .text('Your solution is complete.');
        } else {
          // if answer is incorrect, mark it in the UI
          $(display_element)
            .toggleClass('red-alert', !is_correct);
          $(display_element)
            .children('icon')
            .toggleClass('remove-icon', !is_correct);
            var alert_msg = 'Your solution is either incorrect or incomplete!';

            if (res['result_lines']) {
              switch (res['result_lines']) {
                // in case we want specific message for the error that occured, currently does nothing other then syntax message since that's a bother
                case 1:
                case 2:
                case 3:
                  alert_msg = "Double check if the invariant holds on all iterations!";
                  break;
                case 4:
                  alert_msg = "Check your syntax!";
                  break;
                default:
                  alert_msg = "Unknown error occured, please try again!";
                  break;
              }
            }
            $(display_element).children('span').text(alert_msg);

        }
        if (res['result_test']) {
          if (res['result_test'].length == 0) {
            alert_msg += "\nIt seems as though your instructor chose to run testcases, but did not provide any!"
            $(display_element).children('span').text(alert_msg);
          } else {
            that.prepareGradingTable(res);
          }
        }
      }).fail(function (jqXHR, textStatus, errorThrown) { $('#waitingModal').modal('hide'); console.log(jqXHR, textStatus, errorThrown); });
  };

  ParsonsWidget.prototype.prepareGradingTable = function (data) {
    var error_msg = data['error_test'];
    var testcases = data['result_test'];

    $("#grade-code").show();
    var $gradingTable = $("#gradeMatrix");
    $gradingTable.find(".red-alert").remove();
    $gradingTable.find('.pcrs-table-row').remove();

    // if we hit an error message, display it and we're done
    if (error_msg) {
      $gradingTable.append($('<th class="red-alert"></th>')
        .attr('style', 'width:100%;')
        .attr('colspan', '12')
        .html(error_msg));
      return;
    }
    this._addTestCasesToTable(testcases, $gradingTable);

  };

  ParsonsWidget.prototype._addTestCasesToTable = function (testcases, $gradingTable) {
    for (var i = 0; i < testcases.length; i++) {
      var testcase = this._formatTestCaseObject(testcases[i]);
      var $newRow = this._createTestCaseRow(testcase);
      $gradingTable.append($newRow);
    }
  };

  ParsonsWidget.prototype._formatTestCaseObject = function (testcase) {
    if (testcase.test_desc == '') {
      testcase.test_desc = "No Description Provided"
    }
    return testcase;
  };

  ParsonsWidget.prototype._createTestCaseRow = function (testcase) {
    var $newRow = $('<tr class="pcrs-table-row"></tr>');

    if ("exception" in testcase) {
      $newRow.append($('<th class="red-alert" colspan="12"></th>')
        .attr('style', 'width: 100%;')
        .append("<code>" + testcase.exception + "</code>"));
    }

    $newRow.append('<td class="description">' + testcase.test_desc + '</td>');
    if (testcase.test_input != null) {
      $newRow.append('<td class="expression"><div class="expression_div">' +
        testcase.test_input + '</div></td>');
    } else {
      $newRow.append('<td class="expression">' +
        "Hidden Test" + '</td>');
    }

    var expTestValDiv = $('<div class="ExecutionVisualizer"></div>');
    var testResultDiv = $('<div class="ExecutionVisualizer"></div>');

    $newRow.append($('<td class="expected"></td>')
      .append($('<div class="ptd"></div>')
        .append(expTestValDiv)));
    $newRow.append($('<td class="result"></td>')
      .append($('<div class="ptd"></div>')
        .append(testResultDiv)));

    renderData_ignoreID(testcase.test_val, testResultDiv);
    renderData_ignoreID(testcase.expected_output, expTestValDiv);

    this._addFaceColumnToTestRow($newRow, testcase.passed_test);
    //this._addDebugColumnToTestRow($newRow, testcase.debug);
    this._addA11yToTestRow($newRow,
      this._accessibilityOutput(testcase.test_val),
      testcase.passed_test,
      this._accessibilityOutput(testcase.expected_output));

    return $newRow;

  }

  ParsonsWidget.prototype._accessibilityOutput = function(input) {
    var brakets_o = {"list":"[","tuple":"(","dict":"{"};
    var brakets_c = {"list":"]","tuple":")","dict":"}"};

    if (input.length == 2) {
        return this._accessibilityOutput(
            input[0]) + ":" + this._accessibilityOutput(input[1]);
    } else if (input[0] == "list" || input[0] == "tuple" || input[0] == "dict") {
        var output = brakets_o[input[0]];
        for (var o_index = 2; o_index < input.length; o_index++) {
            output += this._accessibilityOutput(input[o_index]);
            if (o_index != input.length - 1) {
                output += ", ";
            }
        }
        output += brakets_c[input[0]];
        return output
    } else if (input[0] == "string") {
        return "'" + input[2] + "'";
    } else if(input[0] == "float") {
        if (String(input[2]).indexOf(".") > -1) {
            return input[2];
        } else {
            return input[2] + ".0"
        }
    } else {
        return input[2]
    }
}

ParsonsWidget.prototype._addA11yToTestRow = function($row, result, passed,
    expected) {
    var pass_status = passed ? 'passed' : 'failed'
    $row.append('<a class="at" href="">This testcase has ' + pass_status +
        '. Expected: ' + expected +
        '. Result: ' + result + '</a>');
    }

  ParsonsWidget.prototype._addFaceColumnToTestRow = function($row, passed) {
    var $face = $('<img>').attr({
        src: passed ? happyFaceURL : sadFaceURL, // Globals :|
        alt: passed ? 'Smiley Face' : 'Sad Face',
        height: '36',
        width: '36',
    });
    $row.append($('<td class="passed"></td>').append($face));
}

  ParsonsWidget.prototype.minimizeSubmission = function (student_code) {
    var minimized = [];
    $.each(student_code, function (index, value) {
      minimized.push({ "code": value.code, "indent": value.indent });
    });
    return minimized;
  };

  ParsonsWidget.prototype.clearFeedback = function () {
    if (this.feedback_exists) {
      $("#ul-" + this.options.sortableId).removeClass("incorrect correct");
      var li_elements = $("#ul-" + this.options.sortableId + " li");
      $.each(this.FEEDBACK_STYLES, function (index, value) {
        li_elements.removeClass(value);
      });
    }
    this.feedback_exists = false;
  };


  ParsonsWidget.prototype.getRandomPermutation = function (n) {
    var permutation = [];
    var i;
    for (i = 0; i < n; i++) {
      permutation.push(i);
    }
    var swap1, swap2, tmp;
    for (i = 0; i < n; i++) {
      swap1 = Math.floor(Math.random() * n);
      swap2 = Math.floor(Math.random() * n);
      tmp = permutation[swap1];
      permutation[swap1] = permutation[swap2];
      permutation[swap2] = tmp;
    }
    return permutation;
  };


  ParsonsWidget.prototype.shuffleLines = function () {
    var permutation = (this.options.permutation ? this.options.permutation : this.getRandomPermutation)(this.modified_lines.length);
    var idlist = [];
    for (var i in permutation) {
      idlist.push(this.modified_lines[permutation[i]].id);
    }
    if (this.options.trashId) {
      this.createHTMLFromLists([], idlist);
    } else {
      this.createHTMLFromLists(idlist, []);
    }
  };

  ParsonsWidget.prototype.updateHTMLIndent = function (codelineID) {
    var line = this.getLineById(codelineID);
    $('#' + codelineID).css("margin-left", this.options.x_indent * line.indent + "px");
  };


  ParsonsWidget.prototype.codeLineToHTML = function (codeline) {
    return '<li id="' + codeline.id + '" class="prettyprint lang-py">' + codeline.code + '<\/li>';
  };

  ParsonsWidget.prototype.codeLinesToHTML = function (codelineIDs, destinationID) {
    var lineHTML = [];
    for (var id in codelineIDs) {
      var line = this.getLineById(codelineIDs[id]);
      lineHTML.push(this.codeLineToHTML(line));
    }
    return '<ul id="ul-' + destinationID + '">' + lineHTML.join('') + '</ul>';
  };

  /** modifies the DOM by inserting exercise elements into it */
  ParsonsWidget.prototype.createHTMLFromLists = function (solutionIDs, trashIDs) {
    var html;
    if (this.options.trashId) {
      html = (this.options.trash_label ? '<p>' + this.options.trash_label + '</p>' : '') +
        this.codeLinesToHTML(trashIDs, this.options.trashId);
      $("#" + this.options.trashId).html(html);
      html = (this.options.solution_label ? '<p>' + this.options.solution_label + '</p>' : '') +
        this.codeLinesToHTML(solutionIDs, this.options.sortableId);
      $("#" + this.options.sortableId).html(html);
    } else {
      html = this.codeLinesToHTML(solutionIDs, this.options.sortableId);
      $("#" + this.options.sortableId).html(html);
    }

    if (window.prettyPrint && (typeof (this.options.prettyPrint) === "undefined" || this.options.prettyPrint)) {
      prettyPrint();
    }

    var that = this;
    var sortable = $("#ul-" + this.options.sortableId).sortable(
      {
        start: function () { that.clearFeedback(); },
        stop: function (event, ui) {
          if ($(event.target)[0] != ui.item.parent()[0]) {
            return;
          }
          that.updateIndent(ui.position.left - ui.item.parent().position().left,
            ui.item[0].id);
          that.updateHTMLIndent(ui.item[0].id);
          that.addLogEntry({ type: "moveOutput", target: ui.item[0].id }, true);
        },
        receive: function (event, ui) {
          var ind = that.updateIndent(ui.position.left - ui.item.parent().position().left,
            ui.item[0].id);
          that.updateHTMLIndent(ui.item[0].id);
          that.addLogEntry({ type: "addOutput", target: ui.item[0].id }, true);
        },
        grid: that.options.can_indent ? [that.options.x_indent, 1] : false
      });
    sortable.addClass("output");
    if (this.options.trashId) {
      var trash = $("#ul-" + this.options.trashId).sortable(
        {
          connectWith: sortable,
          start: function () { that.clearFeedback(); },
          receive: function (event, ui) {
            that.getLineById(ui.item[0].id).indent = 0;
            that.updateHTMLIndent(ui.item[0].id);
            that.addLogEntry({ type: "removeOutput", target: ui.item[0].id }, true);
          },
          stop: function (event, ui) {
            if ($(event.target)[0] != ui.item.parent()[0]) {
              // line moved to output and logged there
              return;
            }
            that.addLogEntry({ type: "moveInput", target: ui.item[0].id }, true);
          }
        });
      sortable.sortable('option', 'connectWith', trash);
    }
    // Log the original codelines in the exercise in order to be able to
    // match the input/output hashes to the code later on. We need only a
    // few properties of the codeline objects
    var bindings = [];
    for (var i = 0; i < this.modified_lines.length; i++) {
      var line = this.modified_lines[i];
      bindings.push({ code: line.code, distractor: line.distractor })
    }
    this.addLogEntry({ type: 'init', time: new Date(), bindings: bindings });
  };


  window['ParsonsWidget'] = ParsonsWidget;
}
  // allows _ and $ to be modified with noconflict without changing the globals
  // that parsons uses
)($, _);
