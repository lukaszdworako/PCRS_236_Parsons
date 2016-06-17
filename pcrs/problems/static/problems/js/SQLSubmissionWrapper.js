function SQLSubmissionWrapper(name) {
    SubmissionWrapper.call(this, name);
    this.language = "sql";
    this.language_version = "text/x-sql";
}
SQLSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
SQLSubmissionWrapper.prototype.constructor = SQLSubmissionWrapper;

/**
 * @override
 */
SQLSubmissionWrapper.prototype._shouldUseGradeTable = function() {
    return true;
}

/**
 * @override
 */
SQLSubmissionWrapper.prototype.prepareGradingTable = function(testData) {
    var div_id = this.wrapperDivId;
    var best = testData['best_score'];
    var max_score = testData['max_score'];
    var sub_pk = testData['sub_pk'];
    var past_dead_line = testData['past_dead_line'];
    var error_msg = testData['error_msg'];
    var testcases = testData['testcases'];

    var score = 0;
    var tests = [];
    var table_location = $('#'+div_id).find('#table_location');
    table_location.empty();

    // Error ra
    if (error_msg) {
        table_location.append("<div class='red-alert'>"+error_msg+"</div>");

        var test = {'visible': false,
                    'input': null,
                    'output': null,
                    'passed': false,
                    'description': error_msg};
        tests.push(test);
    } else {
        for (var i = 0; i < testcases.length; i++) {
            var current_testcase = testcases[i];
            var main_table = $('<table/>', {id:"gradeMatrix"+current_testcase['testcase'],
                                            class:"pcrs-table"});

            var expected_td = $('<td/>', {
                'class': "table-left"
            }).append("Expected");
            var actual_td = $('<td/>', {class:"table-right"});

            if ( ! this.isEditor) {
                actual_td.append("Actual");
            }

            var left_wrapper = $('<div/>', {class:"sql_table_control"});
            var right_wrapper;
            if (current_testcase['visible'])
                right_wrapper = $('<div/>',{class:"sql_table_control"});
            else {
                right_wrapper = $('<div/>',{class:"sql_table_control_full"});
            }

            var expected_table = $('<table/>', {class:"pcrs-table"});
            var actual_table = $('<table/>', {class:"pcrs-table"});

            var expected_entry = $('<tr/>', {class:"pcrs-table-head-row"});
            var actual_entry = $('<tr/>', {class:"pcrs-table-head-row"});

            if ( ! this.isEditor) {
                if (current_testcase['passed']) {
                    table_location.append("<div class='green-alert'><icon class='ok-icon'>" +
                                          "</icon><span> Test Case Passed</span></div>");
                    score++;
                } else {
                    table_location.append("<div class='red-alert'><icon class='remove-icon'>" +
                                          "</icon><span> Test Case Failed</span></div>");
                }
            }

            if (current_testcase['error'] != null) {
                table_location.append("<div class='red-alert'>"+current_testcase['error']+"</div>");
            } else {
                if (current_testcase['visible'] && !this.isEditor){
                    for (var header = 0; header < current_testcase['expected_attrs'].length; header++){
                        expected_entry.append("<td><b>"+ current_testcase['expected_attrs'][header] +"</b></td>");
                    }
                }
                else if (!this.isEditor) {
                    table_location.append("<div class='blue-alert'>" +
                                      "</icon><span> Expected Result is Hidden </span></div>");
                }

                for (var header = 0; header < current_testcase['actual_attrs'].length; header++){
                    actual_entry.append("<td><b>"+ current_testcase['actual_attrs'][header] +"</b></td>");
                }

                expected_table.append(expected_entry);
                actual_table.append(actual_entry);
                expected_table.removeClass("pcrs-table-head-row").addClass("pcrs-table-row");
                actual_table.removeClass("pcrs-table-head-row").addClass("pcrs-table-row");

                if (current_testcase['visible'] && !this.isEditor){
                    for (var entry = 0; entry < current_testcase['expected'].length; entry++){
                        var entry_class = 'pcrs-table-row';
                        var test_entry = current_testcase['expected'][entry];
                        if (test_entry['missing']){
                            entry_class = "pcrs-table-row-missing";
                        }
                        var expected_entry = $('<tr/>', {class:entry_class});
                        for (var header = 0; header < current_testcase['expected_attrs'].length; header++){
                            expected_entry.append("<td>" +
                                                 test_entry[current_testcase['expected_attrs'][header]] +
                                                 "</td>");
                        }
                        expected_table.append(expected_entry);
                    }
                }

                for (var entry = 0; entry < current_testcase['actual'].length; entry++){
                    var entry_class = 'pcrs-table-row';
                    var test_entry = current_testcase['actual'][entry];
                    if (test_entry['extra']){
                        entry_class = 'pcrs-table-row-extra';
                    }
                    else if (test_entry['out_of_order']){
                        entry_class = 'pcrs-table-row-order';
                    }
                    var actual_entry = $('<tr/>', {class:entry_class});
                    for (var header = 0; header < current_testcase['actual_attrs'].length; header++){

                       actual_entry.append("<td>" +
                                           test_entry[current_testcase['actual_attrs'][header]] +
                                           "</td>");
                    }
                    actual_table.append(actual_entry);
                }

                if (current_testcase['visible'] && !this.isEditor){
                    left_wrapper.append(expected_table);
                    expected_td.append(left_wrapper);
                    main_table.append(expected_td);
                }

                right_wrapper.append(actual_table);
                actual_td.append(right_wrapper);
                main_table.append(actual_td);

                table_location.append(main_table);
            }

            var test = {'visible':current_testcase['visible'],
                        'input': null,
                        'output': null,
                        'passed': current_testcase['passed'],
                        'description': current_testcase['test_desc']};

            tests.push(test);
        }
    }
    var data = {'sub_time':new Date(),
            'submission':myCodeMirrors[div_id].getValue(),
            'score':score,
            'best':best,
            'past_dead_line':past_dead_line,
            'problem_pk':div_id.split("-")[1],
            'sub_pk':sub_pk,
            'out_of':max_score,
            'tests': tests};
    if (best && !data['past_dead_line']){
        update_marks(div_id, score, max_score);
    }
}

