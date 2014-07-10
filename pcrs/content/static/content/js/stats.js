function createAttemptsGraph(data) {
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
    $.get(document.URL + '/data').success(function (data) {
        createAttemptsGraph([data['results']])
    });
});