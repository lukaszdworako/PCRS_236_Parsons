/** @jsx React.DOM */

var quests = [
    {pk: 1, name: 'testquest', dealine: null},
    {pk: 2, name: 'testquest2', dealine: 'tomorrow'}
];

var challenges = {
    1: [
//        {pk: '01', name: 'c1', num_completed: 0, total: 2},
//        {pk: '02', name: 'c2', num_completed: 1, total: 2}
    ],
    2: [
        {pk: '03', name: 'c3', num_completed: 1, total: 2},
        {pk: '04', name: 'c4', num_completed: 1, total: 2}
    ]
};


socket.on('problems', function (data) {
    console.log(data);
    problems.push(data);
    renderProblemList();
});

socket.on('user007', function (data) {
    console.log('received for user: ', data);
});

var QuestList = React.createClass({

    componentDidMount: function () {
//        $.ajax({
//            url: '/content/quests/data',
//            dataType: 'json',
//            success: function (data) {
//                quests = data;
//                this.setState({data: quests});
//            }.bind(this)
//        });
        this.setState({data: quests});
    },

    render: function () {
        var questNodes = quests.map(function (quest) {
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

    getInitialState: function () {
        return {
            visible: true
        };
    },

    render: function () {
        var id = 'Quest-' + this.props.pk;

        var style = {};

        if (!this.state.visible) {
            style.display = "none";
        }
        console.log(this.state.visible);

        return (
            <div className="quest well" id={id}
            onClick={this.toggle}>
                <h3>{this.props.name}</h3>
                <h5>{this.props.deadline}</h5>

                <div id={this.props.pk} style={style}>
                    <ChallengeList id={this.props.pk} />
                </div>
            </div>

            );
    },

    toggle: function () {
        console.log('click');
        this.setState({visible: !this.state.visible});
    }
});


var ChallengeList = React.createClass({

    componentDidMount: function () {
//        $.ajax({
//            url: '/content/quests/data',
//            dataType: 'json',
//            success: function (data) {
//                quests = data;
//                this.setState({data: quests});
//            }.bind(this)
//        });
    },

    render: function () {
        var challengeNodes = challenges[this.props.id].map(
            function (challenge) {
                return (
                    <Challenge name={challenge.name}
                    num_completed={challenge.num_completed}
                    total={challenge.total}>
                    </Challenge>
                    );
            });
        var id = 'ChallengeList-' + this.props.id;
        return (
            <div>
                   {challengeNodes}
            </div>
            );
    }


});

var Challenge = React.createClass({

    render: function () {
        var classes = React.addons.classSet({
            'challenge': true,
            'completed': this.props.num_completed == this.props.total
        });
        return (
            <div className={classes}>
                <h3>{this.props.name}</h3>
                <h5>{this.props.num_completed}/{this.props.total}</h5>
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

function renderChallengeList(quest_id) {
    React.renderComponent(
        <ChallengeList id={quest_id} />,
        document.getElementById("ChallengeList-" + quest_id)
    );
}

renderQuestList();