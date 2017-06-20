var MAX_FILE_SIZE = 100000

function generateExportButton(subPk){
		call_path = root + '/problems/r/' + subPk + '/export';
		if (!$('#export-link').length){
				$('#output').after('<a id="export-link" href="' + call_path + '" class="green-button pull-right">Export Submission</a>');
		}
		else {
				$('#export-link').replaceWith('<a id="export-link" href="' + call_path + '" class="green-button pull-right">Export Submission</a>');
		}
}

function RSubmissionWrapper(name) {
		SubmissionWrapper.call(this, name);
		this.language = 'r';
		this.language_version = '3.3.2';
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
		// Activate loading pop-up
		$('#waitingModal').modal('show');

		var that = this;
		var postParams;

		// Retrieves file if exists, returns undefined if non-existant
		try{
				var uploadedFile = $('input[name*="file_upload"]').prop('files')[0];
		} catch (err){
				uploadedFile = null;
		}
		// Build URLs for running test and uploading file
    var call_path = '';
    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' +
            this.wrapperDivId.split("-")[1]+ '/run';
    }
		var fileCallPath = root + '/problems/' + this.language + '/' + this.problemId + '/upload';

		// Upload the file to the db before running tests
		if(uploadedFile != undefined && uploadedFile.size <= MAX_FILE_SIZE && uploadedFile.type == 'text/csv'){
				$.ajax({
						url: fileCallPath,
						type: 'POST',
						data: uploadedFile,
						processData: false
				})
				.done(function(id){
						postParams = {csrftoken: csrftoken, submission: code, file_id: id}
						// Run the submission now
				    $.post(call_path,
								postParams,
            		function(data) {
			            	var res = data['results'][0];
										if ('test_val' in res){
												$('#user-output').replaceWith('<div id="user-output" class="well"> \
														<h3 style="text-align: center;">Your Output</h3><p>' + res["test_val"].replace(/\n/g, '<br>') + '</p></div>');
										}
										if ('sol_val' in res){
												$('#sol-output').replaceWith('<div id="sol-output" class="well"> \
														<h3 style="text-align: center;">Our Output</h3><p>' + res["sol_val"].replace(/\n/g, '<br>') + '</p></div>');
										}
			            	if ('graphics' in res && res['graphics'] != null) {
			            			that.renderGraph(res['graphics'], false);
			            	}
										if ('sol_graphics' in res && res['sol_graphics'] != null) {
			            			that.renderGraph(res['sol_graphics'], true);
			            	}
										generateExportButton(data['sub_pk'])
			              that._getTestcasesCallback(data);
			              // Deactivate loading pop-up
			              $('#waitingModal').modal('hide');
			          },
        				'json')
     				.fail(function(jqXHR, textStatus, errorThrown) {
								// Deactivate loading pop-up
            		$('#waitingModal').modal('hide');
        		});
				})
				.error(function(jqXHR, textStatus, errorThrown){
						$('#waitingModal').modal('hide');
				});
		} else{
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
								generateExportButton(data["sub_pk"])
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

// Adds an event listener to file input allowing for ajax file uploads
$( document ).ready(function(){
    // Build request URL
    var problemPath = window.location.href;
    var index = problemPath.indexOf("/problems/");
		var submitIndex = problemPath.indexOf("/submit");
    problemPath = problemPath.substring(index, submitIndex);
		var uploadPath = root + problemPath + '/upload';

    $('#file_upload').change(function(){
        var uploadedFile = $("#file_upload").prop('files')[0];
        var probPk = $('#file_upload').attr('name');

    		if(uploadedFile != undefined){
						validFile = true;

						// Check validity of file
						if (uploadedFile.size > MAX_FILE_SIZE){
								alert("File upload rejected, file is too big. Max size: " + MAX_FILE_SIZE);
								validFile = false;
						}
						if (uploadedFile.type != "text/csv"){
								alert("File upload rejected, file is not csv");
								validFile = false;
						}

						// Upload file
						if(validFile){
								// Prepared data
								var textData;
								fr = new FileReader();

								// File read is an async call, so must nest here
								fr.onload = function(e){
										textData = fr.result;
										fileName = uploadedFile.name;
										dataDict = {"data": textData, "name": fileName}

										$.post(
												uploadPath,
												dataDict
				    				)
				            .done(function(data){
				                alert("Data set uploaded");
												htmlString = `<div id="file_existance" class="alert well">
														<p><input type="button" id="delete_file" class="btn btn-danger pull-right"
														value="Delete Data Set"></input>File Name: ` + fileName + "<br>First 150 Characters:<br>"
														+ textData.replace(/\n/g, '<br>').substr(0, 150) + `</p></div>`;

												if($('#file_existance').length){
														$('#file_existance').replaceWith(htmlString);
												}
												else{
														$('#file_upload').after(htmlString);
												}
				                setDeleteButton(uploadPath);
				            })
				            .error(function(jqXHR, textStatus, errorThrown){
				                alert("Error uploading file.");
				            });
								}

								// Async call here
								fr.readAsText(uploadedFile);
						}
        }
    });
    setDeleteButton(uploadPath);
});

function setDeleteButton(uploadPath){
    $('#delete_file').click(function(){
        // Assumes that there is an existing file
        $.ajax({
            url: uploadPath,
            type: "GET"
        })
        .done(function(data){
            if(data == "Success"){
								$('#delete_file').remove();
                $('#file_existance').remove();
            }
            else{
                alert('Error deleting file.');
            }
        })
        .error(function(jqXHR, textStatus, errorThrown){
            alert('Error deleting file.');
        });
    });
}
