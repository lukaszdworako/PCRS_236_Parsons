//root is a global variable from base.html

// Also handles whether keys field for Short Answer Questions is required
$(document).ready(function() {
    idKeys = $('#id_keys');
    labelIdKeys = $('label[for="id_keys"]');
    requiredFieldClass = 'requiredField';
    requiredAttr = "required";
    asteriskHtml = "<span class='asteriskField'>*</span>"
    noSubmissionCheckBox = $("#id_no_correct_response")

    toggleRequired(noSubmissionCheckBox.is(':checked'), idKeys, labelIdKeys, requiredFieldClass, requiredAttr, asteriskHtml);
    noSubmissionCheckBox.change(function() {
        toggleRequired(this.checked, idKeys, labelIdKeys, requiredFieldClass, requiredAttr, asteriskHtml);
    })
});

function toggleRequired(checked, idKeys, labelIdKeys, requiredFieldClass, requiredAttr, asteriskHtml) {
    /*
    1) toggle required field from label for="id_keys"
    2) toggle asterisk from the label
    3) toggle required attribute in the text area for keys
    */
    if (checked) {
        labelIdKeys.removeClass(requiredFieldClass);
        $("span", labelIdKeys).remove();
        idKeys.removeAttr(requiredAttr);
    } else {
        labelIdKeys.addClass(requiredFieldClass);
        labelIdKeys.html(labelIdKeys.html() + asteriskHtml)
        idKeys.attr(requiredAttr, "");
    }
}
