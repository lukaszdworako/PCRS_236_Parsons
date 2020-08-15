//root is a global variable from base.html

// Also handles whether keys field for Short Answer Questions is required
$(document).ready(function() {
    idAnswerKeys = $('#id_answer_keys');
    labelIdAnswerKeys = $('label[for="id_answer_keys"]');
    requiredFieldClass = 'requiredField';
    requiredAttr = "required";
    asteriskHtml = "<span class='asteriskField'>*</span>"
    noSubmissionCheckBox = $("#id_no_correct_response")
    labelIdAnswerKeys.addClass(requiredFieldClass);
    labelIdAnswerKeys.html(labelIdKeys.html() + asteriskHtml)
    idAnswerKeys.attr(requiredAttr, "");
});




