from json import dumps
from unittest import skip
from django import test
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from problems_ra.models import Problem, Submission, TestCase, TestRun

from problems_rdb.models import Dataset, Schema
from ViewTestMixins import ProtectedViewTestMixin, CourseStaffViewTestMixin


class TestProblemListView(ProtectedViewTestMixin, test.TestCase):
    url = reverse('ra_problem_list')
    template = 'problems_ra/Problem_list'


@override_settings(RDB_DATABASE='crs_data_test')
class TestProblemCreateView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('ra_problem_create')
    template = 'problems/problem_form.html'

    def setUp(self):

        schema = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        dataset = 'INSERT INTO WEATHER VALUES(true, 15);'

        self.schema = Schema(pk=1, name='test_schema', definition=schema,
                             tables=dumps({'weather': ['sunny', 'temp']}))
        self.schema.save()
        self.schema2 = Schema.objects.create(pk=2, name='test_schema2',
                                             definition=schema)
        self.dataset = Dataset(pk=1, name='test_ds', definition=dataset,
                               schema=self.schema)

        CourseStaffViewTestMixin.setUp(self)

        self.post_data = {
            'name': 'test_ra_problem',
            'description': 'test_ra_problem_desc',
            'solution': 'weather;',
            'schema': '1',
            'grammar': Problem.GRAMMARS[0][0],
            'semantics': Problem.SEMANTICS[0][0]
        }

    def test_ra_problem_creation(self):
        """
        Creating a new RA problem with correct details.
        """

        response = self.client.post(self.url, self.post_data)

        # problem was added with correct details
        problems = Problem.objects.all()
        self.assertEqual(1, problems.count())
        problem = problems[0]
        self.assertEqual('test_ra_problem', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('weather;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertFalse(problem.visibility)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

    def form_invalid(self, response):
        # Problem was not created.
        self.assertEqual(0, Problem.objects.count())

        # User redirected back to the form
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_ra_problem_creation_with_no_name(self):
        """
        Creating a new RA problem with no name.
        """
        post_data = self.post_data.copy()
        post_data['name'] = ''
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'name',
                             'This field is required.')

    def test_ra_problem_creation_with_empty_solution(self):
        """
        Creating a new RA problem with no solution.
        """
        post_data = self.post_data.copy()
        post_data['solution'] = ''
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'solution',
                             'This field is required.')

    @skip('check ra solution')
    def test_ra_problem_creation_with_invalid_solution(self):
        """
        Creating a new RA problem with invalid solution.
        """
        post_data = self.post_data.copy()
        post_data['solution'] = 'invalid ra'
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'solution',
                             'Solution is invalid.')

    def test_ra_problem_creation_no_schema(self):
        """
        Creating a new RA problem with no schema.
        """
        post_data = self.post_data.copy()
        post_data['schema'] = ''
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'schema',
                             'This field is required.')

    def test_ra_problem_creation_schema_does_not_exist(self):
        """
        Creating a new RA problem with schema that does not exist.
        """
        post_data = self.post_data.copy()
        post_data['schema'] = '222'
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'schema',
                             'Select a valid choice. '
                             'That choice is not one of the available choices.')

    def test_ra_problem_creation_no_semantics(self):
        """
        Creating a new RA problem with no semantics.
        """
        post_data = self.post_data.copy()
        post_data['semantics'] = ''
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'semantics',
                             'This field is required.')

    def test_ra_problem_creation_semantics_does_not_exist(self):
        """
        Creating a new RA problem with semantics that does not exist.
        """
        post_data = self.post_data.copy()
        post_data['semantics'] = 'what?'
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'semantics',
                             'Select a valid choice. '
                             'what? is not one of the available choices.')

    def test_ra_problem_creation_no_grammar(self):
        """
        Creating a new RA problem with no grammar.
        """
        post_data = self.post_data.copy()
        post_data['grammar'] = ''
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'grammar',
                             'This field is required.')

    def test_ra_problem_creation_grammar_does_not_exist(self):
        """
        Creating a new RA problem with grammar that does not exist.
        """
        post_data = self.post_data.copy()
        post_data['grammar'] = 'what?'
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'grammar',
                             'Select a valid choice. '
                             'what? is not one of the available choices.')


