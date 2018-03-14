var MAX_FILE_SIZE = 100000

function generateExportButton(subPk, problemId) {
    call_path = root + '/problems/r/' + subPk + '/export';
    if (!$('#export-link-' + problemId).length) {
        $('#output-' + problemId).append('<a type="button" id="export-link-' + problemId + '" href="' + call_path + '" class="green-button">Export Submission</a>');
    } else {
        $('#export-link-' + problemId).remove();
        $('#output-' + problemId).append('<a type="button" id="export-link-' + problemId + '" href="' + call_path + '" class="green-button">Export Submission</a>');
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

RSubmissionWrapper.prototype.renderGraph = function(graph, sol, problemId) {
    imurl = root + '/problems/' + this.language + '/graph/' + graph;
    if (sol) {
        $('#sol-graph-' + problemId).replaceWith('<div id="sol-graph-' + problemId +'"> \
						<h3 style="text-align: center;">Our Graph</h3>\
						<img alt ="Our graph" src="' + imurl + '" class="img-responsive"></div>');
    } else {
        $('#user-graph-' + problemId).replaceWith('<div id="user-graph-' + problemId + '"> \
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
	var problemId = this.problemId;

    // Retrieves file if exists, returns undefined if non-existant
    try {
        var uploadedFile = $('input[name*="file_upload"]').prop('files')[0];
    } catch (err) {
        uploadedFile = null;
    }
    // Build URLs for running test and uploading file
    var call_path = '';
    if (this.isEditor) {
        call_path = root + '/problems/' + this.language + '/editor/run';
    } else {
        call_path = root + '/problems/' + this.language + '/' +
            this.wrapperDivId.split("-")[1] + '/run';
    }
    var fileCallPath = root + '/problems/' + this.language + '/' + this.problemId + '/upload';

    // Upload the file to the db before running tests
    if (uploadedFile != undefined && uploadedFile.size <= MAX_FILE_SIZE && uploadedFile.type == 'text/csv') {
        $.ajax({
                url: fileCallPath,
                type: 'POST',
                data: uploadedFile,
                processData: false
            })
            .done(function(id, problemId) {
                postParams = {
                    csrftoken: csrftoken,
                    submission: code,
                    file_id: id
                }
                // Run the submission now
                $.post(call_path,
                        postParams,
                        function(data, problemId) {
                            var res = data['results'][0];
                            if ('test_val' in res) {
                                $('#user-output-' + problemId).replaceWith('<div id="user-output-' + problemId + '" class="well"> \
														<h3 style="text-align: center;">Your Output</h3><p>' + res["test_val"].replace(/\n/g, '<br>') + '</p></div>');
                            }
                            if ('sol_val' in res) {
                                $('#sol-output-' + problemId).replaceWith('<div id="sol-output-' + problemId + '" class="well"> \
														<h3 style="text-align: center;">Our Output</h3><p>' + res["sol_val"].replace(/\n/g, '<br>') + '</p></div>');
                            }
                            if ('graphics' in res && res['graphics'] != null) {
                                that.renderGraph(res['graphics'], false, problemId);
                            }
                            if ('sol_graphics' in res && res['sol_graphics'] != null) {
                                that.renderGraph(res['sol_graphics'], true, problemId);
                            }
                            generateExportButton(data['sub_pk'], problemId)
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
            .error(function(jqXHR, textStatus, errorThrown) {
                $('#waitingModal').modal('hide');
            });
    } else {
        // Run submission without file
        postParams = {
            csrftoken: csrftoken,
            submission: code
        }
        $.post(call_path,
                postParams,
                function(data) {
                    var res = data["results"][0];
                    if ("test_val" in res) {
                        $('#user-output-' + problemId).replaceWith('<div id="user-output-' + problemId + '" class="well"> \
												<h3 style="text-align: center;">Your Output</h3><p>' + res["test_val"].replace(/\n/g, '<br>') + '</p></div>');
                    }
                    if ("sol_val" in res) {
                        $('#sol-output-' + problemId).replaceWith('<div id="sol-output-' + problemId + '" class="well"> \
												<h3 style="text-align: center;">Our Output</h3><p>' + res["sol_val"].replace(/\n/g, '<br>') + '</p></div>');
                    }
                    if ("graphics" in res && res["graphics"] != null) {
                        that.renderGraph(res["graphics"], false, problemId);
                    }
                    if ("sol_graphics" in res && res["sol_graphics"] != null) {
                        that.renderGraph(res["sol_graphics"], true, problemId);
                    }
                    generateExportButton(data["sub_pk"], problemId)
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
$(document).ready(function() {
    // Check whether there is a file for each file upload element
    $('.file_upload').each(function(i, obj) {
        var probPk = obj.id;
        var url = root + "/problems/r/" + probPk + "/uploadexist";
        if (probPk != undefined && probPk > 0) {
            $.post(url, function(data) {
                if (data.success == true) {
                    htmlString = `<div id="file_existance+` + probPk + `" class="alert well">
							<p><input type="button" id="delete_file+` + probPk + `" class="btn btn-danger pull-right"
							value="Delete Data Set" onclick="deleteThis('`+ uploadPath + `', this)">
							</input>File Name: ` + data.name + "<br>First 150 Characters:<br>" +
                        data.substring.replace(/\n/g, '<br>').substr(0, 150) + `</p></div>`;
                    $(obj).after(htmlString);
                }
            })
        }

        // Build request URL
        var problemPath = window.location.href;
        var index = problemPath.indexOf("/problems/");
        if (index != -1) {
            var submitIndex = problemPath.indexOf("/submit");
            problemPath = problemPath.substring(index, submitIndex);
            var uploadPath = root + problemPath + '/upload';
        } else {
            var uploadPath = root + '/problems/r/' + probPk + '/upload';
        }
        $(obj).change(function() {
            var uploadedFile = $(obj).prop('files')[0];

            if (uploadedFile != undefined) {
                validFile = true;

                // Check validity of file
                if (uploadedFile.size > MAX_FILE_SIZE) {
                    alert("File upload rejected, file is too big. Max size: " + MAX_FILE_SIZE);
                    validFile = false;
                }
                //if (uploadedFile.type != "text/csv") {
                //    alert("File upload rejected, file is not csv");
                //    validFile = false;
                //}

                // Upload file
                if (validFile) {
                    // Prepared data
                    var textData;
                    fr = new FileReader();

                    // File read is an async call, so must nest here
                    fr.onload = function(e) {
                        textData = fr.result;
                        fileName = uploadedFile.name;
                        dataDict = {
                            "data": textData,
                            "name": fileName
                        }

                        $.post(
                                uploadPath,
                                dataDict
                            )
                            .done(function(data) {
                                alert("Data set uploaded");
                                htmlString = `<div id="file_existance+` + probPk + `" class="alert well">
										<p><input type="button" id="delete_file+` + probPk + `" class="btn btn-danger pull-right"
										value="Delete Data Set" onclick="deleteThis('`+ uploadPath + `', this)">
										</input>File Name: ` + fileName + "<br>First 150 Characters:<br>" +
                                    textData.replace(/\n/g, '<br>').substr(0, 150) + `</p></div>`;

                                if ($('#file_existance+' + probPk).length) {
                                    $('#file_existance+' + probPk).replaceWith(htmlString);
                                } else {
                                    $(obj).after(htmlString);
                                }
                            })
                            .error(function(jqXHR, textStatus, errorThrown) {
                                alert("Error uploading file.");
                            });
                    }

                    // Async call here
                    fr.readAsText(uploadedFile);
                }
            }
        });
    });
});

function deleteThis(uploadPath, ele){
	$.ajax({
		url: uploadPath,
		type: "GET"
	})
	.done(function(data){
		if(data == "Success"){
			ele.parentElement.parentElement.remove()
		}
		else{
			alert('Error deleting file.');
		}
	})
	.error(function(jqXHR, textStatus, errorThrown){
		alert('Error deleting file.');
	});
}

Element.prototype.remove = function() {
    this.parentElement.removeChild(this);
}
NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
    for(var i = this.length - 1; i >= 0; i--) {
        if(this[i] && this[i].parentElement) {
            this[i].parentElement.removeChild(this[i]);
        }
    }
}
