/** @jsx React.DOM */


var ItemList = React.createClass({
    render: function () {
        var items = this.props.items.map(function (item) {
            if (item.content_type == 'problem') {
                return <Problem key={item.id} item={item} />;
            }
            if (item.content_type == 'video') {
                return <Video key={item.id} item={item} />;
            }
        });
        return <div>{items}</div>;
    }
});

var Problem = React.createClass({

    getProblemForm: function (problem) {
        if (problem.problem_type == 'multiple_choice') {
            return (
                <MultipleChoiceProblemForm item={problem} />
                );
        }
        else {
            return (
                <ProgrammingProblemForm item={problem} />
                );
        }
    },

    render: function () {
        var problem = this.props.item;
        return (
            <div id={problem.id}>
                <div>
                    <h3>
                        <span dangerouslySetInnerHTML={{__html: problem.name}} />
                        <ProblemScore item={problem} />
                    </h3>
                </div>
                <p dangerouslySetInnerHTML={{__html: problem.description}} />

                {this.getProblemForm(problem)}

                <hr />
            </div>

            );
    }
});

var ProblemScore = React.createClass({
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
            score = <span className="green-checkmark-icon" />;
        }

        else {
            score = (
                <span>
                    <sup>{this.state.score != null ? this.state.score : '-'}</sup>
                /
                    <sub>{maxScore}</sub>
                </span>);
        }

        return (<span title="Progress so far" className="align-right">
            {score}
        </span>);
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

var ProgrammingProblemForm = React.createClass({

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
            <div>
                <div>
                    <textarea defaultValue={this.props.item.starter_code}
                    ref="submission" className="code-mirror" />
                    <button ref="submitButton" className="green-button"
                    onClick={this.handleSubmit}>
                    Submit
                    </button>
                </div>

                <ProgrammingProblemGrading item={this.props.item} postRender={this.enableButton}/>

            </div>
            );
    }
});

var MultipleChoiceProblemForm = React.createClass({
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
                <span>
                    <input type="checkbox" name="anwer_options"
                    value={option.pk}
                    onChange={component.updateSelectedOptions}>
                         {option.text}
                        <br/>
                    </input>

                </span>
                );
        });

        return (
            <div>
                <div>{options}
                    <button ref="submitButton" className="submitBtn"
                    onClick={this.handleSubmit}>Submit</button>
                </div>

                <MultipleChoiceGrading item={this.props.item} postRender={this.enableButton} />
                <MultipleChoiceSubmissionHistory key={"history-" + this.props.item.id} item={this.props.item} />
            </div>

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

var MultipleChoiceGrading = React.createClass({
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
                <SubmissionCorrectMessage /> :
                <SubmissionIncorrectMessage
                message="This solution is not entirely correct." />);
        }
        return (
            <div>
                {correctness}
            </div>
            );
    }
});

var ProgrammingProblemGrading = React.createClass({
    mixins: [Listener, Grading],
    listenTo: [onGradingUpdate],


    getStatusMessage: function () {
        var correctness;
        var error;

        if (this.state.data) {
            correctness = this.state.data.score == this.props.item.max_score ?
                <SubmissionCorrectMessage /> :
                <SubmissionIncorrectMessage
                message="This solution has passed x out of y testcases." />;

            var errorMessage = this.state.data.results[1] || "";
            if (errorMessage) {
                error = <SubmissionErrorMessage error={errorMessage} />
            }
            return (
                <div>
                    {correctness}
                    {error}
                </div>
                );
        }
    },

    getGradingTable: function () {

        if (this.state.data) {
            var error = this.state.data.results[1];
            var testruns = this.state.data.results[0];
            if (!error && this.props.item.problem_type == 'code') {
                return <CodeProblemTestcaseTable testruns={testruns} />;
            }

            if (!error && (this.props.item.problem_type == 'sql' ||
                this.props.item.problem_type == 'ra')) {
                return <RDBProblemTestcaseTable testruns={testruns} />;
            }
        }
    },

    render: function () {
        return (
            <div>
                {this.getStatusMessage()}
                {this.getGradingTable()}
            </div>
            );
    }
});


