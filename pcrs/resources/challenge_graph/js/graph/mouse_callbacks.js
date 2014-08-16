/**
 * Sets the mouse callbacks for the nodes.
 */
function setMouseCallbacks() {
    "use strict";
    var nodeObjects = $('#graph').find('.node');
    nodeObjects.mouseenter(function (event) {
            updateParentCount($(this).children('.counter-text'), true);
            hoverFocus(event);
        })
        .mouseleave(function (event) {
            updateParentCount($(this).children('.counter-text'), false);
            hoverUnfocus(event);
        });
    setKeydown();
}

/**
 * Sets the keydown events for zoom and scrolling.
 */
function setKeydown() {
    "use strict";
    $(document).keydown(function(e){
        switch (e.keyCode) {
            case 187: // + Key
                zoomIn();
                break;
            case 189: // - Key
                zoomOut();
                break;
        }
        $('#scroll-content').mCustomScrollbar('update');
    });
}