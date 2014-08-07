/** @jsx React.DOM */

var data;

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

function countCompleted(challengeID) {
    var count = 0;
    console.log(data.pages[challengeID]);
    // iterate over pages in challenge
    for (var i = 0; i < data.pages[challengeID].length; i++) {
        var page = data.pages[challengeID][i];
        console.log("page", page);
        // iterate over problems on the page
        for (var j = 0; j < data.problem_lists[page.pk].length; j++) {

            var pID = data.problem_lists[page.pk][j];
            var pType = pID.split('-')[0];
            var ID = pID.split('-')[1];
            console.log("id", pType, ID);

            if (isProblemCompleted(pType, ID))
                count += 1;
        }
    }
    return count;
}


var QuestList = React.createClass({
    getInitialState: function () {
        return {data: quests};
    },

    componentWillMount: function () {
        var component = this;
        socket.on(userhash, function (data) {
            component.updateProblemStatus(data.problem, data.status);
        });

        socket.on('problems', function (data) {
            component.updateProblems(data.problem);
        });
    },

    updateProblemStatus: function (problem, status) {
        if (status.hasOwnProperty('attempted')) {
            data.problems_attempted[problem.problem_type][problem.pk] = status.attempted;
            this.setState({data: data.quests});
        }
        if (status.hasOwnProperty('completed')) {
            var currentStatus = data.problems_completed[problem.problem_type][problem.pk];
            data.problems_completed[problem.problem_type][problem.pk] = status.completed;
            if (currentStatus != status.completed) {
                // calculate number completed in challenge after the update
                var challengeID = data.problems[problem.problem_type][problem.pk].challenge;
                data.challenge_to_completed[challengeID] = countCompleted(challengeID);
                this.setState({data: data.quests});
            }
        }
    },

    updateProblems: function (problem) {
        var problemToUpdate = data.problems[problem.problem_type][problem.pk];
        for (var property in problem.properties) {
            if (problemToUpdate.hasOwnProperty(property)) {
                problemToUpdate[property] = problem.properties[property];
            }
        }
        this.setState({data: data.quests});
    },

    render: function () {
        var questNodes = data.quests.map(function (quest) {
            return (
                <Quest name={quest.name} deadline={quest.deadline} pk={quest.pk}>
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
            <div id={'Quest-' + this.props.pk}
            onClick={this.toggle}>
                <h3>
                    <a>{this.props.name}
                        <span className="pull-right">{this.props.deadline}</span>
                    </a>
                </h3>
                <div id={this.props.pk}>
                    <ChallengeList questID={this.props.pk} />
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
    render: function () {
        var challengeID = this.props.id;

        var total = data.challenge_to_total[challengeID] || 0;
        var completed = data.challenge_to_completed[challengeID] || 0;

        var classes = React.addons.classSet({
            'challenge-not-attempted': completed == 0,
            'challenge-attempted': completed > 0,
            'challenge-completed': completed == total
        });

        var graded = this.props.graded ? 'Graded' : 'Practice';

        return (
            <div onClick={this.toggle}>
                <h3 className={classes}>{this.props.name}
                    <span className="pull-right">
                    {graded}:
                    {completed}/{total}
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

                var attempted = isProblemAttempted(pType, pID);
                var completed = isProblemCompleted(pType, pID);
                var url = pageUrl + '#' + pType + '-' + pID;

                if (problem.is_visible) {
                    return (
                        <Problem name={problem.name}
                        attempted={attempted} completed={completed}
                        url={url}
                        />
                        );
                }
            });
        return (
            <div>{problemNodes}</div>
            );
    }
});

var Problem = React.createClass({
    render: function () {
        var classes = React.addons.classSet({
            'glyphicon': true,
            'glyphicon-edit': true,
            'problem-idle': !this.props.attempted,
            'problem-attempted': this.props.attempted && !this.props.completed,
            'problem-complete': this.props.completed
        });
        return (
            <div>
                <a href={this.props.url} target="_blank">
                    <i className={classes}></i>{this.props.name}
                </a>
            </div>
            );
    }
});


function renderQuestList() {
    React.renderComponent(
        <QuestList />,
        document.getElementById("quests")
    );
}

$.ajax({
    url: 'get_quest_list',
    dataType: 'json',
    success: function (newData) {
        console.log('loaded data', newData);
        data = newData;
        renderQuestList();
    }
});