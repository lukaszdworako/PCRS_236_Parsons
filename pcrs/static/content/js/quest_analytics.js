/**
 * @param {number} userCount The amount of users in this quest
 * @param {array} problems A list of problem analytics
 * @param {string} problems[].name
 * @param {string} problems[].type
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

    var integerSortFunction = function(th, td, tablesort) {
        return parseInt(td.text());
    };
    var percentSortFunction = function(th, td, tablesort) {
        // Convert the float percentage to an integer for sorting
        return parseFloat(td.text()) * 100;
    };
    this.$analyticsTable.find('th#problemAttemptPercent').data('sortBy',
        percentSortFunction);
    this.$analyticsTable.find('th#problemSolvedPercent').data('sortBy',
        percentSortFunction);
    this.$analyticsTable.find('th#problemName').data('sortBy',
        integerSortFunction);
    this.$analyticsTable.find('th#problemAttemptMedian').data('sortBy',
        integerSortFunction);
}

QuestAnalyticsRenderer.prototype._renderProblems = function(problems) {
    this.$analyticsTable.find('.analytics-problem-row').remove();
    for (var i = 0; i < problems.length; i++) {
        var problem = problems[i];

        var $problemNameLink = $('<a></a>')
            .text((i + 1) + ': ' + problem.name)
            .attr('href', problem.url + '/submit');
        var hasAttemptedText = this._formatPercentage(
            problem.hasAttemptedCount / this.userCount);
        var hasSolvedText = this._formatPercentage(
            problem.hasSolvedCount / this.userCount);

        var $row = $('<tr></tr>').attr('class', 'analytics-problem-row')
            .append($('<td></td>').append($problemNameLink))
            .append($('<td></td>').text(problem.type))
            .append($('<td></td>').text(problem.medianAttempts))
            .append($('<td></td>').text(hasAttemptedText))
            .append($('<td></td>').text(hasSolvedText))
        this.$analyticsTable.find('tbody').append($row);
    }
}

QuestAnalyticsRenderer.prototype._formatPercentage = function(num) {
    return (100 * num).toFixed(2) + '%';
}