var CodeProblemTestcaseTable = React.createClass({
    render: function () {
        var tableRows = this.props.testruns.map(function (testrun) {
            return (
                <tr className="pcrs-table-row">
                    <td className="description">{testrun.test_desc}</td>
                    <td className="expression">{testrun.test_input || "Hidden Test"}
                        <div className="expression_div"></div>

                    </td>

                    <td className="expected">{testrun.expected_output || "Hidden Result"}
                        <div className="ptd">
                            <div className="ExecutionVizualizer" />
                        </div>
                    </td>
                    <td className="result">{testrun.test_val}</td>
                    <div className="ptd">
                        <div className="ExecutionVizualizer" />
                    </div>
                    <td className="passed">
                    {
                        testrun.test_passed ?
                            <img id="dynamic" src={happyFaceURL} alt='Happy Face'
                            height="36" width="36" /> :
                            <img id="dynamic" src={sadFaceURL} alt='Sad Face'
                            height="36" width="36" />
                        }

                    </td>
                    <td className="debug">Debug</td>

                    <a className="at">This testcase has __ (if failed, expected and result)</a>
                </tr>
                );
//            TODO: fix me
        });

        var classes = React.addons.classSet({
            "hidden": !this.props.testruns,
            "pcrs-table": true
        });

        return (
            <div>
                <table className={classes}>
                    <thead>
                        <tr className="pcrs-table-head-row">
                            <th className="description">Description</th>
                            <th className="expression">Test Expression</th>
                            <th className="expected">Expected</th>
                            <th className="result">Result</th>
                            <th className="passed">Passed</th>
                            <th className="debug">Debug</th>
                        </tr>
                    </thead>
                    <tbody>
                    {tableRows}
                    </tbody>
                </table>
            </div>
            );
    }
});


var RDBProblemTestcaseTable = React.createClass({
    render: function () {
        console.log(this.props.testruns);

        var tables = this.props.testruns.map(function (testrun) {
            if (testrun.error) {
                return <ErrorMessage error={testrun.error} />;

            }
            // TODO: put tables side by side
            return (
                <div>
                    <Table attributes={testrun.expected_attrs}
                    data={testrun.expected} />
                    <Table attributes={testrun.actual_attrs}
                    data={testrun.actual} />
                </div>
                );
        });

        return (
            <div>
                {tables}
            </div>
            );
    }
});


var ProblemStatusMessage = React.createClass({
    render: function () {
        console.log('ProblemStatus');
        var error;
        if (this.props.error) {
            error = <SubmissionErrorMessage error={this.props.error} />;
        }
        return (
            <div>
                <div className="ProblemStatusMessage">{this.props.message}</div>
                {error}
            </div>
            );
    }

});

var SubmissionErrorMessage = React.createClass({
    render: function () {
        return <div className="red-alert">{this.props.error}</div>;
    }
});

var SubmissionCorrectMessage = React.createClass({
    render: function () {
        return (<div className="green-alert">
        Correct!
        </div>);
    }
});

var SubmissionIncorrectMessage = React.createClass({
    render: function () {
        return (<div className="red-alert">
            {this.props.message}
        </div>);
    }
});

var Table = React.createClass({
    getDataInRow: function (attributes, rowObject) {
        return attributes.map(function (attribute) {
            return rowObject[attribute];
        });
    },

    render: function () {
        var component = this;

        var tableHeader = this.props.attributes.map(function (attribute) {
            return (
                <th>
                    {attribute}
                </th>
                );
        });

        var tableRows = this.props.data.map(function (row) {
            var cells = component.getDataInRow(component.props.attributes, row)
                .map(function (cell) {
                    return (
                        <td>{cell}</td>
                        );
                });

            var classes = React.addons.classSet({
                'extra': row.extra,
                'missing': row.missing,
                'out_of_order': row.out_of_order
            });
            return (
                <tr>{cells}</tr>
                )
                ;
        });
        return (
            <div>
                <table>
                    <thead>
                        <tr>{tableHeader}</tr>
                    </thead>
                    <tbody>
                    {tableRows}
                    </tbody>
                </table>
            </div>
            );
    }
});


