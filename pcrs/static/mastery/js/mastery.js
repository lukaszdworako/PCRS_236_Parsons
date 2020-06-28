$(document).ready(function() {
	$('#mastery-quiz-button').on('click', function() {
		$('#mastery-code-modal').modal('show');
	});
	$('#join-quiz').on('click', function() {
		$.post(root + '/mastery/student/api/join_session', {
			'csrfmiddlewaretoken': window.CSRF_TOKEN, 
			'code': $('#mastery-code-input').val()
		})
		.done(function(data) {
			if (data.status == 'success') {
				$success_div = $('<div/>').addClass('alert alert-success').text(data.message);
				$('.messages').html($success_div);
				$(".alert").fadeTo(4000, 500).slideUp(500, function(){
					$(".alert").slideUp(500);
					$(this).alert('close');
					window.location.href = root + '/mastery/quiz';
				});
			}
			else {
				$error_div = $('<div/>').addClass('alert alert-danger').text(data.message);
				$('.messages').html($error_div);
				$(".alert").fadeTo(4000, 500).slideUp(500, function(){
					$(".alert").slideUp(500);
					$(this).alert('close');
				});
				}

		});
	});
});
