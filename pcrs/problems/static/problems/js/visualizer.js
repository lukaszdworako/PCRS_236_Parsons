/**
 * Generic Visualizer, that is used by all languages.
 * To plug in a language, create a corresponing function. Function must support
 * required options, regardless of existence of visualizer for the language.
 * If a visualizer exists, function must support all options, and language has to be
 * added to supportedVisualization array.
 *
 *                          Usage options:
 *
 * "create_visualizer": creates visualizer of required language
 *     data: format depends on the language.
 *
 * "gen_execution_trace_params": update dictionary with additional parameters required
 *  to generate execution trace. Make sure to JSON.stringify add_params.
 *     data: {language : language, user_script : code}
 *     updated data: {language : language, user_script : code, add_params : {}}
 *
 * "render_data" (required): render code string and populate
 *  corresponding cell in grading table
 *     data: {codeStr : encodedResult, targetElement : $('#tcase_ td.testOutputCell')}
 *
 */

function executeGenericVisualizer(option, data, newCode) {
    var supportedVisualization = ['python', 'c'];

    if (visualizationSupported()){
        if (language == 'python') {
            return executePythonVisualizer(option, data);
        }
        else if (language == 'c') {
            return executeCVisualizer(option, data, newCode);
        }
    }else{
        alert("No support for visualization available!");
        return null;
    }

    function visualizationSupported() {
    /**
     * Return boolean true if global language is in the array supportedVisualization;
     * false otherwise.
     */
        return $.inArray(language, supportedVisualization) > -1;
    }
}

function removeHashkeyForDisplay(div_id, newCode){
    /**
     * Generate a Hashkey based on
     * the problem_id to identify
     * where the student code starts and ends
     */
    var codeArray = newCode.split('\n');
    var line_count = codeArray.length;
    var hash_code = CryptoJS.SHA1(div_id.split("-")[1]);
    var code = "";
    var i;
    for (i = 0; i < line_count; i++){
        //wrapClass = newCode.lineInfo(i).wrapClass;
        if (codeArray[i] == hash_code) {
            continue;
        }
        else {
            code += codeArray[i];
            //Check for the main function declaration, this is the line we should start
            //student steps from, if it is not hidden
        }
        code += '\n';
    }
    return code.substring(0, code.length-1);
}
