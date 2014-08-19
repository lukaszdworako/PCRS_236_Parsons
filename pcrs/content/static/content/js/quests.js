/** @jsx React.DOM */

var data;

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
    mixins: [Problem],

    getInitialState: function () {
        return {
            completed: this.countCompleted(this.props.id),
            total: this.countTotal(this.props.id)
        }
    },

    countCondition: function (challengeID, condition) {
        var count = 0;

        // iterate over pages in challenge
        if (data.pages.hasOwnProperty(challengeID)) {
            for (var i = 0; i < data.pages[challengeID].length; i++) {
                var page = data.pages[challengeID][i];
                // iterate over problems on the page
                if (data.item_lists.hasOwnProperty(page.pk)) {

                    for (var j = 0; j < data.item_lists[page.pk].length; j++) {
                        var id = data.item_lists[page.pk][j];
                        if (condition(id)) {
                            count += 1;
                        }
                    }
                }
            }
        }
        return count;
    },

    countCompleted: function (challengeID) {
        var component = this;
        return this.countCondition(challengeID, function (id) {
                return (data.items[id].content_type == 'problem' &&
                        component.isProblemCompleted(data.items[id]));
            }
        );
    },

    countTotal: function (challengeID) {
        return this.countCondition(challengeID, function (id) {
                return (data.items[id].content_type == 'problem' &&
                        data.items[id].is_visible);
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
                    <Page page={page} total={total} >
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
                    <a href={this.props.page.url} target="_blank">Go to Part {this.props.order}</a>
                </div>
                <div className="panel-body">
                    <ItemList page={this.props.page} />
                </div>
            </div>
            );
    }
});

var ItemList = React.createClass({
    render: function () {
        var component = this;
        var problemNodes = (data.item_lists[this.props.page.pk] || []).map(
            function (id) {
                var item = data.items[id];
                if (item.content_type == 'problem') {
                    return (
                        <Problem key={item.id} problem={item} pageUrl={component.props.page.url}/>
                        );
                }
                if (item.content_type == 'video') {
                    return <Video key={item.id} item={item} pageUrl={component.props.page.url}/>
                }
            });
        return (
            <div>{problemNodes}</div>
            );
    }
});

var Problem = React.createClass({
    render: function () {
        var url = this.props.pageUrl + "#" + this.props.problem.id;
        return (
            <div>
                <a href={url} target="_blank">
                    <ProblemStatusIndicator item={this.props.problem}/>
                    {this.props.problem.name}
                </a>
            </div>
            );
    }

});

var Video = React.createClass({


    render: function () {
        console.log('Video');

        return (
            <div>
                <a href={this.props.item.link} target="_blank">
                    <VideoStatusIndicator item={this.props.item} />
                    {this.props.item.name}
                </a>
            </div>
            );
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