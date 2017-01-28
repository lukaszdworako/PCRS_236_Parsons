var interval;

$(function () {
    $('#button-id-go').click(function () {
        var firstIter = true;
        update(firstIter);
        if (!$('#id_final').is(':checked')) {
            // poll for new data every 2 seconds
            interval = setInterval(update, 2000);
        }
    });
});

function update(firstIter=false) {
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
                createSubmissionGraph([data['submissions']], firstIter);
            }
            if (data['data'].length > 0) {
                createSubmissionDetailsGraph(data['data'], firstIter);
            }
            firstIter = false;
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

function createSubmissionGraph(data, firstIter=false) {
    // Create the submission data graph for live monitoring
    var graph = new RGraph.Bar('submissions-graph', data);
    graph.Set('chart.labels', ['Correct', 'Incorrect']);
    graph.Set('chart.title', "Overall Performance");
    graph.Set('chart.labels.above', true);
    graph.Set('chart.background.grid', false);
    graph.Set('chart.colors', ['rgba(0,128,0,0.85)', 'rgba(128,0,0,0.85)']);
    if (firstIter) {
        RGraph.Effects.Bar.Grow(graph);
    } else {
        graph.Draw();
    }
}

function createSubmissionDetailsGraph(data, firstIter=false) {
    var canvas = $("#details-graph");
    // set width of graph depending on the number of items that will be displayed
    var graph = new RGraph.HBar('details-graph', data);
    graph.Set('chart.title', "Performance Per Testcase/Option");
    graph.Set('chart.labels', Array.from(new Array(data.length), (val,index)=>"#"+(index+1)));
    graph.Set('chart.background.grid', false);
    graph.Set('chart.labels.above', true);
    graph.Set('chart.colors', ['rgba(0,128,0,0.45)', 'rgba(128,0,0,0.45)']);
    if (firstIter) {
        RGraph.Effects.Bar.Grow(graph);
    } else {
        graph.Draw();
    }
}