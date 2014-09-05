/** @jsx React.DOM */


var ItemList = React.createClass({displayName: 'ItemList',
    render: function () {
        var items = this.props.items.map(function (item) {
            if (item.content_type == 'problem') {
                return Problem({key: item.id, item: item});
            }
            if (item.content_type == 'video') {
                return Video({key: item.id, item: item});
            }
        });
        return React.DOM.div(null, items);
    }
});

var Problem = React.createClass({displayName: 'Problem',

    getProblemForm: function (problem) {
        if (problem.problem_type == 'multiple_choice') {
            return (
                MultipleChoiceProblemForm({item: problem})
                );
        }
        else {
            return (
                ProgrammingProblemForm({item: problem})
                );
        }
    },

    render: function () {
        var problem = this.props.item;
        return (
            React.DOM.div({id: problem.id}, 
                React.DOM.div(null, 
                    React.DOM.h3(null, 
                        React.DOM.span({dangerouslySetInnerHTML: {__html: problem.name}}), 
                        ProblemScore({item: problem})
                    )
                ), 
                React.DOM.p({dangerouslySetInnerHTML: {__html: problem.description}}), 

                this.getProblemForm(problem), 

                React.DOM.hr(null)
            )

            );
    }
});

var ProblemScore = React.createClass({displayName: 'ProblemScore',
    mixins: [Listener, ProblemMixin],

    listenTo: [onGradingUpdate],

    getProblemScore: function (problem) {
        var pType = problem.problem_type;
        var pID = problem.pk;
        if (data.scores.hasOwnProperty(pType) &&
            data.scores[pType].hasOwnProperty(pID)) {
            return data.scores[pType][pID];
        }
        return null;
    },

    getInitialState: function () {
        return {
            score: this.getProblemScore(this.props.item)
        }
    },


    handleUpdate: function (event) {
        this.setState({score: event.detail.data.score});
    },

    render: function () {
        var maxScore = this.props.item.max_score;
        console.log('Score rendering.');

        var score;
        if (this.state.score != null && this.state.score == maxScore) {
            score = React.DOM.span({className: "green-checkmark-icon"});
        }

        else {
            score = (
                React.DOM.span(null, 
                    React.DOM.sup(null, this.state.score != null ? this.state.score : '-'), 
                "/", 
                    React.DOM.sub(null, maxScore)
                ));
        }

        return (React.DOM.span({title: "Progress so far", className: "align-right"}, 
            score
        ));
    }
});


var ProblemForm = {
    disableButton: function () {
        console.log('PROCESSING');
        var button = this.refs.submitButton.getDOMNode();
        console.log(button.textContent || button.innerText);

        button.disabled = true;
        button.textContent = "Processing...";
        button.innerText = "Processing...";
    },

    enableButton: function () {
        console.log('DONE');

        var button = this.refs.submitButton.getDOMNode();
        console.log(button.textContent || button.innerText);

        button.disabled = false;
        button.textContent = "Submit";
        button.innerText = "Submit";
    },

    submit: function (submission) {
        var component = this;
        // send to server
        console.log('send to server', submission,
            component.props.item.submit_url);

        component.disableButton();
        $.ajax({
            url: component.props.item.submit_url,
            type: 'post',
            data: {csrftoken: csrftoken, submission: submission},
            success: function (submissionResults) {
                // update problem status and testcases

                console.log(submissionResults);

                if (!submissionResults.past_dead_line) {
                    var status = {
                        score: submissionResults.score,
                        attempted: true,
                        completed: (submissionResults.score ==
                            component.props.item.max_score)
                    };
                    console.log('reporting Status');
                    component.reportStatusUpdate(status);
                    console.log('reporting Grading');
                    component.reportGradingUpdate(submissionResults);
                }
            }});
    }
};

