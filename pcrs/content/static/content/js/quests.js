/** @jsx React.DOM */

//var quests = [
//    {pk: 1, name: 'testquest', deadline: null}
//];
//
//var challenges = {
//    1: [
//        {pk: 1, name: 'c1', graded: false}
//    ]
//};
//
//var pages = {
//    1: [
//        {pk: 1, order: 1}
//    ]
//};
//
//var problem_lists = {
//    1: ['code-1', 'code-2', 'code-3']
//};
//
//var problems = {
//    "code": {
//        1: {name: 'Problem 1 (not att)', challenge: 1},
//        2: {name: 'Problem 2 (att)', challenge: 1},
//        3: {name: 'Problem 3 (solved)', challenge: 1}
//    }
//};
//
//var problems_attempted = {
//    'code': {2: true, 3: true}
//};
//
//var problems_completed = {
//    'code': {3: true}
//};
//
//var challenge_to_completed = {
//  1: 1, 2:0
//};
//
//var challenge_to_total = {
//    1: 3,
//    2: 0
//};

var data;

function is_problem_attempted(pType, pID) {
    return (data.problems_attempted.hasOwnProperty(pType) &&
        data.problems_attempted[pType].hasOwnProperty(pID) &&
        data.problems_attempted[pType][pID]);
}

function is_problem_completed(pType, pID) {
    return (data.problems_completed.hasOwnProperty(pType) &&
        data.problems_completed[pType].hasOwnProperty(pID) &&
        data.problems_completed[pType][pID]);
}

function countCompleted(challengeID) {

}

var ToggleMixin = {
    toggle: function (e) {
        this.setState({visible: !this.state.visible});
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
    },
    getInitialState: function () {
        return {
            visible: true
        };
    }
};

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
        data.problems_attempted[problem.problem_type][problem.pk] = status.attempted;
        data.problems_completed[problem.problem_type][problem.pk] = status.completed;
        this.setState({data: data.quests});

        // calculate number completed in challenge after the update

    },

    updateProblems: function (problem) {
        console.log('updating problem');
        var problemToUpdate = data.problems[problem.problem_type][problem.pk];
        for (var property in problem.properties) {
            console.log(property);
            if (problemToUpdate.hasOwnProperty(property)) {
                problemToUpdate[property] = problem.properties[property];
                console.log(problem.properties[property]);
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
    mixins: [ToggleMixin],

    render: function () {
        var id = 'Quest-' + this.props.pk;

        var style = {};

        if (!this.state.visible) {
            style.display = "none";
        }

        return (
            <div id={id}
            onClick={this.toggle}>
                <h3>
                    <a>{this.props.name}
                        <span className="pull-right">{this.props.deadline}</span>
                    </a>
                </h3>
                <div id={this.props.pk} style={style}>
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
                    <Challenge id={challenge.pk} name={challenge.name} graded={challenge.graded}>
                    </Challenge>
                    );
            });
        return (
            <div>{challengeNodes}</div>
            );
    }
});

var Challenge = React.createClass({
    mixins: [ToggleMixin],

    render: function () {
        var style = {};
        if (!this.state.visible) {
            style.display = "none";
        }

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
                <div style={style}>
                    <PageList challengeID={this.props.id} />
                </div>
            </div>
            );
    }
});

var PageList = React.createClass({

    render: function () {
        var total = (data.pages[this.props.challengeID] || []).length;
        var pageNodes = (data.pages[this.props.challengeID] || []).map(
            function (page) {
                return (
                    <Page id={page.pk} order={page.order} total={total}></Page>
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
                <div className="panel-heading">Page {this.props.order} of {this.props.total}</div>
                <div className="panel-body">
                    <ProblemList pageID={this.props.id} />
                </div>
            </div>
            );
    }
});

var ProblemList = React.createClass({
    render: function () {
        console.log('rendering page ', this.props.pageID, data.problem_lists[this.props.pageID]);

        var problemNodes = (data.problem_lists[this.props.pageID] || []).map(
            function (problemID) {
                problemID = problemID.split('-');
                var pType = problemID[0];
                var pID = problemID[1];
                var problem = data.problems[pType][pID];
                var attempted = is_problem_attempted(pType, pID);
                var completed = is_problem_completed(pType, pID);
                if (problem.is_visible) {
                    return (
                        <Problem name={problem.name}
                        attempted={attempted} completed={completed}/>
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
            'problem-not-attempted': !this.props.attempted,
            'problem-attempted': this.props.attempted,
            'problem-completed': this.props.completed
        });
        return (
            <div>
                <i className={classes}></i>{this.props.name}
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

//renderQuestList();