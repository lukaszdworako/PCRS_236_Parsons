function create_history_code_mirror (language, version, location){
    hcm = history_code_mirror(language, version, $('#'+location), $('#'+location).text()), true;
    if (!(location in cmh_list)){
        cmh_list[location] = hcm;
    }
}

function history_code_mirror (language, version, location, value, lock){

    historyCodeMirror = CodeMirror(function(elt) {
		$(location).replaceWith(elt);
		}, {mode: {name: language,
	               version: version,
	               singleLineStringErrors: false},
	      //themes can be found in codemirror4.1/theme; must be loaded in submission.html
	      	theme: "monokai",
			value: value,
			lineNumbers: 'True',
            readOnly: lock,
			lineWrapping: 'True',
			flattenSpans: 'False'});
    return historyCodeMirror;
}
