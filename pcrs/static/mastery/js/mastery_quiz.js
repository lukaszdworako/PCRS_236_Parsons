$(document).ready(function() {
	$('#start-mastery-quiz').on('click', function(e) {
		$.post(root + '/mastery/setup/api/start_session', {'csrfmiddlewaretoken': window.CSRF_TOKEN})
			.done(function(data) {
				if (data.status == 'success') {
					// Make sure they don't press the button again
					$('#id').text(data.code);
					$('#ta-modal-body').text('Your mastery quiz session has been started, with the code \
						' + data.code + '. Please make sure to \
						end the session after the time limit has expired. Sessions will be automatically closed after \
						one hour.');
					$('#ta-modal-header').text('Success!');
					$('#start-mastery-quiz').attr('disabled', true);
					$('#start-mastery-quiz').text(data.code);
				}
				else if (data.status == 'error') {
					$('#ta-modal-body').text(data.message);
					$('#ta-modal-header').text('Error');
				}
				$('#ta-modal').modal('show');
			});
	});
	$('#end-mastery-quiz').on('click', function() {
		$.post(root + '/mastery/setup/api/stop_session', {'csrfmiddlewaretoken': window.CSRF_TOKEN})
			.done(function(data) {
				if (data.status == 'success') {
					$('#end-mastery-quiz').attr('disabled', true);
					$success_div = $('<div/>').addClass('alert alert-success').text(data.message);
					$('.messages').append($success_div);
				}
				else {
					$error_div = $('<div/>').addClass('alert alert-danger').text(data.message);
					$('.messages').append($error_div);
				}
				$(".alert").fadeTo(2000, 500).slideUp(500, function(){
					$(".alert").slideUp(500);
					$(this).alert('close');
				});
			});
	});
	$('#ta-modal').on('hidden.bs.modal', function() {
		location.reload()
	});
});
