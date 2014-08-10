/*global $*/

/**
 * Represents an SVG graph node (with svg rects and svg texts).
 * @constructor
 * @param {string} name - The name of the Node, also the id of the SVG counterpart.
 */
function Node(name) {
    "use strict";
    this.name = name;
    this.parents = [];
    this.children = [];
    this.outEdges = [];
    this.inEdges = [];
    this.status = '';
}

/**
 * Returns whether this Node is 'active' or 'overriden'.
 */
Node.prototype.isSelected = function () {
    "use strict";
    return this.status === 'active' || this.status === 'overridden';
};


/**
 * Returns true if the parent nodes of this Node are selected.
 * @returns {boolean} Whether the parent nodes of this Node are selected.
 */
Node.prototype.arePrereqsSatisfied = function () {
    "use strict";
    var sat = true;

    for (var i = 0; i < this.parents.length; i++) {
        sat = sat && this.parents[i].isSelected();
    }

    return sat;
};


/**
 * Updates the data-active attribute of this Node.
 */
Node.prototype.updateSVG = function () {
    "use strict";
    $('#' + this.name).attr('data-active', this.status);
};


/**
 * Displays ('lights up') this Node and all preceding parent nodes.
 */
Node.prototype.focus = function () {
    "use strict";

    if (this.status !== 'active') {
        if (this.status !== 'overridden') {
            $('#' + this.name).attr('data-active', 'missing');
        }

        $.each(this.inEdges, function (i, edge) {
            if (edge.parent.status !== 'active') {
                $('#' + edge.name).attr('data-active', 'missing')
                                  .parent().children('polygon').first().attr('data-active', 'missing');
            }
        });

        $.each(this.parents, function (i, node) {
            node.focus();
        });
    }
};


/**
 * Reverses the 'light up' effect produced by Node.prototype.focus.
 */
Node.prototype.unfocus = function () {
    "use strict";

    if (!this.isSelected()) {
        $('#' + this.name).attr('data-active', this.status);
    }

    $.each(this.parents, function (i, node) {
        node.unfocus();
    });

    $.each(this.outEdges, function (i, edge) {
        edge.updateStatus();
    });
};


/**
 * Updates this Node's status based on its prerequisites and whether this Node is selected.
 */
Node.prototype.updateStatus = function () {
    "use strict";

    if (this.arePrereqsSatisfied()) {
        if (this.isSelected()) {
            this.status = 'active';
        } else {
            this.status = 'doable';
        }
    } else {
        if (this.isSelected()) {
            this.status = 'overridden';
        } else {
            this.status = 'inactive';
        }
    }

    this.updateSVG();
};


/**
 * Turns the node 'active' if the node is not active and if the parents of this Node are selected. 'Overriden' otherwise.
 * Note: Can also be implemented to reverse 'active' to 'inactive' (or 'overridden' to 'inactive').
 */
Node.prototype.turn = function () {
    "use strict";

    this.status = 'active';
    var nodObject = $('#' + this.name);
    nodObject.children('.counter-text').remove();
    nodObject.children('.missing-counter').remove();

    this.updateStatus();

    $.each(this.children, function (i, node) {
        node.updateStatus();
    });
    $.each(this.outEdges, function (i, edge) {
        edge.updateStatus();
    });
    $.each(this.inEdges, function (i, edge) {
        edge.updateStatus();
    });

    this.updateSVG();
    updateNavGraph($("#" + this.name));
};


/**
 * Represents an SVG path.
 * @constructor
 * @param {Node} parent - The Node that this edge points from.
 * @param {Node} child - The Node that this Edge points to.
 * @param {string} name - The name of the Edge, also the id of the SVG counterpart.
 */
function Edge(parent, child, name) {
    "use strict";
    this.parent = parent;
    this.child = child;
    this.name = name;
    this.status = 'inactive';
}


/**
 * Updates the data-active attribute of this edge, as well as its arrow head (the parents only polygon child).
 */
Edge.prototype.updateSVG = function () {
    "use strict";
    $('#' + this.name).attr('data-active', this.status)
                      .parent().children('polygon').first().attr('data-active', this.status);
};


/**
 * Updates this Node's status based on its prerequisites and whether this Node is selected.
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


/**
 * Makes a Node.
 * @param {string} name - The name of the Node, also the id of the SVG counterpart.
 */
function makeNode(name) {
    "use strict";
    window[name] = new Node(name);
    nodes.push(name);
}


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
