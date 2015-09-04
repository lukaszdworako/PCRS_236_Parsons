/** @jsx React.DOM */



var Listener = {
    componentDidMount: function () {
        var component = this;
        component.listenTo.forEach(function (listener) {
            window.addEventListener(listener.onUpdate(component),
                function (event) {
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
        if (component.handleUpdate) {
            component.handleUpdate(event)
        }
        component.setState(event.detail.status);
    }
};

var onGradingUpdate = {
    onUpdate: function (component) {
        return "gradingUpdate" + component.props.item.id;
    },

    handleUpdate: function (component, event) {
        if (component.handleUpdate) {
            component.handleUpdate(event)
        }
        else {
            component.setState({data: event.detail.data});
        }
    }
};

var onVisibilityUpdate = {
    onUpdate: function (component) {
        return "itemUpdate" + component.props.item.id;
    },

    handleUpdate: function (component, event) {
        component.handleUpdate(event)
    }
};


var StatusUpdateDispatcher = {
    onStatusUpdate: function() {
        return onStatusUpdate.onUpdate(this);
    },

    reportStatusUpdate: function (status) {
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



var ProblemMixin = {
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

var ProblemStatusIndicator = React.createClass({displayName: 'ProblemStatusIndicator',
    mixins: [Listener, ProblemMixin],
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

    shouldComponentUpdate: function (nextProps, nextState) {
        return ((this.state.attempted !== nextState.attempted ||
                (this.state.completed !== nextState.completed)
            ));
    },

    componentDidUpdate: function() {
        if (this.props.problemDidUpdate)
            this.props.problemDidUpdate(this.state.completed);
    },


    render: function () {
        var problemClasses = React.addons.classSet({
            "problem-not-attempted": !this.state.attempted,
            "problem-attempted": this.state.attempted && !this.state.completed,
            "problem-completed": this.state.completed
        });

        return(
            React.DOM.span({className: problemClasses, 
            title: this.getItemStatusRepresentation(this.props.item)}
            )
            );
    }
});

var Video = {
    shouldComponentUpdate: function (nextProps, nextState) {
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
    },

    handleUpdate: function(event) {
         this.setState(event.detail.status);

    }

};


var VideoStatusIndicator = React.createClass({displayName: 'VideoStatusIndicator',
    mixins: [Listener, Video],
    listenTo: [onStatusUpdate],

    render: function () {
        var problemClasses = React.addons.classSet({
            "video-watched": this.state.completed,
            "video-not-watched": !this.state.completed
        });

        return(
            React.DOM.span({className: problemClasses, 
            title: this.getItemStatusRepresentation()}
            )
            );
    },

    componentDidUpdate: function(prevProps, prevState) {
        if (prevProps.hasOwnProperty('videoDidUpdate'))
            prevProps.videoDidUpdate();
    }
});

var SubmitButton = React.createClass({displayName: 'SubmitButton',
    render: function () {
        return (React.DOM.button({ref: "submitButton", className: "green-button", 
                        onClick: this.props.onClick}, "Submit"));
    }}
);