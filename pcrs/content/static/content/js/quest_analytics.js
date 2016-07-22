function QuestAnalyticsRenderer(userCount, problems) {
    this.userCount = userCount;
    this.problems = problems;
}

QuestAnalyticsRenderer.prototype.renderTo = function($analyticsTable) {
    // No sorting initially
    this._renderProblemsToTable(this.problems, $analyticsTable);
}

QuestAnalyticsRenderer.prototype._renderProblemsToTable =
        function(problems, $table) {
    for (var i = 0; i < problems.length; i++) {
        var problem = problems[i];

        var $row = $('<tr></tr>').attr('class', 'analytics-problem-row')
            .append($('<td></td>').text(problem.name))
            .append($('<td></td>').text(problem.language))
            .append($('<td></td>').text(problem.medianAttempts))
            .append($('<td></td>').text(
                problem.hasAttemptedCount + ' / ' + this.userCount))
            .append($('<td></td>').text(
                problem.hasSolvedCount + ' / ' + this.userCount))
        $table.append($row);
    }
}