var ProgrammingProblemForm = React.createClass({displayName: 'ProgrammingProblemForm',

    mixins: [StatusUpdateDispatcher, GradingUpdateDispatcher, ProblemForm],

    handleSubmit: function () {
        var submission = this.refs.submission.getDOMNode().value.trim();
        if (submission) {
            // Do not submit empty submission.
            this.submit(submission);
        }
    },

    render: function () {
        return (
            React.DOM.div(null, 
                React.DOM.div(null, 
                    React.DOM.textarea({defaultValue: this.props.item.starter_code, 
                    ref: "submission", className: "code-mirror"}), 
                    React.DOM.button({ref: "submitButton", className: "green-button", 
                    onClick: this.handleSubmit}, 
                    "Submit"
                    )
                ), 

                ProgrammingProblemGrading({item: this.props.item, postRender: this.enableButton})

            )
            );
    }
});

var MultipleChoiceProblemForm = React.createClass({displayName: 'MultipleChoiceProblemForm',
    mixins: [StatusUpdateDispatcher, GradingUpdateDispatcher, ProblemForm],


    getInitialState: function () {
        return {options: []};
    },

    handleSubmit: function () {
        this.submit(this.state.options);
    },


    updateSelectedOptions: function (evt) {
        var options = this.state.options;
        var optionID = evt.target.value;
        var optionSelected = evt.target.checked;

        if (optionSelected) {
            options.push(optionID);
        }
        else {
            options.splice(options.indexOf(optionID), 1);
        }

        this.setState({options: options});
    },

    render: function () {
        var component = this;
        var options = this.props.item.answer_options.map(function (option) {
            return (
                React.DOM.span(null, 
                    React.DOM.input({type: "checkbox", name: "anwer_options", 
                    value: option.pk, 
                    onChange: component.updateSelectedOptions}, 
                         option.text, 
                        React.DOM.br(null)
                    )

                )
                );
        });

        return (
            React.DOM.div(null, 
                React.DOM.div(null, options, 
                    React.DOM.button({ref: "submitButton", className: "submitBtn", 
                    onClick: this.handleSubmit}, "Submit")
                ), 

                MultipleChoiceGrading({item: this.props.item, postRender: this.enableButton}), 
                MultipleChoiceSubmissionHistory({key: "history-" + this.props.item.id, item: this.props.item})
            )

            );
    }
});


var Grading = {
    getInitialState: function () {
        return {data: null}
    },

    componentDidUpdate: function () {
        this.props.postRender();
    }
};

var MultipleChoiceGrading = React.createClass({displayName: 'MultipleChoiceGrading',
    mixins: [Listener, Grading],
    listenTo: [onGradingUpdate],

    render: function () {
        var correctness;
        if (this.state.data) {
            var score = this.state.data.score;
            var maxScore = this.props.item.max_score;
            console.log(score, maxScore);

            correctness = (
                    score == maxScore ?
                SubmissionCorrectMessage(null) :
                SubmissionIncorrectMessage({
                message: "This solution is not entirely correct."}));
        }
        return (
            React.DOM.div(null, 
                correctness
            )
            );
    }
});

var ProgrammingProblemGrading = React.createClass({displayName: 'ProgrammingProblemGrading',
    mixins: [Listener, Grading],
    listenTo: [onGradingUpdate],


    getStatusMessage: function () {
        var correctness;
        var error;

        if (this.state.data) {
            correctness = this.state.data.score == this.props.item.max_score ?
                SubmissionCorrectMessage(null) :
                SubmissionIncorrectMessage({
                message: "This solution has passed x out of y testcases."});

            var errorMessage = this.state.data.results[1] || "";
            if (errorMessage) {
                error = SubmissionErrorMessage({error: errorMessage})
            }
            return (
                React.DOM.div(null, 
                    correctness, 
                    error
                )
                );
        }
    },

    getGradingTable: function () {

        if (this.state.data) {
            var error = this.state.data.results[1];
            var testruns = this.state.data.results[0];
            if (!error && this.props.item.problem_type == 'code') {
                return CodeProblemTestcaseTable({testruns: testruns});
            }

            if (!error && (this.props.item.problem_type == 'sql' ||
                this.props.item.problem_type == 'ra')) {
                return RDBProblemTestcaseTable({testruns: testruns});
            }
        }
    },

    render: function () {
        return (
            React.DOM.div(null, 
                this.getStatusMessage(), 
                this.getGradingTable()
            )
            );
    }
});


