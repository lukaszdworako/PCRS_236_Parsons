from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete

from problems.models import (AbstractSubmission, AbstractTestRun,
                             testcase_delete, problem_delete)
from problems_rdb.db_wrapper import StudentWrapper
from problems_rdb.models import RDBProblem, RDBTestCase


class Problem(RDBProblem):
    """
    A SQL problem, extends RDBProblem.

    The problem solution is expected to be a set of valid SQL expressions.
    The value in order_matters defines whether the solution comparison
    is exact, or set-based.

    When a SQLProblem is deleted, any associated SQLTestCases are also deleted.
    """
    language = 'sql'

    order_matters = models.BooleanField(null=False, default=False)

    @property
    def affect_submissions(self):
        return ['solution', 'order_matters']

    def validate_solution(self):
        self._run_solution(self.solution)


class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def run_testcases(self, request):
        results = []
        testcases = self.problem.testcase_set.all()
        with StudentWrapper(database=settings.RDB_DATABASE,
                            user=request.user.username) as db:
            for testcase in testcases:
                dataset = testcase.dataset
                result = db.run_testcase(self.problem.solution, self.submission,
                                         dataset.namespace,
                                         self.problem.order_matters)
                TestRun(submission=self, testcase=testcase,
                        test_passed=result['passed']).save()
                result['testcase'] = testcase
                results.append(result)
        return results, None


class TestCase(RDBTestCase):
    """
    A test case for a SQL problem. A SQLTestCase consists of an associated
    SQLProblem and a Dataset.

    When a Dataset or a SQLProblem is deleted, any associated SQLTestCases
    are also deleted.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)


class TestRun(AbstractTestRun):
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)


# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)

post_delete.connect(problem_delete, sender=Problem)