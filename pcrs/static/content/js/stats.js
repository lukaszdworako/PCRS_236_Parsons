function createAttemptsGraph(data) {
    var canvas = document.getElementById('attempts-graph');
    var ctx1 = canvas.getContext("2d");
    ctx1.clearRect(0, 0, canvas.width, canvas.height);

    var graph = new RGraph.Bar('attempts-graph', data);
    graph.Set('chart.gutter.bottom', 50);
    graph.Set('chart.gutter.right', 200);
    graph.Set('chart.key', ['Did not attempt', 'Attempted', 'Completed']);
    graph.Set('chart.key.position.x', 200);
    graph.Set('chart.labels.above', true);
    graph.Set('chart.background.grid', false);
    graph.Set('chart.colors', ['#E31837', '#008BB0' , '#3C9A45']);
    graph.Draw();
    $('<a/>',{
        class:"at",
        href:'',
        text:data[0][0] + " students did not attempt the problem, " +
             data[0][1] + " student attempted the problem, " +
             data[0][2] + " completed the problem"
    }).appendTo('.col-md-offset-1');

}

$(function () {
    $('#generate_graph').click(function() {
        var active_only = $('#active_only').is(':checked');
        var post_data = {};
        if (active_only) {
            post_data = {'active_only': active_only};
        }
        $.post(document.URL + '/data', post_data, function (data) {
            // on success
            createAttemptsGraph([data['results']]);
        });
    })
});