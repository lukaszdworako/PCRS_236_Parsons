/** @jsx React.DOM */

var data;

// Listen for updates to problems.
// These events are dispatched by the socket listener.
window.addEventListener('problemUpdate', function (event) {
    var receiver = 'problemUpdate-' +
        event.detail.problem.problem_type + event.detail.problem.pk;
    window.dispatchEvent(
        new CustomEvent(receiver, {detail: event.detail})
    );
}, false);

window.addEventListener('problemStatusUpdate', function (event) {
    var receiver = 'problemStatusUpdate-' +
        event.detail.problem.problem_type + event.detail.problem.pk;
    console.log('propagating', receiver);
    window.dispatchEvent(
        new CustomEvent(receiver, {detail: event.detail})
    );
}, false);

function isProblemAttempted(pType, pID) {
    return (data.problems_attempted.hasOwnProperty(pType) &&
        data.problems_attempted[pType].hasOwnProperty(pID) &&
        data.problems_attempted[pType][pID]);
}

function isProblemCompleted(pType, pID) {
    return (data.problems_completed.hasOwnProperty(pType) &&
        data.problems_completed[pType].hasOwnProperty(pID) &&
        data.problems_completed[pType][pID]);
}

function isProblemVisible(pType, pID) {
    return data.problems[pType][pID].is_visible;
}

var QuestList = React.createClass({
    render: function () {
        var questNodes = data.quests.map(function (quest) {
            return (
                <Quest id={quest.pk} name={quest.name}
                deadline={quest.deadline}>
                </Quest>
                );
        });
        return (
            <div className="QuestList">
                   {questNodes}
            </div>
            );
    }
});


var Quest = React.createClass({
    render: function () {
        return (
            <div id={'Quest-' + this.props.id}>
                <h3>
                    <a>{this.props.name}
                        <span className="pull-right">{this.props.deadline}</span>
                    </a>
                </h3>
                <div id={this.props.id}>
                    <ChallengeList questID={this.props.id} />
                </div>
            </div>
            );
    }
});


var ChallengeList = React.createClass({
    render: function () {

        var challengeNodes = (data.challenges[this.props.questID] || []).map(
            function (challenge) {
                return (
                    <Challenge id={challenge.pk} name={challenge.name}
                    graded={challenge.graded} url={challenge.url}>
                    </Challenge>
                    );
            });
        return (
            <div>{challengeNodes}</div>
            );
    }
});

var Challenge = React.createClass({
    getInitialState: function () {
        return {
            completed: this.countCompleted(this.props.id),
            total: this.countTotal(this.props.id)
        }
    },

    countCondition: function (challengeID, condition) {
        var count = 0;
        console.log('challengepk', challengeID);

        // iterate over pages in challenge
        if (data.pages.hasOwnProperty(challengeID)) {
            for (var i = 0; i < data.pages[challengeID].length; i++) {
                var page = data.pages[challengeID][i];
                // iterate over problems on the page
                if (data.problem_lists.hasOwnProperty(page.pk)) {

                    for (var j = 0; j < data.problem_lists[page.pk].length; j++) {
                        var ID = data.problem_lists[page.pk][j];
                        var pType = ID.split('-')[0];
                        var pID = ID.split('-')[1];
                        if (condition(pType, pID)) {
                            count += 1;
                        }
                    }
                }
            }
        }
        return count;
    },

    countCompleted: function (challengeID) {
        return this.countCondition(challengeID, function (pType, pID) {
                return isProblemVisible(pType, pID) &&
                       isProblemCompleted(pType, pID);
            }
        );
    },

    countTotal: function (challengeID) {
        return this.countCondition(challengeID, function (pType, pID) {
                return isProblemVisible(pType, pID);
            }
        );
    },

    componentDidMount: function () {
        var component = this;
        var event = 'challengeUpdated-' + this.props.id;
        window.addEventListener(event, function (event) {
            component.setState({
                    completed: component.countCompleted(component.props.id),
                    total: component.countTotal(component.props.id)
                }
            );
        }, false);

    },

    render: function () {
        var classes = React.addons.classSet({
            'challenge-not-attempted': this.state.completed == 0,
            'challenge-attempted': this.state.completed > 0,
            'challenge-completed': this.state.completed == this.state.total
        });

        return (
            <div onClick={this.toggle}>
                <h3 className={classes}>{this.props.name}
                    <span className="pull-right">
                    {this.props.graded ? 'Graded' : 'Practice'}:
                    {this.state.completed}/{this.state.total}
                    </span>
                </h3>
                <div>
                    <PageList challengeID={this.props.id}
                    challengeUrl={this.props.url} />
                </div>
            </div>
            );
    }
});

