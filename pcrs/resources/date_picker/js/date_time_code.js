$(document).ready(function() {
    $('.datetimeinput').attr({'placeholder':'YYYY-MM-DD HH:mm'});
    var needed_controls = $('.controls').has('.datetimeinput');
    needed_controls.attr({"data-date-format":"YYYY-MM-DD HH:mm"});
    needed_controls.removeClass('controls');
    needed_controls.addClass('input-group date');
    needed_controls.append("<span class='input-group-addon'><span class='glyphicon glyphicon-calendar'></span></span>");
    needed_controls.datetimepicker();
});