/** @jsx React.DOM */

var data;
var problemsCompleted = {};

var QuestList = React.createClass({
    render: function () {
        var quests = data.quests.map(function (quest) {
            return (
                <Quest quest={quest} />
                );
        });
        return (
            <div className="QuestList">
                   {quests}
            </div>
            );
    }
});


var Quest = React.createClass({
    render: function () {
        var questID = 'Quest-' + this.props.quest.pk;
        var divInfo;
        var deadline = this.props.quest.deadline;

        var panelClasses = React.addons.classSet({
            "panel-collapse": true,
            "collapse": true
        });

        if (deadline) {
            if (this.props.quest.deadline_passed) {
                divInfo = (<div className="info">
                Submission closed on&nbsp;
                    <br className="info-sm"> {deadline}</br>
                </div>);

            }

            else {
                divInfo = (<div className="info">
                Due on&nbsp;
                    <br className="info-sm"> {deadline}</br>
                </div>);
            }
        }

        return (
            <div className="pcrs-panel-group">
                <div className="pcrs-panel">
                    <div className={this.props.quest.deadline_passed ? "quest-expired" : "quest-live"}>

                        <h4 className="pcrs-panel-title">
                            <a href={"#" + questID} className="collapsed" data-toggle="collapse">

                                <i className="collapse-indicator"></i>
                                {this.props.quest.name}
                                {divInfo}
                            </a>
                        </h4>
                    </div>
                    <div id={questID} className={panelClasses}>
                        <div className="quest-body" >
                            <h4>{this.props.quest.description}</h4>
                            <h3> Challenges </h3>
                            <ChallengeList questID={this.props.quest.pk} />
                        </div>
                    </div>
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
                    <Challenge challenge={challenge} />
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
            attempted: this.countAttempted(this.props.challenge.pk) > 0,
            completed: this.countCompleted(this.props.challenge.pk),
            total: this.countTotal(this.props.challenge.pk)
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
        return this.countCondition(challengeID, function (id) {
                return (
                    (data.items[id].content_type == 'video' &&
                        data.watched.hasOwnProperty(id)) ||
                    (data.items[id].content_type == 'problem' &&
                        (problemsCompleted.hasOwnProperty(id) ||
                            ProblemMixin.isProblemCompleted(data.items[id]
                            ))
                        )
                    );
            }
        );
    },

    countAttempted: function (challengeID) {
        return this.countCondition(challengeID, function (id) {
                return (
                    (data.items[id].content_type == 'video' &&
                        data.watched.hasOwnProperty(id)) ||
                    (data.items[id].content_type == 'problem' &&
                        ProblemMixin.isProblemAttempted(data.items[id]
                            )
                        )
                    );
            }
        );
    },

    countTotal: function (challengeID) {
        return this.countCondition(challengeID, function (id) {
                return (data.items[id].content_type == 'video' ||
                    (data.items[id].content_type == 'problem' &&
                        data.items[id].is_visible));
            }
        );
    },

    challengeScoreUpdate: function () {
        this.setState({
                attempted: true,
                completed: this.countCompleted(this.props.challenge.pk)
            }
        );
    },

    challengeItemsUpdate: function () {
        this.setState({
                total: this.countTotal(this.props.challenge.pk)
            }
        );
    },

    componentDidMount: function () {
        var component = this;

        var event = 'challengeUpdate' + this.props.challenge.pk;
        window.addEventListener(event, function (event) {
            component.challengeScoreUpdate()
        }, false);

        event = 'challengeItemsUpdate' + this.props.challenge.pk;
        window.addEventListener(event, function (event) {
            component.challengeItemsUpdate()
        }, false);

    },

    render: function () {
        var challengeID = this.props.challenge.id;

        var challengeStatusClass = React.addons.classSet({
            "challenge-not-attempted": !this.state.attempted && this.state.total != 0,
            "challenge-attempted": this.state.attempted &&
                                   !(this.state.completed == this.state.total),
            "challenge-completed": this.state.total != 0 &&
                                   this.state.completed == this.state.total,
            "challenge-empty": this.state.total == 0
        });

        var challengeMarkClass = React.addons.classSet({
            "challenge-mark-unknown": this.state.total == 0,
            "challenge-mark-incomplete": this.state.total != 0 &&
                                         this.state.completed != this.state.total,
            "challenge-mark-complete": this.state.completed == this.state.total &&
                                        this.state.total != 0
        });

        var panelClasses = React.addons.classSet({
            "pcrs-panel-body": true,
            "panel-collapse": true,
            "collapse": true
        });

        return (
            <div className="pcrs-panel">
                <div className={challengeStatusClass}>
                    <h4 className="pcrs-panel-title">
                        <a className="collapsed" data-toggle="collapse" href={"#" + challengeID}>
                            <i className="collapse-indicator"></i>
                            <span>
                                <i className={this.props.challenge.graded ? "credit-challenge" : "practice-challenge" }
                                title={(this.props.challenge.graded ? "Practice" : "Graded" ) + " Challenge"}>
                                </i>
                            </span>
                            <span dangerouslySetInnerHTML={{__html: this.props.challenge.name}} />
                            <div className={challengeMarkClass}>
                                <br className="info-sm" />
                                    {this.props.challenge.graded ? "Graded" : "Practice"}
                                <i className="complete-icon"></i>
                                <span className="challenge-mark">
                                    {this.state.completed} / {this.state.total}
                                </span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id={challengeID} className={panelClasses}>
                    <span dangerouslySetInnerHTML={{__html: this.props.challenge.description}} />
                    <PageList challengeID={this.props.challenge.pk}
                    challengeUrl={this.props.challenge.url}
                    challengeScoreUpdate={this.challengeScoreUpdate}
                    challengeItemsUpdate={this.challengeItemsUpdate}
                    />
                </div>
            </div>
            );
    }
});

var PageList = React.createClass({
    render: function () {
        var component = this;
        var total = (data.pages[this.props.challengeID] || []).length;
        var pageNodes = (data.pages[this.props.challengeID] || []).map(
            function (page) {
                return (
                    <Page page={page} total={total}
                    challengeScoreUpdate={component.props.challengeScoreUpdate}
                    challengeItemsUpdate={component.props.challengeItemsUpdate} />
                    );
            });
        return (
            <div>{pageNodes}</div>
            );
    }
});

var Page = React.createClass({
    render: function () {
        var component = this;
        var items = [];
        (data.item_lists[this.props.page.pk] || []).forEach(
            function (id) {
                var item = data.items[id];
                if (item.content_type == 'problem') {
                    items.push(
                        <Problem key={item.id} item={item}
                        pageUrl={component.props.page.url}
                        challengeScoreUpdate={component.props.challengeScoreUpdate}
                        challengeItemsUpdate={component.props.challengeItemsUpdate}
                        />
                        );
                }
                if (item.content_type == 'video') {
                    items.push(
                    <Video key={item.id} item={item}
                    pageUrl={component.props.page.url}
                    challengeScoreUpdate={component.props.challengeScoreUpdate}
                    challengeItemsUpdate={component.props.challengeItemsUpdate}
                    />)
                }

                 if (item.content_type == 'textblock') {
                    items.push(
                    <TextIcon key={item.id} item={item} pageUrl={component.props.page.url} />)
                }
            });


        return (
            <div className="challenge-page">
                <div className="pcrs-panel">
                    <div className="pcrs-panel-heading">
                        <a href={this.props.page.url} target="_blank">Go to Part {this.props.page.order}</a>
                    </div>
                    <div className="pcrs-panel-body">
                    {items}
                    </div>
                </div>
            </div>
            );
    }
});


var Problem = React.createClass({
    getInitialState: function () {
        return {isVisible: this.props.item.is_visible};
    },

    mixins: [Listener],
    listenTo: [onVisibilityUpdate],

    handleUpdate: function (event) {
        var isVisible = event.detail.item.properties.is_visible;
        data.items[event.detail.item.id].is_visible = isVisible;
        this.setState({isVisible: isVisible});
        this.props.challengeItemsUpdate()
    },

    render: function () {
        if (this.state.isVisible) {
            var url = this.props.pageUrl + "#" + this.props.item.id;
            return (
                <div>
                    <a href={url} target="_blank">
                        <ProblemStatusIndicator item={this.props.item} problemDidUpdate={this.problemDidUpdate}/>
                        {this.props.item.name}
                    </a>
                </div>
                );
        }
        else {
            return null;
        }
    },

    problemDidUpdate: function (problemCompleted) {
        if (problemCompleted) {
            problemsCompleted[this.props.item.id] = true;
        }
        this.props.challengeScoreUpdate();
    }

});

var Video = React.createClass({
    render: function () {
        var url = this.props.pageUrl + "#" + this.props.item.id;
        return (
            <div>
                <a href={url} target="_blank">
                    <VideoStatusIndicator item={this.props.item} videoDidUpdate={this.videoStatusDidUpdate} />
                    {this.props.item.name}
                </a>
            </div>
            );
    },

    videoStatusDidUpdate: function () {
        data.watched[this.props.item.id] = true;
        this.props.challengeScoreUpdate();
    }
});

var TextIcon = React.createClass({
    render: function () {
        var url = this.props.pageUrl + "#" + this.props.item.id;
        return (
            <div>
                <a href={url} target="_blank">
                    <span className="text-icon" />
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
        data = newData;
        React.renderComponent(
            <QuestList />,
            document.getElementById("quests")
        );
    }
});