var MAX_FILE_SIZE = 100000

function ProblemFormHandler($form) {
    this.$form = $form;
}

/**
 * Should be called once the page loads.
 */
ProblemFormHandler.prototype.pageLoad = function() {
    this._setUpMultipleSelectFields();
}

// Make the tags section nice 'n' fancy
ProblemFormHandler.prototype._setUpMultipleSelectFields = function() {
    var that = this;

    $('#div_id_tags label').append(
        $('<a type="button"></a>')
            .attr('title', 'Test Suite Help')
            .attr('class', 'label-icon-button')
            .click(function() {
                that._showAddTagDialog();
            })
            .append('<i class="plus-sign-icon"></i>'));

    var searchBoxHtml = '<input type="text"' +
        'class="textInput textinput form-control" placeholder="Search" />';

    this.$form.find('.select-multiple-field').multiSelect({
        selectableHeader: searchBoxHtml,
        selectionHeader: '<h5>Selected</h5>',
        afterInit: function(ms) {
            var that = this;
            var $selectableSearch = that.$selectableUl.prev();
            var selectableSearchString = '#' + that.$container.attr('id') +
                ' .ms-elem-selectable:not(.ms-selected)';

            that.qs = $selectableSearch.quicksearch(selectableSearchString)
                .on('keydown', function(e) {
                    var isDownArrowOrTab = e.which === 40 || e.which == 9;
                    if (isDownArrowOrTab) {
                        that.$selectableUl.focus();
                        return false;
                    }
                });
        },
        afterSelect: function() {
            this.qs.cache();
        },
        afterDeselect: function() {
            this.qs.cache();
        },
    });
}

ProblemFormHandler.prototype._showAddTagDialog = function() {
    var that = this;
    AlertModal.prompt('Create New Tag', function(value) {
        if (value) {
            that.createProblemTag(value);
        }
    });
}

ProblemFormHandler.prototype.createProblemTag = function(name) {
    var $selectMultipleField = this.$form.find('.select-multiple-field');
    $.ajax({
        // The 'root' variable is a global defined in base.html
        url:    root + "/content/tags/create",
        method: "POST",
        data: {
            'name': name,
        },
        dataType: 'json',
    }).success(function(data) {
        if ('validation_error' in data) {
            AlertModal.alert(
                'Tag Format Error',
                data['validation_error']['name']);
            return;
        }

        $selectMultipleField.multiSelect('addOption', {
            value: data['pk'],
            text: data['name'],
            index: 0,
        });
    });
}

/**
 * Override this if you want to call a custom ProblemFormHandler.
 *
 * This function exists so it can be overridden by various PCRS versions.
 */
var problemFormPageLoadCallback = function() {
    new ProblemFormHandler($('form')).pageLoad();
}

$(function() {
    problemFormPageLoadCallback();
});

/**
 * A callback for HTML generated in form.py.
 */
function showClearSubmissionsDialog(clearUrl) {
    AlertModal
        .clear()
        .setTitle('Clear submissions to this problem?')
        .setBody('All submissions to this problem will be removed.')
        .addFooterElement($('<button></button>')
            .attr('class', 'btn btn-danger pull-left')
            .attr('type', 'button')
            .text('Clear')
            .click(function() {
                clearSubmissionsForCurrentProblem(clearUrl);
            }))
        .addCancelButtonToFooter('right')
        .show();
}

function clearSubmissionsForCurrentProblem(clearUrl) {
    $.ajax({
        url:    clearUrl,
        method: "POST",
    }).success(function(data) {
        // Clear errors on the page.
        $('.has-error').removeClass('has-error');
        // Remove error help blocks
        var helpBlocks = $('.help-block');
        for (var i = 0; i < helpBlocks.length; i++) {
            var block = $(helpBlocks[i]);
            if (block.attr('id').indexOf('error') > -1) {
                block.remove();
            }
        }
        AlertModal.hide();
    });
}

// Adds an event listener to file input allowing for ajax file uploads.
$( document ).ready(function(){
    // Build request URL
    var problemPath = window.location.href;
    var index = problemPath.indexOf("/problems/");
    var isCreate = problemPath.indexOf("create");

    if(isCreate != -1){
        problemPath = problemPath.substring(index, isCreate) + probPk
    } else{
        problemPath = problemPath.substring(index, problemPath.length)
    }

    var uploadPath = root + problemPath + '/uploaddata';

    $('#file_upload').change(function(){
        var uploadedFile = $("#file_upload").prop('files')[0];

    		if(uploadedFile != undefined){
						validFile = true;

						// Check validity of file
						if (uploadedFile.size > MAX_FILE_SIZE){
								alert("File upload rejected, file is too big. Max size: " + MAX_FILE_SIZE);
								validFile = false;
						}
						//if (uploadedFile.type != "text/csv"){
						//		alert("File upload rejected, file is not csv");
						//		validFile = false;
						//}

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
                alert("Error deleting file.");
            }
        })
        .error(function(jqXHR, textStatus, errorThrown){
            alert("Error deleting file.");
        });
    });
}
