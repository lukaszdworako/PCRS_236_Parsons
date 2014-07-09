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
}

$(function () {
    $.get(document.URL + '/data').success(function (data) {
        createAttemptsGraph([data['results']])
    });
});