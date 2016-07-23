/**
 * @param {number} userCount The amount of users in this quest
 * @param {array} problems A list of problem analytics
 * @param {string} problems[].name
 * @param {string} problems[].language
 * @param {number} problems[].medianAttempts
 * @param {number} problems[].hasAttemptedCount
 * @param {number} problems[].hasSolvedCount
 */
function QuestAnalyticsRenderer(userCount, problems, $analyticsTable) {
    this.userCount = userCount;
    this.problems = problems;
    this.$analyticsTable = $analyticsTable;
}

QuestAnalyticsRenderer.prototype.render = function() {
    this._renderProblems(this.problems);
    this.$analyticsTable.tablesort(); // jQuery plugin
}

QuestAnalyticsRenderer.prototype._renderProblems = function(problems) {
    this.$analyticsTable.find('.analytics-problem-row').remove();
    for (var i = 0; i < problems.length; i++) {
        var problem = problems[i];

        var $row = $('<tr></tr>').attr('class', 'analytics-problem-row')
            .append($('<td></td>').text(problem.name))
            .append($('<td></td>').text(problem.language))
            .append($('<td></td>').text(problem.medianAttempts))
            .append($('<td></td>').text(problem.hasAttemptedCount))
            .append($('<td></td>').text(problem.hasSolvedCount))
        this.$analyticsTable.find('tbody').append($row);
    }
}

