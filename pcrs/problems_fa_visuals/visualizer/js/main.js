var canvas = document.getElementById("myCanvas");
var context = canvas.getContext('2d');
//var height = canvas.height = window.innerHeight;
var width = canvas.width = window.innerWidth;
var mouseClicked = false, mouseReleased = true;
var states = [];
var lines = [];
var LINE_RADIUS = 20;
var lastClick = null;
context.font = '30px sans-serif';
document.addEventListener("click", onMouseClick, false);
document.addEventListener("keydown", onKeyDown, false);

class Line {
	constructor(node1, node2) {
		this.start = node1;
		this.end = node2;
		this.isLoop = (node1 == node2);
		this.text = '';
	}
	draw(c, colour='#fff') {
		var drawx = this.start.x + (Math.cos(-Math.PI*(0.2/3)) * this.start.radius);
		var drawy = this.start.y - this.start.radius + (Math.sin(-Math.PI*(0.2/3)) * this.start.radius);
		if (this.isLoop) {
			c.beginPath();
			c.arc(this.start.x, this.start.y - this.start.radius, LINE_RADIUS, Math.PI * (2.8 / 3), Math.PI * (6.2 / 3), false);
			c.lineTo(drawx - 18, drawy + 5);
			c.moveTo(drawx - 30, drawy + 15);
			c.lineTo(drawx - 42, drawy + 5);
			c.strokeStyle = c.fillStyle = colour;
			c.lineWidth = 1;
			c.stroke();
			if (this.text != ''){
				var x = this.start.x
				var y = this.start.y - this.start.radius
				c.fillText(this.text, x - 7, y - LINE_RADIUS - 2);
			}
		} else{
			//slope = (this.end.y - this.start.y)/(this.end.x - this.start.x)
			var angle = Math.atan2(this.end.y - this.start.y, this.end.x - this.start.x);
			var startx = this.start.x + (Math.cos(angle) * this.start.radius);
			var starty = this.start.y + (Math.sin(angle) * this.start.radius);
			var endx = this.end.x - (Math.cos(angle) * this.start.radius);
			var endy = this.end.y - (Math.sin(angle) * this.start.radius);
			c.beginPath();
			c.moveTo(startx, starty);
			c.lineTo(endx, endy);
			var arrowtipx = endx - (Math.cos(angle-(Math.PI/4)) * 10);
			var arrowtipy = endy - (Math.sin(angle-(Math.PI/4)) * 10);
			var arrowtipx2 = endx - (Math.cos(angle+(Math.PI/4)) * 10);
			var arrowtipy2 = endy - (Math.sin(angle+(Math.PI/4)) * 10);
			c.lineTo(arrowtipx, arrowtipy);
			c.moveTo(endx, endy);
			c.lineTo(arrowtipx2, arrowtipy2);
			c.strokeStyle = c.fillStyle = colour;
			c.lineWidth = 1;
			c.stroke();
			if (this.text != ''){
				var x = (startx + endx)/2 - 10
				var y = (starty + endy)/2 - 5
				c.fillText(this.text, x, y);
			}
		}
	}
	delete(c){
		this.draw(c, '#000');
	}
	select(c){
		this.draw(c, '#00f');
	}
	contains(x, y) {
		if (this.isLoop){
			var xCheck = (x - this.start.x) * (x - this.start.x);
			var yCheck = (y - this.start.y + this.start.radius) * (y - this.start.y + this.start.radius);
			var circleSize = (LINE_RADIUS + 1)* (LINE_RADIUS + 1);
			return (xCheck + yCheck < circleSize) && !(this.start.contains(x, y));
		} else { 
			//Algorithm from: http://paulbourke.net/geometry/pointlineplane/
			var angle = Math.atan2(this.end.y - this.start.y, this.end.x - this.start.x);
			var startx = this.start.x + (Math.cos(angle) * this.start.radius);
			var starty = this.start.y + (Math.sin(angle) * this.start.radius);

			var endx =  this.end.x - (Math.cos(angle) * this.start.radius);
			var endy = this.end.y - (Math.sin(angle) * this.start.radius);

			var scalar = (((x - startx)*(endx - startx)) + ((y-starty)*(endy-starty)))/((endx - startx)**2 + (endy - starty)**2)
			var closex = startx + scalar*(endx - startx);
			var closey = starty + scalar*(endy - starty);
			var dist = Math.sqrt((closex - x)**2 + (closey - y)**2)
			return (dist < 10) && !(this.start.contains(x, y)) && !(this.end.contains(x, y));
			
			// var corner1 = endx - (Math.cos(angle-(Math.PI/2)) * 10);
			// var corner2 = endy - (Math.sin(angle-(Math.PI/2)) * 10);

			// var corner3 = endx - (Math.cos(angle+(Math.PI/2)) * 10);
			// var corner4 = endy - (Math.sin(angle+(Math.PI/2)) * 10);
		}
	}
}

