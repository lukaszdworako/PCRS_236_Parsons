/* 
A helper function for replacing table body data.
:param tableId: table id tag value (string)
:param data: table body inner html (string)
*/
function replaceTBody(tableId, data) {
    // current table body
    const tbody = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    // new table body (for inserting new rows)
    var new_tbody = document.createElement('tbody');
    // insert new rows
    new_tbody.innerHTML += data;
    // replace current table body with new table body
    tbody.parentNode.replaceChild(new_tbody, tbody);
}

/*
Gets the top 'num_of_problems', problems with difficulty, 'diff'.
:param diff: problem difficulty (string)
*/
async function getTopProblems(diff) {
    // number of problems dropdown
    const num_of_problems = document.getElementById("num_of_problems").value;

    // get the top <num_of_problems> problems
    const response = await fetch(root + '/analytics/api/problems/hard/' + num_of_problems);
    const data = await response.json();

    const problems = data[diff + "_problems"];

    var tbodyHTML = "";

    for (var i = 0; i < problems.length; i++) {
	
	const type = problems[i]['type'].slice(9);
	const problem_url = root + "/problems/" + type + "/" + problems[i]['id'];

	var tr = "<tr>";
	tr += "<td>"+ (i + 1).toString() + "</td>";
	tr += "<td>"+"<a href=" + problem_url +">"+problems[i]['name']+"</a>"+"</td>";
	tr += "<td>"+problems[i]['description']+"</td>";
	tr += "<td>"+type+"</td>";
	tr += "<td>"+problems[i]['attempts']+"</td>";
	tr += "</tr>";
	tbodyHTML += tr;
    }

    replaceTBody('generalProblemTable', tbodyHTML);

}

/*
Gets the users that have not attempted a mastery quiz with id, 'quizId'.
:param quizId: mastery quiz id
 */
async function getNotAttempted(quizId) {

    // get the list of users who haven't attempted the mastery quiz
    const response = await fetch(root + '/analytics/api/mastery_quiz/' + quizId + '/not_attempted');
    const data = await response.json();
    const users = data['users_not_attempted'];
    
    tbodyHTML = "";

    for (var i = 0; i < users.length; i++) {
	var tr = "<tr>";
	tr += "<td>"+ (i + 1).toString()  +"</td>";
	tr += "<td>"+users[i]+"</td>";
	tbodyHTML += tr;
    }

    replaceTBody('masteryQuizTable', tbodyHTML);
    
}

/*
Gets the users that have not finished a mastery quiz with id, 'quizId'.
:param quizId: mastery quiz id
 */
async function getNotFinished(quizId) {

    // get the list of users who haven't attempted the mastery quiz
    const response = await fetch(root + '/analytics/api/mastery_quiz/' + quizId + '/not_finished');
    const data = await response.json();
    const users = data['users_not_finished'];
    
    tbodyHTML = "";

    for (var i = 0; i < users.length; i++) {
	var tr = "<tr>";
	tr += "<td>"+ (i + 1).toString()  +"</td>";
	tr += "<td>"+users[i]+"</td>";
	tbodyHTML += tr;
    }

    replaceTBody('masteryQuizTable', tbodyHTML);
    
}


/* var easyBtn = document.getElementsByName('easy_problems')[0];
var hardBtn = document.getElementsByName('hard_problems')[0];    

easyBtn.addEventListener('click', getTopProblems('easy'));
hardBtn.addEventListener('click', getTopProblems('hard')); */
