/**
 * Initializes user data so that the nodes of the graph represent the
 * completed challenges.
 */
function initializeUserData() {
    "use strict";
    var userData = getJSON();
    $.each(userData, function (i, val) {
        if (val[0] === val[1]) {
            window["node-" + i].turn();
        }
    });
}

/**
 * Gets the JSON object produced for the current user.
 * @returns {*} The JSON object of the current user's challenge data.
 */
function getJSON() {
    "use strict";
    var json = null;
    $.ajax({
        url: 'prereq_graph/for_user',
        dataType: 'text',
        async: false,
        success: function (data) {
            json = data;
        }
    });
    return $.parseJSON(json);
}