/** @jsx React.DOM */

var problems = [];


socket.on('problems', function (data) {
    console.log(data);
    problems.push(data);
    renderProblemList();
});

var ProblemList = React.createClass({

    componentDidMount: function () {
        $.ajax({
            url: '/content/inclass/list',
            dataType: 'json',
            success: function (data) {
                console.log(data);
                problems = data;
                this.setState({data: problems});

            }.bind(this)
        });
    },

    render: function () {
        var problemNodes = problems.map(function (problem) {
            return (
                <Problem name={problem.name} url={problem.url}>
                    {problem.url}
                </Problem>
                );
        });
        return (
            <div className="ProblemList">
                   {problemNodes}
            </div>
            );
    }
});


var Problem = React.createClass({
    render: function () {
        return (
            <div className="problem">
                <a href={this.props.url}>{this.props.name}</a>
            </div>
            );
    }
});

function renderProblemList() {
    React.renderComponent(
        <ProblemList  />,
        document.getElementById("problemList")
    );
}
renderProblemList();