var CodeProblemTestcaseTable = React.createClass({displayName: 'CodeProblemTestcaseTable',
    render: function () {
        var tableRows = this.props.testruns.map(function (testrun) {
            return (
                React.DOM.tr({className: "pcrs-table-row"}, 
                    React.DOM.td({className: "description"}, testrun.test_desc), 
                    React.DOM.td({className: "expression"}, testrun.test_input || "Hidden Test", 
                        React.DOM.div({className: "expression_div"})

                    ), 

                    React.DOM.td({className: "expected"}, testrun.expected_output || "Hidden Result", 
                        React.DOM.div({className: "ptd"}, 
                            React.DOM.div({className: "ExecutionVizualizer"})
                        )
                    ), 
                    React.DOM.td({className: "result"}, testrun.test_val), 
                    React.DOM.div({className: "ptd"}, 
                        React.DOM.div({className: "ExecutionVizualizer"})
                    ), 
                    React.DOM.td({className: "passed"}, 
                    
                        testrun.test_passed ?
                            React.DOM.img({id: "dynamic", src: happyFaceURL, alt: "Happy Face", 
                            height: "36", width: "36"}) :
                            React.DOM.img({id: "dynamic", src: sadFaceURL, alt: "Sad Face", 
                            height: "36", width: "36"})
                        

                    ), 
                    React.DOM.td({className: "debug"}, "Debug"), 

                    React.DOM.a({className: "at"}, "This testcase has __ (if failed, expected and result)")
                )
                );
//            TODO: fix me
        });

        var classes = React.addons.classSet({
            "hidden": !this.props.testruns,
            "pcrs-table": true
        });

        return (
            React.DOM.div(null, 
                React.DOM.table({className: classes}, 
                    React.DOM.thead(null, 
                        React.DOM.tr({className: "pcrs-table-head-row"}, 
                            React.DOM.th({className: "description"}, "Description"), 
                            React.DOM.th({className: "expression"}, "Test Expression"), 
                            React.DOM.th({className: "expected"}, "Expected"), 
                            React.DOM.th({className: "result"}, "Result"), 
                            React.DOM.th({className: "passed"}, "Passed"), 
                            React.DOM.th({className: "debug"}, "Debug")
                        )
                    ), 
                    React.DOM.tbody(null, 
                    tableRows
                    )
                )
            )
            );
    }
});


var RDBProblemTestcaseTable = React.createClass({displayName: 'RDBProblemTestcaseTable',
    render: function () {
        console.log(this.props.testruns);

        var tables = this.props.testruns.map(function (testrun) {
            if (testrun.error) {
                return ErrorMessage({error: testrun.error});

            }
            // TODO: put tables side by side
            return (
                React.DOM.div(null, 
                    Table({attributes: testrun.expected_attrs, 
                    data: testrun.expected}), 
                    Table({attributes: testrun.actual_attrs, 
                    data: testrun.actual})
                )
                );
        });

        return (
            React.DOM.div(null, 
                tables
            )
            );
    }
});


var ProblemStatusMessage = React.createClass({displayName: 'ProblemStatusMessage',
    render: function () {
        console.log('ProblemStatus');
        var error;
        if (this.props.error) {
            error = SubmissionErrorMessage({error: this.props.error});
        }
        return (
            React.DOM.div(null, 
                React.DOM.div({className: "ProblemStatusMessage"}, this.props.message), 
                error
            )
            );
    }

});

var SubmissionErrorMessage = React.createClass({displayName: 'SubmissionErrorMessage',
    render: function () {
        return React.DOM.div({className: "red-alert"}, this.props.error);
    }
});

var SubmissionCorrectMessage = React.createClass({displayName: 'SubmissionCorrectMessage',
    render: function () {
        return (React.DOM.div({className: "green-alert"}, 
        "Correct!"
        ));
    }
});