var PageList = React.createClass({
    render: function () {
        var url = this.props.challengeUrl;
        var total = (data.pages[this.props.challengeID] || []).length;
        var pageNodes = (data.pages[this.props.challengeID] || []).map(
            function (page) {
                return (
                    <Page id={page.pk} order={page.order} total={total}
                    url={url + '/' + page.order}>
                    </Page>
                    );
            });
        return (
            <div>{pageNodes}</div>
            );
    }
});

var Page = React.createClass({
    render: function () {
        var classes = React.addons.classSet({
            'panel': true,
            'panel-default': true,
            'problem-page': true
        });
        return (
            <div className={classes}>
                <div className="panel-heading">
                    <a href={this.props.url} target="_blank">Go to Part {this.props.order}</a>
                </div>
                <div className="panel-body">
                    <ProblemList pageID={this.props.id} pageUrl={this.props.url}/>
                </div>
            </div>
            );
    }
});

var ProblemList = React.createClass({
    render: function () {
        var pageUrl = this.props.pageUrl;

        var problemNodes = (data.problem_lists[this.props.pageID] || []).map(
            function (problemID) {
                problemID = problemID.split('-');
                var pType = problemID[0];
                var pID = problemID[1];
                var problem = data.problems[pType][pID];

                return (
                    <Problem pType={pType} id={pID}
                    challengeID={problem.challenge}
                    name={problem.name}
                    url={pageUrl + '#' + pType + '-' + pID}/>
                    );
            });
        return (
            <div>{problemNodes}</div>
            );
    }
});

var Problem = React.createClass({

    getInitialState: function () {
        var pType = this.props.pType;
        var pID = this.props.id;
        return {
            attempted: isProblemAttempted(pType, pID),
            completed: isProblemCompleted(pType, pID),
            isVisible: isProblemVisible(pType, pID)
        }
    },

    componentDidMount: function () {
        var component = this;

        // Listen for problem updates.
        var update = 'problemUpdate-' + this.props.pType + this.props.id;
        window.addEventListener(update, function (event) {
            // Update problem properties
            component.updateProblem(event);
        }, false);

        update = 'problemStatusUpdate-' + this.props.pType + this.props.id;

        window.addEventListener(update, function (event) {
            // Update problem attempted / completed state.
            console.log('captured');
            component.updateProblemStatus(event);
        }, false);
    },

    render: function () {
        var problemVisibilityClass = React.addons.classSet({
            'hidden': !this.state.isVisible
        });

        var problemClasses = React.addons.classSet({
            'glyphicon': true,
            'glyphicon-edit': true,
            'problem-idle': !this.state.attempted,
            'problem-attempted': this.state.attempted && !this.state.completed,
            'problem-complete': this.state.completed
        });

        return (
            <div className={problemVisibilityClass}>
                <a href={this.props.url} target="_blank">
                    <i className={problemClasses}></i>{this.props.name}
                </a>
            </div>
            );
    },

    updateProblemStatus: function (event) {
        console.log('updating');
        console.log(event.detail);

        var problem = event.detail.problem;
        var status = event.detail.status;

        var attempted = status.attempted || this.state.attempted;
        var completed = status.completed || this.state.completed;

        data.problems_attempted[problem.problem_type][problem.pk] = attempted;

        if (status.hasOwnProperty('completed')) {
            var currentStatus = data.problems_completed[problem.problem_type][problem.pk];
            data.problems_completed[problem.problem_type][problem.pk] = status.completed;

            if (currentStatus != status.completed) {
                // Problem completion status has changed.
                // Challenge needs to update.
                window.dispatchEvent(
                    new CustomEvent('challengeUpdated-' + this.props.challengeID)
                );
            }
        }
        this.setState({
            attempted: attempted,
            completed: completed
        });
    },

    updateProblem: function (event) {
        var problem = event.detail.problem;
        var problemToUpdate = data.problems[problem.problem_type][problem.pk];

        var previousVisibility = problemToUpdate.is_visible;

        for (var property in problem.properties) {
            if (problemToUpdate.hasOwnProperty(property)) {
                problemToUpdate[property] = problem.properties[property];
            }
        }
        if (previousVisibility != problemToUpdate.is_visible) {
            // Problem visibility has changed. Challenge needs to update.
            window.dispatchEvent(
                new CustomEvent('challengeUpdated-' + this.props.challengeID)
            );
        }

        this.setState({
            isVisible: problemToUpdate.is_visible
        });


    }
});

$.ajax({
    url: 'get_quest_list',
    dataType: 'json',
    success: function (newData) {
        console.log('loaded data', newData);
        data = newData;
        React.renderComponent(
            <QuestList />,
            document.getElementById("quests")
        );
    }
});