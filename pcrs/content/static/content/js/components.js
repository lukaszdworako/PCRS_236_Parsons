/** @jsx React.DOM */



var Listener = {
    componentDidMount: function () {
        var component = this;
        component.listenTo.forEach(function (listener) {
            window.addEventListener(listener.onUpdate(component),
                function (event) {
                    console.log("Listener received message");
                    listener.handleUpdate(component, event);
                }, false);
        });
    }
};


var onStatusUpdate = {
    onUpdate: function (component) {
        return "statusUpdate" + component.props.item.id;
    },

    handleUpdate: function (component, event) {
        console.log('Handling status update');
        component.setState(event.detail.status);
    }
};

var onGradingUpdate = {
    onUpdate: function (component) {
        return "gradingUpdate" + component.props.item.id;
    },

    handleUpdate: function (component, event) {
        console.log('Handling grading update');
        if (component.handleUpdate) {
            component.handleUpdate(event)
        }
        else {
            component.setState({data: event.detail.data});
        }
    }
};


var StatusUpdateDispatcher = {
    onStatusUpdate: function() {
        return onStatusUpdate.onUpdate(this);
    },

    reportStatusUpdate: function (status) {
        console.log("StatusUpdate dispatching message");
        window.dispatchEvent(
            new CustomEvent(this.onStatusUpdate(),
                {
                    detail: {
                        item: this.props.item,
                        status: status
                    }
                }
            )
        );
        this.notifySocket(status)
    },

    notifySocket: function (status) {
        console.log("StatusUpdate notified socket");
        socket.emit('statusUpdate',
            {
                item: this.props.item,
                status: status,
                userhash: userhash
            });
    }
};

var GradingUpdateDispatcher = {
    onGradingUpdate: function() {
        return onGradingUpdate.onUpdate(this);
    },

    reportGradingUpdate: function (data) {
        console.log("GradingUpdate dispatching message");
        window.dispatchEvent(
            new CustomEvent(this.onGradingUpdate(),
                {
                    detail: {
                        data: data
                    }
                }
            )
        );
    }
};



var Problem = {
    isProblemAttempted: function (problem) {
        var pType = problem.problem_type;
        var pID = problem.pk;
        return (data.scores.hasOwnProperty(pType) &&
            data.scores[pType].hasOwnProperty(pID)
            );
    },

    isProblemCompleted: function (problem) {
        var pType = problem.problem_type;
        var pID = problem.pk;
        return (data.scores.hasOwnProperty(pType) &&
            data.scores[pType].hasOwnProperty(pID) &&
            data.scores[pType][pID] == problem.max_score
            );
    }
};

var ProblemStatusIndicator = React.createClass({
    mixins: [Listener, Problem],

        listenTo: [onStatusUpdate],

    getInitialState: function () {
        return {
            attempted: this.isProblemAttempted(this.props.item),
            completed: this.isProblemCompleted(this.props.item)
        };
    },

    getItemStatusRepresentation: function (problem) {
        var repr = problem.name;
        if (!this.state.attempted) {
            repr += ": not attempted";
        }
        else {
            repr += !this.state.completed ? " : attempted" : " : completed";
        }
        return repr;

    },

    render: function () {
        // TODO: remove bootstrap classes
        var problemClasses = React.addons.classSet({
            "glyphicon": true,
            "glyphicon-check": this.state.completed,
            "glyphicon-edit": !this.state.completed,
            "problem-idle": !this.state.attempted,
            "problem-attempted": this.state.attempted && !this.state.completed,
            "problem-complete": this.state.completed
        });

        return(
            <span className={problemClasses}
            title={this.getItemStatusRepresentation(this.props.item)}>
            </span>
            );
    }
});

var Video = {
    shouldComponentUpdate: function (nextProps, nextState) {
        console.log('Is update needed?');
        console.log(this.state.completed !== nextState.completed);
        return (this.state.completed !== nextState.completed);
    },

    getInitialState: function () {
        return {
            completed: data.watched.hasOwnProperty(this.props.item.id)
        };
    },

    getItemStatusRepresentation: function () {
        return this.props.name +
            this.state.completed ? " : watched" : " : unwatched ";
    }
};


var VideoStatusIndicator = React.createClass({
    mixins: [Listener, Video],

        listenTo: [onStatusUpdate],

    render: function () {
        console.log('VideoStatusIndicator');

        // TODO: remove bootstrap classes
        var problemClasses = React.addons.classSet({
            "glyphicon": true,
            "glyphicon-film": true,
            "ok-icon-green": this.state.completed
        });

        return(
            <span className={problemClasses}
            title={this.getItemStatusRepresentation()}>
            </span>
            );
    }
});