@override_settings(RDB_DATABASE='crs_data_test')
class TestProblemUpdateViewWithNoSubmissions(CourseStaffViewTestMixin,
                                               test.TestCase):
    url = reverse('ra_problem_update', kwargs={'pk': 1})
    successful_redirect_url = url
    template = 'problems/problem_form.html'

    def setUp(self):
        self.valid_solution = 'weather;'
        self.problem = Problem.objects.create(
            pk=1, name='test_ra_problem', description='test_ra_problem_desc',
            solution=self.valid_solution, schema_id=1, visibility='draft',
            grammar=Problem.GRAMMARS[0][0], semantics=Problem.SEMANTICS[0][0])
        TestProblemCreateView.setUp(self)

        self.post_data = {
            'name':  'new_name',
            'description': 'test_ra_problem_desc',
            'solution': 'weather;',
            'schema': '1',
            'visibility': 'draft',
            'grammar': Problem.GRAMMARS[0][0],
            'semantics': Problem.SEMANTICS[0][0]
        }

    def test_ra_problem_edit_visibility(self):
        """
        Editing a RA problem visibility with no submissions.
        """
        self.assertTrue(Problem.objects.filter(pk=1).exists())
        self.post_data['visibility'] = 'closed'
        response = self.client.post(self.url, self.post_data)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('weather;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual('closed', problem.visibility)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_ra_problem_edit_schema(self):
        """
        Editing a RA problem schema with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        self.post_data['schema'] = '2'
        response = self.client.post(self.url, self.post_data)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('weather;', problem.solution)
        self.assertEqual(2, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_ra_problem_edit_solution(self):
        """
        Editing a RA problem solution with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        self.post_data['solution'] = 'weather; weather;'
        response = self.client.post(self.url, self.post_data)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('weather; weather;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_ra_problem_edit_grammar(self):
        """
        Editing a RA problem grammar with no submissions.
        """
        self.assertTrue(Problem.objects.filter(pk=1).exists())
        self.post_data['grammar'] = Problem.GRAMMARS[1][0]
        response = self.client.post(self.url, self.post_data)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('weather;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[1][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

        self.assertRedirects(response, self.successful_redirect_url)

    def test_ra_problem_edit_semantics(self):
        """
        Editing a RA problem semantics with no submissions.
        """

        self.assertTrue(Problem.objects.filter(pk=1).exists())
        self.post_data['semantics'] = Problem.SEMANTICS[1][0]
        response = self.client.post(self.url, self.post_data)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('weather;', problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[1][0], problem.semantics)

        self.assertRedirects(response, self.successful_redirect_url)


@override_settings(RDB_DATABASE='crs_data_test')
class TestProblemUpdateViewWithSubmissions(CourseStaffViewTestMixin,
                                              test.TestCase):
    url = reverse('ra_problem_update', kwargs={'pk': 1})
    template = 'problem_form'
    successful_redirect_url = url

    def setUp(self):
        TestProblemUpdateViewWithNoSubmissions.setUp(self)

        Submission.objects.create(
            pk=1, problem=self.problem, user=self.student, score=1,
            section=self.student.section, submission='submission1')

    def test_ra_problem_edit_with_submissions(self):
        """
        Editing a RA problem name and description when submissions exist.
        """
        self.post_data['name'] = 'new_name'
        self.post_data['description'] = 'new_desc'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('new_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

    def test_ra_problem_edit_visibility(self):
        """
        Editing a RA problem visibility with submissions.
        """
        self.post_data['visibility'] = 'open'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        # problem details were updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('new_name', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual('open', problem.visibility)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

    def test_ra_problem_edit_schema(self):
        """
        Editing a RA problem schema when submissions exist.
        """
        self.post_data['schema'] = '2'
        response = self.client.post(self.url, self.post_data)
        # user redirected back to the form
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertFormError(response, 'form', 'schema',
                             'Submissions must be cleared.')

        # problem details were not updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_ra_problem', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

    def test_ra_problem_edit_solution(self):
        """
        Editing a RA problem solution when submissions exist.
        """
        self.post_data['solution'] = 'weather; weather;'
        response = self.client.post(self.url, self.post_data)
        # user redirected back to the form
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertFormError(response, 'form', 'solution',
                             'Submissions must be cleared.')

        # problem details were not not updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_ra_problem', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

    def test_ra_problem_edit_grammar(self):
        """
        Editing a RA problem grammar with submissions.
        """
        self.post_data['grammar'] = Problem.GRAMMARS[1][0]
        response = self.client.post(self.url, self.post_data)
        self.assertFormError(response, 'form', 'grammar',
                             'Submissions must be cleared.')

        # problem details were not updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_ra_problem', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)

    def test_ra_problem_edit_semantics(self):
        """
        Editing a RA problem semantics with submissions.
        """
        self.post_data['semantics'] = Problem.SEMANTICS[1][0]
        response = self.client.post(self.url, self.post_data)
        self.assertFormError(response, 'form', 'semantics',
                             'Submissions must be cleared.')

        # problem details were not updated
        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)
        problem = problems[0]
        self.assertEqual('test_ra_problem', problem.name)
        self.assertEqual('test_ra_problem_desc', problem.description)
        self.assertEqual(self.valid_solution, problem.solution)
        self.assertEqual(1, problem.schema.pk)
        self.assertEqual(Problem.GRAMMARS[0][0], problem.grammar)
        self.assertEqual(Problem.SEMANTICS[0][0], problem.semantics)