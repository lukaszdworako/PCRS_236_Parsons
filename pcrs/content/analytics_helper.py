import problems_java, problems_python, problems_c, problems_sql, problems_ra
import problems_multiple_choice, problems_short_answer
from content.models import Challenge
from statistics import median

class QuestAnalyticsHelper:
    '''Used to compute quest analytics'''

    # Unfortunately, we have to iterate each model to get every type of problem
    problemModels = {
        'Java': problems_java.models,
        'Python': problems_python.models,
        'C': problems_c.models,
        'SQL': problems_sql.models,
        'RA': problems_ra.models,
        'Multiple Choice': problems_multiple_choice.models,
        'Short Answer': problems_short_answer.models,
    }

    def __init__(self, quest, users):
        self.users = users
        self.problems = self._getProblemsInQuest(quest)

    def _getProblemsInQuest(self, quest):
        problems = {}
        for problemType, problemModel in self.problemModels.items():
            problems[problemType] = problemModel.Problem.objects.filter(
                challenge=Challenge.objects.filter(quest=quest)
            )
        return problems

    def computeAllProblemInfo(self):
        '''Computes a list of problem information for the given quest

        The quest is specified in the constructor of this object

        Returns:
            A list of problem information.
            See _computeProblemInfoForProblem for format
        '''
        problemInfo = []
        for pType in self.problems.keys():
            for p in self.problems[pType]:
                problemInfo.append(self._computeProblemInfoForProblem(p, pType))
        return problemInfo

    def _computeProblemInfoForProblem(self, problem, problemType):
        submissionClass = self.problemModels[problemType].Submission

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
            bestSubmission = submissionClass.objects.get(
                user=user,
                problem=problem,
                has_best_score=True
            )
            if problem.max_score == bestSubmission.score:
                hasSolvedCount += 1

        # Round the median so we don't end up with weird numbers
        medianAttempts = int(median(userAttemptCounts)) \
            if len(userAttemptCounts) else 0

        return {
            'pk': problem.pk,
            'name': problem.name,
            'type': problemType,
            'medianAttempts': medianAttempts,
            'hasSolvedCount': hasSolvedCount,
            'hasAttemptedCount': hasAttemptedCount,
        }

