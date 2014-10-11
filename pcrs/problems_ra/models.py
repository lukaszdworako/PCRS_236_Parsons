from json import loads

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete

from pyparsing import ParseException
from problems_rdb.db_wrapper import StudentWrapper
from rapt.treebrd.errors import TreeBRDError
from rapt.rapt import Rapt

from rapt.treebrd.grammars import GRAMMARS as RAPT_GRAMMARS

from problems.models import (AbstractTestRun, AbstractSubmission,
                             testcase_delete, problem_delete)
from problems_rdb.models import RDBProblem, RDBTestCase, Schema


class Problem(RDBProblem):
    """
    A Relational Algebra problem.

    Must define rapt grammar.

    A solution is expected to be a non-empty set of RA expressions,
    as defined by the rasq grammar rules in the specified grammar.

    When a RAProblem is deleted, any associated RATestCases are also deleted.
    """
    language = 'ra'
    GRAMMARS = [(name, name) for name, cls in RAPT_GRAMMARS.items()]
    SEMANTICS = (('set', 'Set'), ('bag', 'Bag'),)
    grammar = models.TextField(blank=False, null=False, choices=GRAMMARS)
    semantics = models.TextField(blank=False, null=False, choices=SEMANTICS)

    @property
    def affect_submissions(self):
        return ['solution', 'grammar', 'semantics']

    def validate_solution(self):
        """
        Validate the problem solution.

        Check that solution parses correctly and runs correctly
        within the problem schema.
        """

        if self.grammar and self.schema:
            translator = Rapt(grammar=self.grammar,
                              syntax={'join_op': '\\product'}
            )
            schema = loads(self.schema.tables)
            try:
                sql = translator.to_sql(instring=self.solution,
                                        schema=schema,
                                        use_bag_semantics=self.semantics=='bag')
                self._run_solution('; '.join(sql))
            except ParseException as e:
                error = 'Syntax error at line {lineno} column {col}:  \'{line}\''\
                    .format(lineno=e.lineno, col=e.col, line=e.line)
                raise ValidationError({'solution': [error]})
            except TreeBRDError as e:
                raise ValidationError({'solution': [e]})


class TestCase(RDBTestCase):
    """
    A test case for an RA problem. An RATestCase consists of an associated
    RAProblem and a Dataset.

    When a Dataset or a RAProblem is deleted, any associated RATestCases
    are also deleted.
    """
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)


class Submission(AbstractSubmission):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def run_testcases(self, request):
        results = []
        testcases = self.problem.testcase_set.all()
        t_sub, t_ans, error = self.get_sql_translations()

        if not error:
            results, error = self.get_results(request, t_sub, t_ans, testcases)
        else:
            for testcase in testcases:
                TestRun(submission=self, testcase=testcase,
                        test_passed=False).save()
        return results, str(error) if error else None

    def get_results(self, request, submission, solution, testcases):
        results, error = [], None
        with StudentWrapper(database=settings.RDB_DATABASE,
                            user=request.user.username) as db:
            for testcase in testcases:
                dataset = testcase.dataset
                result = db.run_testcase('; '.join(solution),
                                         '; '.join(submission),
                                         dataset.namespace)
                TestRun(submission=self, testcase=testcase,
                        test_passed=result['passed']).save()
                result['testcase'] = testcase.id
                results.append(result)
                if result['error']:
                    error = self.parse_sql_error(result['error'])
        return results, error

    def parse_sql_error(self, error):
        if '42883' in error and 'type casts' in error:
            message = error.split(':')[3]
            line_starts = message.find('LINE')
            message = message[:line_starts]
            return 'Type error: {}'.format(message)
        return 'Error executing query.'

    def get_sql_translations(self):
        schema = loads(self.problem.schema.tables)
        use_bag = self.problem.semantics == 'bag'
        translator = Rapt(grammar=self.problem.grammar,
                          syntax={'join_op': '\\product'})
        submission, solution, error = [], [], None

        try:
            submission = translator.to_sql(instring=self.submission,
                                           schema=schema,
                                           use_bag_semantics=use_bag)
            solution = translator.to_sql(instring=self.problem.solution,
                                         schema=schema,
                                         use_bag_semantics=use_bag)
        except ParseException as e:
            error = 'Syntax error at line {lineno} column {col}:  \'{line}\''\
                .format(lineno=e.lineno, col=e.col, line=e.line)

        except TreeBRDError as e:
            error = e

        return submission, solution, error


class TestRun(AbstractTestRun):
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def get_history(self):
        return {
            'visible': False,
            'input': '',
            'output': '',
            'passed': self.test_passed,
            'description': str(self.testcase)
        }

# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)

post_delete.connect(problem_delete, sender=Problem)