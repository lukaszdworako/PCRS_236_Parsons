from django.conf import settings

import problems_java, problems_python, problems_c, problems_sql, problems_ra
import problems_multiple_choice, problems_short_answer, problems_parsons
from content.models import (Challenge, ContentType, ContentPage,
    ContentSequenceItem)
from statistics import median

from pcrs.models import get_problem_content_types

class QuestAnalyticsHelper:
    '''Used to compute quest analytics'''

    # Unfortunately, we have to iterate each model to get every type of problem
    problemModels = {
        # These should match the names in INSTALLED_PROBLEM_APPS
        'problems_java': problems_java.models,
        'problems_python': problems_python.models,
        'problems_c': problems_c.models,
        'problems_sql': problems_sql.models,
        'problems_ra': problems_ra.models,
        'problems_multiple_choice': problems_multiple_choice.models,
        'problems_short_answer': problems_short_answer.models,
        'problems_parsons': problems_parsons.models,
    }

    def __init__(self, quest, users):
        self.users = users
        self.quest = quest

    def computeAllProblemInfo(self):
        '''Computes a list of problem information for the given quest

        The quest is specified in the constructor of this object

        Returns:
            A list of problem information.
            See _computeProblemInfoForProblem for format
            This list is sorted in the order of the quest
        '''
        problemInfo = []
        for challenge in Challenge.objects.filter(quest=self.quest):
            for page in ContentPage.objects.filter(challenge=challenge):
                problemInfo += self._getProblemsInfoInPage(page)
        return problemInfo

    def _getProblemsInfoInPage(self, page):
        '''Gathers all problem in the given page.

        To order the problems nicely, this code has to be convoluted >:(
        '''
        problemInfo = []

        for item in ContentSequenceItem.objects.filter(content_page=page):
            contentType = item.content_type
            if contentType.name != "problem":
                # Must be a non-problem. e.g. text or a video
                continue
            if contentType.app_label not in self.problemModels.keys():
                # If the problem type is not configured
                continue

            problemTypeName = contentType.app_label
            problemModel = self.problemModels[problemTypeName]

            problemId = item.object_id
            problem = problemModel.Problem.objects.get(pk=problemId)

            problemInfo.append(
                self._computeProblemInfoForProblem(problem, problemTypeName))

        return problemInfo

    def _computeProblemInfoForProblem(self, problem, problemTypeName):
        submissionClass = self.problemModels[problemTypeName].Submission

        userAttemptCounts = []
        hasSolvedCount = 0
        hasAttemptedCount = 0

        for user in self.users:
            submissionsCount = submissionClass.objects.filter(
                user=user,
                problem=problem
            ).count()
            userAttemptCounts.append(submissionsCount)
            if submissionsCount == 0:
                continue

            hasAttemptedCount += 1
            bestSubmission = submissionClass.objects.filter(
                user=user,
                problem=problem,
                has_best_score=True
            )[0]
            if problem.max_score == bestSubmission.score:
                hasSolvedCount += 1

        # Round the median so we don't end up with weird numbers
        medianAttempts = int(median(userAttemptCounts)) \
            if len(userAttemptCounts) else 0

        return {
            'pk': problem.pk,
            'url': problem.get_absolute_url(),
            'name': problem.name,
            'type': settings.INSTALLED_PROBLEM_APPS[problemTypeName],
            'medianAttempts': medianAttempts,
            'hasSolvedCount': hasSolvedCount,
            'hasAttemptedCount': hasAttemptedCount,
        }

