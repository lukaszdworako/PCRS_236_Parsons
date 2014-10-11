function create_history_code_mirror (language, version, location){
    hcm = history_code_mirror(language, version, $('#'+location), $('#'+location).text(), true);
    if (!(location in cmh_list)){
        cmh_list[location] = hcm;
    }
}

function history_code_mirror (language, version, location, value, lock){

    var mode;
    if (language == 'python'){
        mode = {name: language,
                version: version,
                singleLineStringErrors: false}
    }
    else if (language == 'sql'){
        mode = 'text/x-plsql';
    }
    else if (language == 'ra'){
        mode = 'text/ra';
    }
    else if (language == 'c'){
        mode = 'text/x-csrc';
    }
    historyCodeMirror = CodeMirror(function(elt) {
        $(location).replaceWith(elt);
        }, {mode: mode,
          //themes can be found in codemirror4.1/theme; must be loaded in submission.html
            theme: user_theme,
            value: value,
            lineNumbers: 'True',
            indentUnit: 4,
            readOnly: lock,
            lineWrapping: 'True',
            flattenSpans: 'False'});


    return historyCodeMirror;
}
