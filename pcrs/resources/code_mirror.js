function create_history_code_mirror (language, version, location){
    hcm = history_code_mirror(language, version, location, $('#'+location).text());
    if (!(location in cmh_list)){
        cmh_list[location] = hcm;
    }
}

function history_code_mirror (language, version, location, value){
    historyCodeMirror = CodeMirror(function(elt) {
		$('#'+location).replaceWith(elt);
		}, {mode: {name: language,
	               version: version,
	               singleLineStringErrors: false},
	      //themes can be found in codemirror4.1/theme; must be loaded in submission.html
	      	theme: "monokai",
			value: value,
			lineNumbers: 'True',
            readOnly: 'True',
			lineWrapping: 'True',
			flattenSpans: 'False'});
    return historyCodeMirror;
}

function create_code_mirror (language, version, value){
    newCodeMirror = CodeMirror(function(elt) {
		$('#id_submission').replaceWith(elt);
		}, {mode: {name: language,
	               version: version,
	               singleLineStringErrors: false},
	      //themes can be found in codemirror4.1/theme; must be loaded in submission.html
	      	theme: "monokai",
			value: value,
			lineNumbers: 'True',
			lineWrapping: 'True',
			flattenSpans: 'False'});
    return newCodeMirror;
}