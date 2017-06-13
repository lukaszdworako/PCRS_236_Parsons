var MAX_FILE_SIZE = 100000

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

/**
 * @override
 */
RSubmissionWrapper.prototype.getTestcases = function(code) {
		// Activate loading pop-up
		$('#waitingModal').modal('show');

		var that = this;
		var postParams;

		// Retrieves file if exists, returns undefined if non-existant
		try{
				var uploadedFile = $("input[name*='file_upload']").prop('files')[0];
		} catch (err){
				uploadedFile = null;
		}
		// Build URLs for running test and uploading file
    var call_path = "";
    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' +
            this.wrapperDivId.split("-")[1]+ '/run';
    }
		var fileCallPath = root + '/problems/' + this.language + '/' + this.problemId + '/upload';

		// Upload the file to the db before running tests
		if(uploadedFile != undefined && uploadedFile.size <= MAX_FILE_SIZE && uploadedFile.type == "text/csv"){
				$.ajax({
						url: fileCallPath,
						type: "POST",
						data: uploadedFile,
						processData: false
				})
				.done(function(id){
						postParams = {csrftoken: csrftoken, submission: code, file_id: id}
						// Run the submission now
				    $.post(call_path,
								postParams,
            		function(data) {
			            	var res = data["results"][0];
										if ("test_val" in res){
												$('#user-output').replaceWith('<div id="user-output" class="well"> \
														<h3 style="text-align: center;">Your Output</h3><p>' + res["test_val"].replace(/\n/g, '<br>') + '</p></div>');
										}
										if ("sol_val" in res){
												$('#sol-output').replaceWith('<div id="sol-output" class="well"> \
														<h3 style="text-align: center;">Our Output</h3><p>' + res["sol_val"].replace(/\n/g, '<br>') + '</p></div>');
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
     				.fail(function(jqXHR, textStatus, errorThrown) {
								// Deactivate loading pop-up
            		$('#waitingModal').modal('hide');
        		});
				})
				.error(function(jqXHR, textStatus, errorThrown){
						$('#waitingModal').modal('hide');
				});
		} else{
				if (uploadedFile.size > MAX_FILE_SIZE){
						alert("File upload rejected, file is too big. Max size: " + MAX_FILE_SIZE);
				}
				if (uploadedFile.type != "text/csv"){
						alert("File upload rejected, file is not csv");
				}

				// Run submission without file
				postParams = {csrftoken: csrftoken, submission: code}
		    $.post(call_path,
						postParams,
						function(data) {
								var res = data["results"][0];
								if ("test_val" in res){
										$('#user-output').replaceWith('<div id="user-output" class="well"> \
												<h3 style="text-align: center;">Your Output</h3><p>' + res["test_val"].replace(/\n/g, '<br>') + '</p></div>');
								}
								if ("sol_val" in res){
										$('#sol-output').replaceWith('<div id="sol-output" class="well"> \
												<h3 style="text-align: center;">Our Output</h3><p>' + res["sol_val"].replace(/\n/g, '<br>') + '</p></div>');
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
				.fail(function(jqXHR, textStatus, errorThrown) {
						// Deactivate loading pop-up
						$('#waitingModal').modal('hide');
				});
		}
}
