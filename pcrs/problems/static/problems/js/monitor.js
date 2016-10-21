var interval;

$(function () {
    $('#button-id-go').click(function () {
        update();
        if (!$('#id_final').is(':checked')) {
            // poll for new data every 2 seconds
            interval = setInterval(update, 2000);
        }
    });
});

function update() {
    // get the most recent data from db for this problem after this time

    // If only first submissions are requested for analysis,
    // firstSubmissionsOnly is true.
    if ($('#id_firstSubmissionsOnly').is(':checked')) {
        firstSubmissionsOnly = true;
    } else {
        firstSubmissionsOnly = false;
    }
    $.post(document.URL + '_data',
        {
            time: $("#id_time").val(),
            section: $("#id_section").val(),
            firstSubmissionsOnly: firstSubmissionsOnly
        }
    ).success(function (data) {
            // update the graphs
            clearCanvases();
            if (data['submissions'].length > 0) {
                createSubmissionGraph([data['submissions']]);
            }
            if (data['data'].length > 0) {
                createSubmissionDetailsGraph(data['data']);
            }
        });
}


function clearCanvases() {
    var canvas = document.getElementById('submissions-graph');
    var ctx1 = canvas.getContext("2d");
    ctx1.clearRect(0, 0, canvas.width, canvas.height);
    canvas = document.getElementById('details-graph');
    var ctx2 = canvas.getContext("2d");
    ctx2.clearRect(0, 0, canvas.width, canvas.height);
}

function createSubmissionGraph(data) {
    // Create the submission data graph for live monitoring
    var graph = new RGraph.Bar('submissions-graph', data);
    graph.Set('chart.labels', ['Correct', 'Incorrect']);
    graph.Set('chart.labels.above', true);
    graph.Set('chart.background.grid', false);
    graph.Set('chart.colors', ['#3C9A45', '#E31837']);
    graph.Draw();
}

function createSubmissionDetailsGraph(data) {
    var canvas = $("#details-graph");
    // set width of graph depending on the number of items that will be displayed
    canvas.attr("width", data.length * 150);
    var graph = new RGraph.Bar('details-graph', data);
    graph.Set('chart.background.grid', false);
    graph.Set('chart.labels.above', true);
    graph.Set('chart.colors', ['#3C9A45', '#E31837']);
    graph.Draw();
}