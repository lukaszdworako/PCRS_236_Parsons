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

RSubmissionWrapper.prototype.renderGraph = function(graph) {
	imurl = root+'/problems/'+this.language+'/graph/'+graph;
	console.log(imurl);
	window.open(imurl, "R Graph", "width=500,height=500,resizable,scrollbars=yes");
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
            	if ("graphics" in res) {
            		var graph = res["graphics"];
            		that.renderGraph(graph);
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