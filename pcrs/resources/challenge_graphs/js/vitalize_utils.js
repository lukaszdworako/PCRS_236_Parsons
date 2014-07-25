/*
 *
 */
function intersects(px, py, rx, ry, width, height, offset) {
    var dx = px - rx;
    var dy = py - ry;
    return dx >= -1 * offset && dx <= width + offset && dy >= -1 * offset && dy <= height + offset;
}

/*
 *
 */
function release(func) {
    setTimeout(func, 5000);
}

/*
 * @param
 */
function hoverFocus(event) {
    var id = event.target.parentNode.id;
    window[id].focus();
};


/*
 * @param
 */
function hoverUnfocus(event) {
    var id = event.target.parentNode.id;
    window[id].unfocus();
};


/*
 * @param
 */
function turnNode(event) {
    var id = event.target.parentNode.id;
    window[id].turn();
};

/*
 *
 */
function increaseZoom() {
    zoom = zoom + 10;
    $("#graph-root").css("zoom", zoom + "%");
}

/*
 *
 */
function decreaseZoom() {
    zoom = zoom - 10;
    $("#graph-root").css("zoom", zoom + "%");
}