var SubmissionIncorrectMessage = React.createClass({displayName: 'SubmissionIncorrectMessage',
    render: function () {
        return (React.DOM.div({className: "red-alert"}, 
            this.props.message
        ));
    }
});

var Table = React.createClass({displayName: 'Table',
    getDataInRow: function (attributes, rowObject) {
        return attributes.map(function (attribute) {
            return rowObject[attribute];
        });
    },

    render: function () {
        var component = this;

        var tableHeader = this.props.attributes.map(function (attribute) {
            return (
                React.DOM.th(null, 
                    attribute
                )
                );
        });

        var tableRows = this.props.data.map(function (row) {
            var cells = component.getDataInRow(component.props.attributes, row)
                .map(function (cell) {
                    return (
                        React.DOM.td(null, cell)
                        );
                });

            var classes = React.addons.classSet({
                'extra': row.extra,
                'missing': row.missing,
                'out_of_order': row.out_of_order
            });
            return (
                React.DOM.tr(null, cells)
                )
                ;
        });
        return (
            React.DOM.div(null, 
                React.DOM.table(null, 
                    React.DOM.thead(null, 
                        React.DOM.tr(null, tableHeader)
                    ), 
                    React.DOM.tbody(null, 
                    tableRows
                    )
                )
            )
            );
    }
});


var Video = React.createClass({displayName: 'Video',
    mixins: [Listener, StatusUpdateDispatcher, Video],

    listenTo: [onStatusUpdate],

    updateState: function (state) {
        this.setState(state,
            this.reportStatusUpdate(state)
        );
    },

    handleClick: function () {
        console.log('Video clicked');
        var video = this.props.item;
        var component = this;
        $.ajax({
            url: video.record_watched,
            type: "post",
            data: {csrftoken: csrftoken},
            success: function () {
                console.log('Setting state');
                component.updateState({completed: true});
            }
        });
    },

    render: function () {
        console.log('Video');
        var video = this.props.item;
        var videoControls = "{\"customControlsOnMobile\": true }";
        var videoClasses = React.addons.classSet({
            'video-js': true,
            'vjs-default-skin': true
        });
        var videoWatched;
        if (this.state.completed) {
            videoWatched = React.DOM.span({className: "video-complete"}, "done")
        }

        return (
            React.DOM.div(null, 
                React.DOM.div(null, 
                this.props.item.name, " ", videoWatched
                ), 
                React.DOM.div({id: video.id, onClick: this.handleClick}, 
                    React.DOM.video({
                    className: videoClasses, 
                    controls: true, 
                    preload: "auto", 
                    'data-setup': videoControls, 
                    poster: video.thumbnail}, 
                        React.DOM.source({src: video.url, type: "rtmp/mp4"})
                    )
                )
            )
            );
    }
});

var NavigationBar = React.createClass({displayName: 'NavigationBar',
    render: function () {
        console.log('NavigationBar');

        var prevClass = React.addons.classSet({
            "icon-prev-active": data.prev_url,
            "icon-prev-inactive": !data.prev_url
        });

        var nextClass = React.addons.classSet({
            "icon-next-active": data.next_url,
            "icon-next-inactive": !data.next_url
        });


        var items = this.props.items.map(function (item) {
            return NavigationBarItem({key: item.id, item: item});
        });

        return (
            React.DOM.div({className: "pcrs-sidebar", role: "complementary"}, 
                React.DOM.ul({className: "pcrs-sidenav"}, 
                    items, 
                    React.DOM.a({className: "side-bar-arrow", href: data.prev_url}, 
                        React.DOM.span({className: prevClass})
                    ), 
                    React.DOM.a({className: "side-bar-arrow", href: data.next_url}, 
                        React.DOM.span({className: nextClass})
                    )
                )
            )
            );

    }
});

