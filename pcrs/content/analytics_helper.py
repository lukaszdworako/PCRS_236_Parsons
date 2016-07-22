import problems_java, problems_python, problems_c, problems_sql, problems_ra
from content.models import Challenge
from statistics import median

class QuestAnalyticsHelper:
    '''Used to compute quest analytics'''

    # Unfortunately, we have to iterate each model to get every type of problem
    problemModels = {
        'java': problems_java.models,
        'python': problems_python.models,
        'c': problems_c.models,
        'sql': problems_sql.models,
        'ra': problems_ra.models,
    }

    def __init__(self, quest, users):
        self.users = users
        self.problems = self._getGradedProblemsInQuest(quest)

    def _getGradedProblemsInQuest(self, quest):
        problems = []
        for problemModel in self.problemModels.values():
            problems += problemModel.Problem.objects.filter(
                challenge=Challenge.objects.filter(
                    quest=quest,
                    is_graded=True
                )
            )
        return problems

    def computeAllProblemInfo(self):
        '''Computes a list of problem information for the given quest

        The quest is specified in the constructor of this object

        Returns:
            A list of problem information. See _problemInfo for format
        '''
        return [ self._computeProblemInfoForProblem(p) for p in self.problems ]

    def _computeProblemInfoForProblem(self, problem):
        submissionClass = self.problemModels[problem.language].Submission

        userAttemptCounts = []
        hasSolvedCount = 0
        hasAttemptedCount = 0

        for user in self.users:
            submissions = submissionClass.objects.filter(
                user=user,
                problem=problem
            )

            userAttemptCounts.append(submissions.count())
            if submissions.count() == 0:
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
            'language': problem.language,
            'medianAttempts': medianAttempts,
            'hasSolvedCount': hasSolvedCount,
            'hasAttemptedCount': hasAttemptedCount,
        }

