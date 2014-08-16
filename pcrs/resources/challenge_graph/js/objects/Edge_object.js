/**
 * Makes an Edge with a parent Node parent and a child node child.
 * @param parent The parent Node that the new Edge points from.
 * @param child The child Node that the new Edge points to.
 * @param name The 'name' of the new Edge.
 */
function makeEdge(parent, child, name) {
    "use strict";

    if (typeof parent !== 'undefined' && typeof child !== 'undefined') {
        window[name] = new Edge(parent, child, name);
        parent.outEdges.push(window[name]);
        child.inEdges.push(window[name]);
        parent.children.push(child);
        child.parents.push(parent);
    }
}


/**
 * Creates an Edge that represents an SVG path.
 * @constructor
 * @param {Node} parent The Node that this edge points from.
 * @param {Node} child  The Node that this Edge points to.
 * @param {string} name The name of the Edge, also the id of the SVG
 *                      counterpart.
 */
function Edge(parent, child, name) {
    "use strict";
    this.parent = parent;
    this.child = child;
    this.name = name;
    this.status = 'inactive';
}


/**
 * Updates the data-active attribute of this Edge, as well as its arrow head
 * (the parents only polygon child).
 */
Edge.prototype.updateSVG = function () {
    "use strict";
    $('#' + this.name).attr('data-active', this.status)
                      .parent()
                      .children('polygon')
                      .first()
                      .attr('data-active', this.status);
};


/**
 * Updates this Edge's status based on the status's of this Edge's parent
 * and child Nodes.
 */
Edge.prototype.updateStatus = function () {
    "use strict";

    if (!this.parent.isSelected()) {
        this.status = 'inactive';
    } else if (!this.child.isSelected()) {
        this.status = 'doable';
    } else {
        this.status = 'active';
    }

    this.updateSVG();
};