var NavigationBarItem = React.createClass({displayName: 'NavigationBarItem',
    render: function () {
        console.log('NavigationBarItem', this.props.item);

        var component;
        if (this.props.item.content_type == "video") {
            component = VideoStatusIndicator({item: this.props.item})
        }
        if (this.props.item.content_type == "problem") {
            component = ProblemStatusIndicator({item: this.props.item})
        }
        return(
            React.DOM.div({className: "side-bar-el"}, 
                React.DOM.a({href: "#" + this.props.item.id}, 
                component
                )
            )
            );
    }
});

var MultipleChoiceSubmissionHistory = React.createClass({displayName: 'MultipleChoiceSubmissionHistory',
    mixins: [Listener],
    listenTo: [onGradingUpdate],

    getInitialState: function () {
        return {submissions: []};
    },

    render: function () {
        var rows = this.state.submissions.map(function (submission) {
            return (
                MultipleChoiceSubmissionHistoryItem({key: "mc-history-" + submission.sub_pk, submission: submission})
                );
        });

        var modalID = "history_window_" + this.props.item.id;
        return (
            React.DOM.div(null, 
                React.DOM.div({className: "pcrs-modal-history", id: modalID, 
                tabindex: "-1", 'aria-labelledby': "myModalLabel", 'aria-hidden': "true"}, 
                    React.DOM.div({className: "pcrs-modal-content"}, 

                        React.DOM.div({className: "pcrs-modal-header"}, 
                            React.DOM.h4({className: "pcrs-modal-title", title: "problem History"}, "Submission History"), 
                            React.DOM.button({type: "button", className: "close", 'data-dismiss': "modal", 'aria-hidden': "false", title: "Close History"})
                        ), 

                        React.DOM.div({className: "pcrs-modal-body"}, 
                            React.DOM.div({className: "pcrs-panel-group", id: "history_accordion"}, 
                            rows
                            )
                        ), 
                        React.DOM.div({className: "pcrs-modal-footer"}, 
                            React.DOM.button({type: "button", className: "reg-button", 'data-dismiss': "modal"}, "Close", 
                                React.DOM.span({className: "at"}, " Close History ")
                            )
                        )
                    )
                ), 

                React.DOM.button({ref: "historyButton", dataToggle: "modal", dataTarget: "#" + modalID, className: "reg-button"}, 
                "History"
                )

            ));
    },

    handleUpdate: function (event) {
        var newState = [event.detail.data].concat(this.state.submissions);
        this.setState({submissions: newState});
    }
});

var MultipleChoiceSubmissionHistoryItem = React.createClass({displayName: 'MultipleChoiceSubmissionHistoryItem',
    render: function () {
        var submission = this.props.submission;
        var classes = React.addons.classSet({
            "pcrs-panel-warning": submission.past_dead_line,
            "pcrs-panel-default": !submission.past_dead_line && !submission.best,
            "pcrs-panel-star": !submission.past_dead_line && submission.best
        });

               var collapseClasses = React.addons.classSet({
            "pcrs-panel-collapse": true,
            "collapse": true
        });

        return (React.DOM.div({className: classes}, 
                    React.DOM.div({className: "pcrs-panel-heading"}, 
                        React.DOM.h4({className: "pcrs-panel-title"}, 

                        React.DOM.a({className: "collapsed", 'data-toggle': "collapse", 'data-parent': "#history_accordion", href: "#history-"+submission.sub_pk}, 
                            "Submission title"
                            )
                        )
                    ), 
                    React.DOM.div({className: collapseClasses, id: "history-"+submission.sub_pk}, 
                        "submission stuff"
                    )
               ));
    }

});


$.ajax({
    url: document.URL + "/get_page_data",
    dataType: "json",
    async: false,
    success: function (problemData) {
        console.log("loaded data", problemData);
        data = problemData;
        React.renderComponent(
            ItemList({items: data.items}),
            document.getElementById("content_items")
        );
        // TODO initialize codemirror
        // Initialize code mirror instances.
//        $(".code-mirror").each(function (index, element) {
//            create_history_code_mirror("python", 3, element);
//        });
        React.renderComponent(
            NavigationBar({items: data.items}),
            document.getElementById("sidebar")
        );
    }

});