var Video = React.createClass({
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
            videoWatched = <span className="video-complete">done</span>
        }

        return (
            <div>
                <div>
                {this.props.item.name} {videoWatched}
                </div>
                <div id={video.id} onClick={this.handleClick}>
                    <video
                    className={videoClasses}
                    controls
                    preload="auto"
                    data-setup={videoControls}
                    poster={video.thumbnail}>
                        <source src={video.url} type='rtmp/mp4' />
                    </video>
                </div>
            </div>
            );
    }
});

var NavigationBar = React.createClass({
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
            return <NavigationBarItem key={item.id} item={item} />;
        });

        return (
            <div className="pcrs-sidebar" role="complementary">
                <ul className="pcrs-sidenav">
                    {items}
                    <a className="side-bar-arrow" href={data.prev_url}>
                        <span className={prevClass}></span>
                    </a>
                    <a className="side-bar-arrow" href={data.next_url}>
                        <span className={nextClass}></span>
                    </a>
                </ul>
            </div>
            );

    }
});

var NavigationBarItem = React.createClass({
    render: function () {
        console.log('NavigationBarItem', this.props.item);

        var component;
        if (this.props.item.content_type == "video") {
            component = <VideoStatusIndicator item={this.props.item} />
        }
        if (this.props.item.content_type == "problem") {
            component = <ProblemStatusIndicator item={this.props.item} />
        }
        return(
            <div className="side-bar-el">
                <a href={"#" + this.props.item.id}>
                {component}
                </a>
            </div>
            );
    }
});

var MultipleChoiceSubmissionHistory = React.createClass({
    mixins: [Listener],
    listenTo: [onGradingUpdate],

    getInitialState: function () {
        return {submissions: []};
    },

    render: function () {
        var rows = this.state.submissions.map(function (submission) {
            return (
                <MultipleChoiceSubmissionHistoryItem key={"mc-history-" + submission.sub_pk} submission={submission} />
                );
        });

        var modalID = "history_window_" + this.props.item.id;
        return (
            <div>
                <div className="pcrs-modal-history" id={modalID}
                tabindex="-1" aria-labelledby="myModalLabel" aria-hidden="true">
                    <div className="pcrs-modal-content">

                        <div className="pcrs-modal-header">
                            <h4 className="pcrs-modal-title" title="problem History">Submission History</h4>
                            <button type="button" className="close" data-dismiss="modal" aria-hidden="false" title="Close History"></button>
                        </div>

                        <div className="pcrs-modal-body">
                            <div className="pcrs-panel-group" id="history_accordion">
                            {rows}
                            </div>
                        </div>
                        <div className="pcrs-modal-footer">
                            <button type="button" className="reg-button" data-dismiss="modal">Close
                                <span className="at"> Close History </span>
                            </button>
                        </div>
                    </div>
                </div>

                <button ref="historyButton" dataToggle="modal" dataTarget={"#" + modalID} className="reg-button">
                History
                </button>

            </div>);
    },

    handleUpdate: function (event) {
        var newState = [event.detail.data].concat(this.state.submissions);
        this.setState({submissions: newState});
    }
});

var MultipleChoiceSubmissionHistoryItem = React.createClass({
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

        return (<div className={classes}>
                    <div className="pcrs-panel-heading">
                        <h4 className="pcrs-panel-title">

                        <a className="collapsed" data-toggle="collapse" data-parent="#history_accordion" href={"#history-"+submission.sub_pk}>
                            Submission title
                            </a>
                        </h4>
                    </div>
                    <div className={collapseClasses} id={"history-"+submission.sub_pk}>
                        submission stuff
                    </div>
               </div>);
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
            <ItemList items={data.items} />,
            document.getElementById("content_items")
        );
        // TODO initialize codemirror
        // Initialize code mirror instances.
//        $(".code-mirror").each(function (index, element) {
//            create_history_code_mirror("python", 3, element);
//        });
        React.renderComponent(
            <NavigationBar items={data.items} />,
            document.getElementById("sidebar")
        );
    }

});