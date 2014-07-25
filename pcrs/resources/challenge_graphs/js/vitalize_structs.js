/**
 * Represents an SVG graph node (with rectangle and text).
 * @constructor
 * @param {string} name - The name of the Node, also the id of the SVG counterpart.
 */
function Node(name) {
    this.name = name;
    this.parents = [];
    this.children = [];
    this.outEdges = [];
    this.inEdges = [];
    this.updated = false;
    this.status = '';
}

/*
 *
 */
Node.prototype.isSelected = function () {
    return this.status === 'active' || this.status === 'overridden';
}


/*
 *
 */
Node.prototype.arePrereqsSatisfied = function () {
    var sat = true;
    for (var i = 0; i < this.parents.length; i++) {
        sat = sat && this.parents[i].isSelected();
    }
    return sat;
}


/*
 *
 */
Node.prototype.updateSVG = function () {
    $('#' + this.name).attr('data-active', this.status);
}


/*
 *
 */
Node.prototype.focus = function () {
    if (this.status !== 'active') {
        if (this.status !== 'overridden') {
            $("#" + this.name).attr('data-active', 'missing');
        }
        $.each(this.inEdges, function (i, edge) {
            if (edge.parent.status !== 'active') {
                $("#" + edge.name).attr('data-active', 'missing');
                $("#" + edge.name).parent().children("polygon").first().attr('data-active', 'missing');
            }
        });
        $.each(this.parents, function (i, node) {
            node.focus();
        });
    }
}


/*
 *
 */
Node.prototype.unfocus = function () {
    if (!this.isSelected()) {
        $("#" + this.name).attr('data-active', this.status);
    }
    $.each(this.parents, function (i, node) {
        node.unfocus();
    });
    $.each(this.outEdges, function (i, edge) {
        edge.updateStatus();
    });
}


/*
 *
 */
Node.prototype.updateStatus = function () {
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
}


/*
 *
 */
Node.prototype.turn = function () {
    this.status = 'active';

    $("#" + this.name).children(".counter-text").remove();
    $("#" + this.name).children(".missing-counter").attr("fill", "url(#active-image)");

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
}


/**
 * Represents an SVG path.
 * @constructor
 * @param {Node} parent - The Node that this edge points from.
 * @param {Node} child - The Node that this Edge points to.
 * @param {string} name - The name of the Edge, also the id of the SVG counterpart.
 */
function Edge(parent, child, name) {
    this.parent = parent;
    this.child = child;
    this.name = name;
    this.status = 'inactive';
}


/*
 *
 */
Edge.prototype.updateSVG = function () {
    $('#' + this.name).attr('data-active', this.status);
    $('#' + this.name).parent().children("polygon").first().attr('data-active', this.status);
}


/*
 *
 */
Edge.prototype.updateStatus = function () {
    if (!this.parent.isSelected()) {
        this.status = 'inactive';
    } else if (!this.child.isSelected()) {
        this.status = 'doable';
    } else {
        this.status = 'active';
    }

    this.updateSVG();
}

/*
 * @param {string} name - The name of the Node, also the id of the SVG counterpart.
 */
function makeNode(name) {
    window[name] = new Node(name);
    nodes.push(name);
}


/*
 *
 */
function makeEdge(parent, child, name) {
    window[name] = new Edge(parent, child, name);
    parent.outEdges.push(window[name]);
    child.inEdges.push(window[name]);
    parent.children.push(child);
    child.parents.push(parent);
}