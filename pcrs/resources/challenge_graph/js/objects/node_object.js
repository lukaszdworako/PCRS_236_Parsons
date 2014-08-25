/*global $*/


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
