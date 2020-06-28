$(document).ready(function() {
  $(function() {
      $("#quest_table .challenge-node").draggable({
        stack: "div",
        start: function() {
          $original_div = $(this);
          $original_td = $(this).parent();
          $('td').addClass('drag-available');
          $($(this).parent()).removeClass('drag-available');
        },
        stop: function() {
          $('td').removeClass('drag-available');
        },
        revert: "invalid",
        revertDuration: 100,
      });
      $("#quest_table td").droppable({
        drop: function(event, ui) {
          var $this = $(this);
          ui.draggable.parent().append($(this).children());
          $(this).append(ui.draggable);
          ui.draggable.css({
              left: '',
              top: ''
          });
          ui.draggable.position({
            my: "center",
            at: "center",
            of: $this,
            using: function(pos) {
              $(this).animate(pos, 0, "linear");
            }
          });
        }
    });
  });
})
