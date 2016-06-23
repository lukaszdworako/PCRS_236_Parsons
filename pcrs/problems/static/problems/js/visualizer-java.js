function executeJavaVisualizer(option, data) {
    switch(option) {
        case "create_visualizer":
            console.log(data);
            break;

        case "gen_execution_trace_params":
            console.log(data);
            getExecutionTraceParams(data);
            break;

        case "render_data":
            console.log(data);
            break;

        default:
            return "option not supported";
    }

    /**
     * Update dictionary initPostParams with additional parameters
     * that will be used to create a visualizer.
     */
    function getExecutionTraceParams(initPostParams) {
        initPostParams.add_params = JSON.stringify({
        });
    }
}

