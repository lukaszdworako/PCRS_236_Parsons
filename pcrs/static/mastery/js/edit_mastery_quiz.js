$(document).ready(function() {

	var challenges;

	$.get('get_challenges', function(response) {
		challenges = response;
	});

	$mastery_challenge_html = ''
	
	$(document).on('click', '.add-test-to-challenge', function(e) {
		// Get all available mastery quizzes
		$.get('get_challenges', function(response) {
			$li_html = '\
				<li style="background: #fff9c4" mastery-id="new" class="quiz-item-container list-group-item bg-change"> \
					<div class="pull-left form-inline"> \
						<input placeholder="Test Name" \
							class="input-name editable form-control" \
							type="text" \
							value=""> \
						</input> \
						<input placeholder="Pass Threshold" \
							class="input-pass-threshold editable form-control" \
							type="text" \
							value=""> \
						</input><select class="mastery-test-id selectpicker">';
			for (var i = 0; i < response.challenges.length; i++) {
				$li_html += '<option value="' + response.challenges[i].id +'">'+ response.challenges[i].name +'</option>';
			}
			$li_html += '</select>\
					</div> \
					<div class="pull-right mastery-edit-icons"> \
						<span style="color: #66bb6a"> \
							<i class="save-test mastery-edit-icon fa fa-check-circle fa-2x" aria-hidden="true"></i> \
						</span> \
						<span style="color: #ef5350"> \
							<i class="delete-test mastery-edit-icon fa fa-times-circle fa-2x" aria-hidden="true"> \
						</i></span> \
					</div> \
					<div style="clear: both"></div> \
				</li>';
			$(e.target).closest('.panel-heading').next().append($li_html);
			$('.selectpicker').selectpicker('refresh');
		});
	});

	$('.myclass').each(function(){
		$(this).attr('oldval',$(this).val());
	});

	$(document).on('change keypress paste textInput input', '.editable', function(e) {
		var val = $(this).val();
		if(val != $(this).attr('oldval') ){
			$(this).attr('oldval', val);
			$(e.target).closest('.bg-change').css('background', '#fff9c4');
		}
	});

	$(document).on('click', '.save-test', function(e) {
		data = {};
		data.csrfmiddlewaretoken = window.CSRF_TOKEN;
		data.id = $(e.target).closest('.quiz-item-container').attr('mastery-id');
		data.pass_threshold = $(e.target).closest('.quiz-item-container').children(':first').find('.input-pass-threshold').val();
		data.name = $(e.target).closest('.quiz-item-container').children(':first').find('.input-name').val();
		data.mastery_quiz_challenge_id = $(e.target).closest('.quiz-item-container').parent().prev().attr('challenge-id');
		data.mastery_quiz_test_challenge_id = $(e.target).closest('.quiz-item-container').find('select.mastery-test-id')
			.find('option:selected').val();
		$.post('edit_quizzes/test/add', data, function(response) {
			if (response.status == 'success') {
				// Change the background back to white, feedback for the instructor that we've saved it
				$(e.target).closest('.bg-change').css('background', 'white');
				// Update the test ID if we have to
				if ('test_id' in response) {
					$(e.target).closest('.quiz-item-container').attr('mastery-id', response.test_id)
				}
			}
		});
	});

	$(document).on('click', '.delete-test', function(e) {
		data = {};
		data.csrfmiddlewaretoken = window.CSRF_TOKEN;
		data.id = $(e.target).closest('.quiz-item-container').attr('mastery-id');
		$.post('edit_quizzes/test/delete', data, function(response) {
			if (response.status == 'success') {
				// Remove the entry (now deleted)
				$(e.target).closest('.bg-change').remove();
			}
		});
	});

	$(document).on('click', '.edit-quiz-time', function(e) {
		data = {};
		data.csrfmiddlewaretoken = window.CSRF_TOKEN;
		data.username = $('#username').val();
		data.ratio = $('#ratio').val();
		$.post('mastery_quiz_times/edit', data)
		.done(function() {
			location.reload();
		});
	});

	$(document).on('click', '.add-mastery-btn', function(e) {
		data = {};
		data.csrfmiddlewaretoken = window.CSRF_TOKEN;
		$.post('add_mastery_quiz', data, function(response) {
			location.reload();
		});
	});

	$(document).on('click', '.delete-challenge', function(e) {
		data = {};
		data.csrfmiddlewaretoken = window.CSRF_TOKEN;
		data.id = $(e.target).closest('.quiz-challenge').attr('challenge-id');
		$.post('delete_mastery_quiz', data, function(response) {
			if (response.status = 'success') {
				// Remove from the UI
				$(e.target).closest('.quiz-challenge').parent().remove();
			}
		});
	});

	$(document).on('click', '.save-challenge', function(e) {
		data = {};
		data.csrfmiddlewaretoken = window.CSRF_TOKEN;
		data.id = $(e.target).closest('.quiz-challenge').attr('challenge-id');
		data.name = $(e.target).closest('.quiz-challenge').find('.mastery-name').val();
		data.mastery_quiz_challenge_id = $(e.target).closest('.quiz-challenge').find('.mastery-quest-id').find(":selected").val();
		data.mastery_quiz_requires_id = $(e.target).closest('.quiz-challenge').find('.required-mastery-test')
			.find(":selected").val();
		$.post('save_mastery_quiz', data, function(response) {
			if (response.status = 'success') {
				// Change back to white
				$(e.target).closest('.bg-change').css('background', 'white');
			}
		});
	});

});