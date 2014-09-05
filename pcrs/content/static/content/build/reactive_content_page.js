/** @jsx React.DOM */


var ProblemScore = React.createClass({displayName: 'ProblemScore',
    mixins: [Listener, ProblemMixin],

    listenTo: [onStatusUpdate],

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
        this.setState({score: event.detail.score});
    },

    shouldComponentUpdate: function (nextProps, nextState) {
        return ((this.state.score == null ||
            (this.state.score < nextState.score)
            ));
    },

    render: function () {
        var maxScore = this.props.item.max_score;

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


var VideoWatched = React.createClass({displayName: 'VideoWatched',
    mixins: [Listener, Video],
    listenTo: [onStatusUpdate],

    render: function () {
        var videoWatched;
        if (this.state.completed) {
            videoWatched = React.DOM.span({className: "green-checkmark-icon"});
        }

        return React.DOM.span(null, videoWatched);
    }
});

var NavigationBar = React.createClass({displayName: 'NavigationBar',
    render: function () {
        var prevClass = React.addons.classSet({
            "icon-prev-active": data.prev_url,
            "icon-prev-inactive": !data.prev_url
        });

        var nextClass = React.addons.classSet({
            "icon-next-active": data.next_url,
            "icon-next-inactive": !data.next_url
        });


        var items = this.props.items.map(function (item) {
            if (item.content_type == "video" || item.content_type == "problem"){
                return NavigationBarItem({key: item.id, item: item});
            }
        });

        return (
                React.DOM.ul({className: "pcrs-sidenav"}, 
                    items, 
                    React.DOM.div({className: "row"}, 
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


$(function() {
    var url = document.URL.match('[^#]*')[0] + "/get_page_data";
    $.ajax({
        url: url,
        dataType: "json",
        async: false,
        success: function (problemData) {
            data = problemData;
            data.items.forEach(function (item) {
                if (item.content_type == "problem") {
                    React.renderComponent(
                        ProblemScore({item: item}),
                        document.getElementById("score-" + item.id));
                }
                if (item.content_type == "video") {
                    React.renderComponent(
                        VideoWatched({item: item}),
                        document.getElementById("watched-" + item.id));
                }
            });
            React.renderComponent(
            NavigationBar({items: data.items}),
            document.getElementById("sidebar")
        );
        }
    });
});

