function RSubmissionWrapper(name) {
		SubmissionWrapper.call(this, name);
		this.language = "r";
		this.language_version = "3.3.2";
		this.tcm = null;
}
RSubmissionWrapper.prototype = Object.create(SubmissionWrapper.prototype);
RSubmissionWrapper.prototype.constructor = RSubmissionWrapper;

/**
 * @override
 */
RSubmissionWrapper.prototype.getAllCode = function() {
		var hash = CryptoJS.SHA1(this.problemId);
		return this.tcm.getHashedCode(hash);
}

/**
 * @override
 */
RSubmissionWrapper.prototype.createCodeMirrors = function() {
 		this.tcm = this.createSubmissionMirror();
 }

RSubmissionWrapper.prototype.renderGraph = function(graph, sol) {
		imurl = root+'/problems/'+this.language+'/graph/'+graph;
		if (sol){
				$('#sol-graph').replaceWith('<div id="sol-graph"> \
						<h3 style="text-align: center;">Our Graph</h3>\
						<img alt ="Our graph" src="' + imurl + '" class="img-responsive"></div>');
		} else{
				$('#user-graph').replaceWith('<div id="user-graph"> \
						<h3 style="text-align: center;">Your Graph</h3> \
						<img alt ="Your graph" src="' + imurl + '" class="img-responsive"></div>');
		}
}

 /**
  * @override
  */
RSubmissionWrapper.prototype.getTestcases = function(code) {
		var call_path = "";
    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' +
            this.wrapperDivId.split("-")[1]+ '/run';
    }

    var postParams = { csrftoken: csrftoken, submission: code };

    // Activate loading pop-up
    $('#waitingModal').modal('show');

    var that = this;
    $.post(call_path,
            postParams,
            function(data) {
            	var res = data["results"][0];
							if ("test_val" in res){
								$('#user-output').replaceWith('<div id="user-output" class="well"> \
										<h3 style="text-align: center;">Your Output</h3><p>' + res["test_val"].replace('\n', '<br>') + '</p></div>');
							}
							if ("sol_val" in res){
								$('#sol-output').replaceWith('<div id="sol-output" class="well"> \
										<h3 style="text-align: center;">Our Output</h3><p>' + res["sol_val"].replace('\n', '<br>') + '</p></div>');
							}
            	if ("graphics" in res && res["graphics"] != null) {
            		that.renderGraph(res["graphics"], false);
            	}
							if ("sol_graphics" in res && res["sol_graphics"] != null) {
            		that.renderGraph(res["sol_graphics"], true);
            	}
              that._getTestcasesCallback(data);
              // Deactivate loading pop-up
              $('#waitingModal').modal('hide');
            },
        "json")
     .fail(
        function(jqXHR, textStatus, errorThrown) {
            // Deactivate loading pop-up
            $('#waitingModal').modal('hide');
        });
}
