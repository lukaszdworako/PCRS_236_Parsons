//root is a global variable from base.html

// Also handles whether keys field for Short Answer Questions is required
$(document).ready(function() {
    id_feedback_keys = $('#id_feedback_keys');
    labelIdFeedbackKeys = $('label[for="id_feedback_keys"]');
    requiredFieldClass = 'requiredField';
    requiredAttr = "required";
    asteriskHtml = "<span class='asteriskField'>*</span>"
    noSubmissionCheckBox = $("#id_no_correct_response")
});
