from django import test
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from problems_rdb.models import Dataset, Schema

from problems_sql.models import Problem, Submission, TestCase, TestRun
from ViewTestMixins import ProtectedViewTestMixin, CourseStaffViewTestMixin


class TestProblemListView(ProtectedViewTestMixin, test.TestCase):
    url = reverse('sql_problem_list')
    template = 'problems_sql/sqlproblem_list'


@override_settings(RDB_DATABASE='crs_data_test')
class TestSQLProblemCreateView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('sql_problem_create_and_add_testcase')
    successful_redirect_url = reverse('sql_problem_add_testcase',
        kwargs={'problem': 1})
    template = 'problem_form'

    def setUp(self):

        schema = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        dataset = 'INSERT INTO WEATHER VALUES(true, 15);'

        self.schema = Schema.objects.create(pk=1, name='test_schema',
            definition=schema)
        self.schema2 = Schema.objects.create(pk=2, name='test_schema2',
            definition=schema)
        self.dataset = Dataset(pk=1, name='test_ds', definition=dataset,
            schema=self.schema)

        CourseStaffViewTestMixin.setUp(self)

    def test_sql_problem_creation(self):
        """
        Creating a new SQL problem with correct details.
        """

        valid_solution = 'SELECT * FROM WEATHER;'
        post_data = {
            'name': 'test_sql_problem',
            'description': 'test_sql_problem_desc',
            'solution': valid_solution,
            'schema': '1',
            'visibility': 'closed'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        # problem was added with correct details
        problems = Problem.objects.all()
        self.assertEqual(1, problems.count())
        problem = problems[0]
        self.assertEqual('test_sql_problem', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual('SELECT * FROM WEATHER;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual('closed', problem.visibility)
        self.assertFalse(problem.order_matters)

    def form_invalid(self, response):
        # Problem was not created.
        self.assertEqual(0, Problem.objects.count())

        # User redirected back to the form
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_sql_problem_creation_with_no_name(self):
        """
        Creating a new SQL problem with no name.
        """

        post_data = {
            'name': '',
            'description': 'test_sql_problem_desc',
            'solution': '',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'name',
            'This field is required.')

    def test_sql_problem_creation_with_no_solution(self):
        """
        Creating a new SQL problem with no solution.
        """

        post_data = {
            'name': 'test_sql_problem',
            'description': 'test_sql_problem_desc',
            'solution': '',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'solution',
            'This field is required.')

    def test_sql_problem_creation_with_invalid_solution(self):
        """
        Creating a new SQL problem with invalid solution.
        """

        post_data = {
            'name': 'test_sql_problem',
            'description': 'test_sql_problem_desc',
            'solution': 'not a valid sql query',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        # self.assertFormError(response, 'form', 'solution',
        #     'Solution is invalid.')

    def test_sql_problem_creation_no_solution(self):
        """
        Creating a new SQL problem with no solution.
        """

        post_data = {
            'name': 'test_sql_problem',
            'description': 'test_sql_problem_desc',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'solution',
            'This field is required.')

    def test_sql_problem_creation_no_schema(self):
        """
        Creating a new SQL problem with no schema.
        """

        post_data = {
            'name': 'test_sql_problem',
            'description': 'test_sql_problem_desc',
            'solution': 'test_sql_problem_solution',
            }
        response = self.client.post(self.url, post_data)

        self.form_invalid(response)
        self.assertFormError(response, 'form', 'schema',
            'This field is required.')

    def test_sql_problem_creation_schema_does_not_exist(self):
        """
        Creating a new SQL problem with schema that does not exist.
        """

        post_data = {
            'name': 'test_sql_problem',
            'description': 'test_sql_problem_desc',
            'solution': 'test_sql_problem_solution',
            'schema': '222'
        }
        response = self.client.post(self.url, post_data)

        self.form_invalid(response)
        self.assertFormError(response, 'form', 'schema',
            'Select a valid choice. '
            'That choice is not one of the available choices.')


@override_settings(RDB_DATABASE='crs_data_test')
class TestSQLProblemUpdateViewWithNoSubmissions(CourseStaffViewTestMixin,
                                                test.TestCase):
    url = reverse('sql_problem_update', kwargs={'pk': 1})
    successful_redirect_url = url

    template = 'problem_form'

    def setUp(self):
        self.valid_solution = 'SELECT * FROM WEATHER;'
        self.problem = Problem.objects.create(
            pk=1, name='test_sql_problem', description='test_sql_problem_desc',
            solution=self.valid_solution, schema_id=1, visibility='draft')
        TestSQLProblemCreateView.setUp(self)

    def test_sql_problem_edit_visibility(self):
        """
        Editing a SQL problem visibility with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': 'SELECT temp FROM WEATHER;',
            'schema': '1',
            'visibility': 'open'
        }
        response = self.client.post(self.url, post_data)

        problems = Problem.objects.all()

        # problem details were updated
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual('SELECT temp FROM WEATHER;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual('open', problem.visibility)
        self.assertFalse(problem.order_matters)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_sql_problem_edit_schema(self):
        """
        Editing a SQL problem schema with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': self.valid_solution,
            'schema': '2'
        }
        response = self.client.post(self.url, post_data)

        problems = Problem.objects.all()

        # problem details were updated
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(2, problem.schema.pk)
        self.assertFalse(problem.visibility)
        self.assertFalse(problem.order_matters)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_sql_problem_edit_solution(self):
        """
        Editing a SQL problem solution with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': 'SELECT temp FROM WEATHER;',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)

        problems = Problem.objects.all()

        # problem details were updated
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual('SELECT temp FROM WEATHER;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.visibility)
        self.assertFalse(problem.order_matters)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_sql_problem_edit_order(self):
        """
        Editing a SQL problem order_matters with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': 'SELECT temp FROM WEATHER;',
            'schema': '1',
            'order_matters': 'on'
        }
        response = self.client.post(self.url, post_data)

        problems = Problem.objects.all()

        # problem details were updated
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual('SELECT temp FROM WEATHER;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.visibility)
        self.assertTrue(problem.order_matters)

        self.assertRedirects(response, self.successful_redirect_url)


@override_settings(RDB_DATABASE='crs_data_test')
class TestSQLProblemUpdateViewWithSubmissions(CourseStaffViewTestMixin,
                                              test.TestCase):
    url = reverse('sql_problem_update', kwargs={'pk': 1})
    template = 'problem_form'
    successful_redirect_url = url

    def setUp(self):
        TestSQLProblemUpdateViewWithNoSubmissions.setUp(self)

        Submission.objects.create(
            pk=1, problem=self.problem, user=self.student, score=1,
            section=self.student.section, submission='submission1')

    def test_sql_problem_edit_with_submissions(self):
        """
        Editing a SQL problem name and description when submissions exist.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'new_desc',
            'solution': self.valid_solution,
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('new_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.visibility)
        self.assertFalse(problem.order_matters)

    def test_sql_problem_edit_visibility(self):
        """
        Editing a SQL problem visibility with submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': self.valid_solution,
            'schema': '1',
            'visibility': 'open'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual('open', problem.visibility)
        self.assertFalse(problem.order_matters)

    def test_sql_problem_edit_schema(self):
        """
        Editing a SQL problem schema when submissions exist.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': self.valid_solution,
            'schema': '2'
        }
        response = self.client.post(self.url, post_data)
        # user redirected back to the form
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertFormError(response, 'form', 'schema',
                             'Submissions must be cleared.')

        # problem details were not updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_sql_problem', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.order_matters)

    def test_sql_problem_edit_solution(self):
        """
        Editing a SQL problem solution when submissions exist.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': 'SELECT temp FROM WEATHER;',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        # user redirected back to the form
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertFormError(response, 'form', 'solution',
                             'Submissions must be cleared.')

        # problem details were not updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_sql_problem', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.order_matters)

    def test_sql_problem_edit_order(self):
        """
        Editing a SQL problem order_matters with submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        post_data = {
            'name':  'new_name',
            'description': 'test_sql_problem_desc',
            'solution': self.valid_solution,
            'schema': '1',
            'order_matters': 'on'
        }
        response = self.client.post(self.url, post_data)
        self.assertFormError(response, 'form', 'order_matters',
                             'Submissions must be cleared.')

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_sql_problem', problem.name)
        self.assertEqual('test_sql_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.order_matters)