class Cir {
	constructor(x, y) {
		this.x = x;
		this.y = y;
		this.accept = false;
		this.text = '';
		this.radius = 50;
	}
	draw(c, colour='#fff') {
		c.beginPath();
		c.arc(this.x, this.y, this.radius, 0, 2 * Math.PI, false);
		c.strokeStyle  = c.fillStyle = colour;
		c.stroke();
		if (this.accept){
			c.beginPath();
			c.arc(this.x, this.y, this.radius - 6, 0, 2 * Math.PI, false);
			c.stroke();
		}
	}
	delete(c){
		this.draw(c, '#000');
	}
	select(c){
		this.draw(c, '#00f');
	}
	contains(x, y) {
		return (x - this.x) * (x - this.x) + (y - this.y) * (y - this.y) < this.radius * this.radius;
	}
}

function redraw(c){
	c.clearRect(0, 0, canvas.width, canvas.height);
	for (var i = 0, len = states.length; i < len; ++i){
		states[i].draw(c);
	}
	for (var i = 0, len = lines.length; i < len; ++i){
		lines[i].draw(c);
	}
}

function onMouseClick(e) {
	var currClick = null;
	for (var i = 0, len = states.length; i < len; ++i){
		if (states[i].contains(e.clientX, e.clientY)){
			currClick = states[i];
			break;
		} 
	}
	for (var i = 0, len = lines.length; i < len; ++i){
		if (lines[i].contains(e.clientX, e.clientY)){
			currClick = lines[i];
			break;
		}
	}
	if (lastClick == null && (currClick instanceof Cir || currClick instanceof Line)){
		lastClick = currClick;
		lastClick.select(context);
	} else if (lastClick instanceof Cir && currClick instanceof Cir){
		newLine = new Line(lastClick, currClick);
		newLine.draw(context);
		lines.push(newLine);
		lastClick.draw(context);
		lastClick = null;
		currClick = null;
	} else if (lastClick == null && currClick == null){
		newState = new Cir(e.clientX, e.clientY);
		newState.draw(context);
		states.push(newState);
	} else {
		lastClick.draw(context);
		lastClick = null;
	}
	
}

function onKeyDown(e){
	if (e.key == "Delete" || e.key == "Backspace"){ //del or backspace
		if (lastClick instanceof Cir){
			var indices = [];
			for (i = 0, len = lines.length; i < len; ++i){
				if (lines[i].start == lastClick || lines[i].end == lastClick){
					//lines[i].delete(context);
					indices.push(i);
				}
			}
			for (i = 0, len = indices.length; i < len; ++i){
				lines.splice(indices[i], 1);
			}
			var i = 0;
            while (i < states.length) {
                if (states[i].x == lastClick.x && states[i].y == lastClick.y) {
                    states.splice(i, 1);
                } else {
                    i++;
                }
            }
			lastClick = null;
			redraw(context);
		} else if (lastClick instanceof Line){
			var indices = [];
			for (i = 0, len = lines.length; i < len; ++i){
				if (lines[i] == lastClick){
					indices.push(i);
				}
			}
			for (i = 0, len = indices.length; i < len; ++i){
				lines.splice(indices[i], 1);
			}
			lastClick = null;
			redraw(context);
		} else {
			//Nothing to delete!
		}
	} else {
		if (lastClick instanceof Cir && e.key == 'a'){
			for (var i = 0, len = states.length; i < len; ++i){
				if (states[i] == lastClick){
					states[i].accept = !states[i].accept;
					redraw(context);
					lastClick = null;
					break;
				} 
			}
		} else if (lastClick instanceof Line){
			for (var i = 0, len = lines.length; i < len; ++i){
				if (lines[i] == lastClick){
					lines[i].text = e.key;
					redraw(context);
					lastClick = null;
					break;
				} 
			}
		}	
	}
}

// function prettyPrintList(list){
// 	var chars = '';
// 	for (var i = 0, len = list.length; i < len; ++i){
// 		if (chars == '' && list[i] != ''){
// 			chars = chars + list[i];
// 		} else if (chars != '' && list[i] != '') {
// 			chars = chars + ', ' + list[i];
// 		}
// 	}
// }

function returnIndex(node){
	for (var i = 0, len = states.length; i < len; ++i){
		if (states[i] == node){
			return i;
			break;
		}
	}
	return -1;
}


function buttonClick(){
	//alpha
	//start
	//accept
	//transitions (start, letter, end)
	var alpha = '';
	for (var i = 0, len = lines.length; i < len; ++i){
		if (alpha == '' && lines[i].text != ''){
			alpha = alpha + lines[i].text;
		} else if (alpha != '' && lines[i].text != '') {
			alpha = alpha + ', ' + lines[i].text;
		}
	}
	var st = 1;
	var accept = '';
	for (var i = 0, len = states.length; i < len; ++i){
		if (accept == '' && states[i].accept){
			accept = accept + (i + 1);
		} else if (accept != '' && states[i].accept) {
			accept = alpha + ', ' + (i + 1);
		}
	}
	var transitions = [];
	for (var i = 0, len = lines.length; i < len; ++i){
		start = (returnIndex(lines[i].start) + 1).toString();
		end = (returnIndex(lines[i].end) + 1).toString();
		transitions.push(start + ', ' + lines[i].text + ', ' + end);
	}
	var content = '';
	content += alpha + '<br/>' + st + '<br/>' + accept + '<br/>';
	for (var i = 0, len = transitions.length; i < len; ++i){
		content += transitions[i] + '<br/>'
	}

	var theDiv = document.getElementById("output");
	theDiv.innerHTML = content;

}