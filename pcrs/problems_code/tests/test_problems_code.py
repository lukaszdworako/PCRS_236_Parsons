from django import test
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase

from problems.tests.test_best_attempt_before_deadline import *
from problems.tests.test_performance import TestSubmissionHistoryDatabaseHits
from problems_code.models import Problem, TestCase, Submission, TestRun
from ViewTestMixins import ProtectedViewTestMixin, \
    CourseStaffViewTestMixin, UsersMixin


class TestCodingProblemListView(ProtectedViewTestMixin, test.TestCase):
    """
    Test accessing the problem list page.
    """
    url = reverse('coding_problem_list')
    template = 'problem_list'
    model = Problem


class TestCodingProblemCreateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a problem.
    """
    url = reverse('coding_problem_create')
    successful_redirect_url = reverse('coding_problem_list')
    template = 'problem'
    model = Problem

    def setUp(self):
        CourseStaffViewTestMixin.setUp(self)
        self.post_data = {
            'name': 'test_problem',
            'description': 'test_desc',
            'language': 'python',
            'visibility': 'closed'
        }

    def test_create_problem(self):
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('', object.solution)
        self.assertEqual('closed', object.visibility)

    def test_create_problem_no_name(self):
        del(self.post_data['name'])
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(0, self.model.objects.count())


class TestCodingProblemUpdateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing a problem with no submissions.
    """
    url = reverse('coding_problem_update', kwargs={'pk': 1})
    successful_redirect_url = reverse('coding_problem_list')
    template = 'problem'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        self.post_data = {
            'name': 'test_problem',
            'description': 'solve_this',
            'language': 'python',
            'visibility': 'closed'
        }

    def test_add_description(self):
        self.post_data['description'] = 'test_desc'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('', object.solution)
        self.assertEqual('closed', object.visibility)

    def test_change_name(self):
        self.post_data['name'] = 'new_name'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new_name', object.name)
        self.assertEqual('solve_this', object.description)
        self.assertEqual('', object.solution)
        self.assertEqual('closed', object.visibility)

    def test_add_solution(self):
        self.post_data['solution'] = 'solution'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('solve_this', object.description)
        self.assertEqual('solution', object.solution)
        self.assertEqual('closed', object.visibility)

    def test_edit_solution(self):
        self.object.solution = 'old_solution'
        self.object.save()
        self.assertEqual('old_solution', self.object.solution)

        self.post_data['solution'] = 'new_solution'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('solve_this', object.description)
        self.assertEqual('new_solution', object.solution)
        self.assertEqual('closed', object.visibility)

    def test_make_visible(self):
        self.post_data['visibility'] = 'open'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('solve_this', object.description)
        self.assertEqual('', object.solution)
        self.assertEqual('open', object.visibility)


class TestCodingProblemUpdateViewWithSubmissions(TestCodingProblemUpdateView):
    """
    Test editing a problem with submissions.
    """
    def setUp(self):
        TestCodingProblemUpdateView.setUp(self)
        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())


class TestCodingProblemClearView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test clearing submissions.
    """
    url = reverse('coding_problem_clear', kwargs={'pk': 1})
    successful_redirect_url = reverse('coding_problem_update', kwargs={'pk': 1})
    template = 'problems/submission_check_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def test_clear(self):
        post_data = {}
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.object.submission_set.exists())


class TestCodingProblemDeleteView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test deleting a problem.
    """
    url = reverse('coding_problem_delete', kwargs={'pk': 1})
    successful_redirect_url = reverse('coding_problem_list')
    template = 'problems/problem_check_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def test_delete_no_testcases(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.object.submission_set.exists())
        self.assertFalse(self.model.objects.exists())

    def test_delete_with_testcases(self):
        TestCase(problem=self.object, test_input='question',
                 expected_output='42').save()
        TestCase(problem=self.object, test_input='42',
                 expected_output='42').save()

        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.object.submission_set.exists())
        self.assertFalse(self.object.testcase_set.exists())
        self.assertFalse(self.model.objects.exists())


class TestCodingProblemAddTestcaseView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a testcase with no submissions.
    """
    url = reverse('coding_problem_add_testcase', kwargs={'problem': 1})
    sussessful_redirect_url = reverse('coding_problem_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

    def test_add_minimal(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.sussessful_redirect_url)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('', testcase.description)
        self.assertFalse(testcase.is_visible)

    def test_add_full(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 1,
            'description': 'desc',
            'is_visible': 'on'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.sussessful_redirect_url)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('desc', testcase.description)
        self.assertTrue(testcase.is_visible)

    def test_add_with_invalid_problem_get(self):
        url = reverse('coding_problem_add_testcase', kwargs={'problem': 100})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_add_with_invalid_problem_post(self):
        url = reverse('coding_problem_add_testcase', kwargs={'problem': 100})
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_add_with_no_input(self):
        post_data = {
            'expected_output': '42',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'test_input',
                             'This field is required.')

    def test_add_with_no_output(self):
        post_data = {
            'test_input': 'question',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'expected_output',
                             'This field is required.')


class TestCodingProblemAddTestcaseViewWithSubmissions(CourseStaffViewTestMixin,
                                                      test.TestCase):
    """
    Test adding a testcase with submissions.
    """
    url = reverse('coding_problem_add_testcase', kwargs={'problem': 1})
    template = 'testcase'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='draft')
        self.assertTrue(self.model.objects.filter(pk=1).exists())
        TestCase.objects.create(test_input='question', expected_output='42',
                                pk=1, problem=self.problem)
        self.assertTrue(TestCase.objects.filter(pk=1).exists())

        CourseStaffViewTestMixin.setUp(self)
        Submission.objects.create(problem=self.problem,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.problem.submission_set.exists())

    def test_add(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 1
        }
        response = self.client.get(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response,
            'Submissions must be cleared before adding a testcase.')
        self.assertEqual(1, self.problem.testcase_set.count())


class TestUpdateTestcaseView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing a testcase with no submissions.
    """
    url = reverse('coding_problem_update_testcase',
                  kwargs={'problem': 1, 'pk': 1})
    successful_redirect_url = reverse('coding_problem_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='draft')
        self.problem2 = self.model.objects.create(pk=2, name='test_problem2',
                                                  visibility='draft')
        TestCase.objects.create(test_input='question', expected_output='42',
                                pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)

    def test_edit_input(self):
        post_data = {
            'test_input': 'the question',
            'expected_output': '42',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('the question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('', testcase.description)
        self.assertFalse(testcase.is_visible)

    def test_edit_output(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '43',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('43', testcase.expected_output)
        self.assertEqual('', testcase.description)
        self.assertFalse(testcase.is_visible)

    def test_edit_description_visibility(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 1,
            'description': 'desc',
            'is_visible': 'on'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('desc', testcase.description)
        self.assertTrue(testcase.is_visible)

    def test_edit_problem(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 2,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)

        self.assertFormError(response, 'form', 'problem',
                             'Reassigning a problem is not allowed.')

    def test_edit_with_invalid_problem_get(self):
        url = reverse('coding_problem_update_testcase',
                      kwargs={'problem': 100, 'pk': 1})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_problem_post(self):
        url = reverse('coding_problem_update_testcase',
                      kwargs={'problem': 100, 'pk': 1})
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_edit_with_no_input(self):
        post_data = {
            'expected_output': '42',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'test_input',
                             'This field is required.')

    def test_edit_with_no_output(self):
        post_data = {
            'test_input': 'question',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'expected_output',
                             'This field is required.')


class TestUpdateTestcaseViewWithSubmissions(CourseStaffViewTestMixin,
                                                      test.TestCase):
    """
    Test adding an testcase with submissions.
    """
    url = reverse('coding_problem_update_testcase',
                  kwargs={'problem': 1, 'pk': 1})
    successful_redirect_url = reverse('coding_problem_update', kwargs={'pk': 1})
    template = 'testcase'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='draft')
        self.problem2 = self.model.objects.create(pk=2, name='test_problem2',
                                                  visibility='draft')
        TestCase.objects.create(test_input='question', expected_output='42',
                                pk=1, problem=self.problem)

        CourseStaffViewTestMixin.setUp(self)
        Submission.objects.create(problem=self.problem,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.problem.submission_set.exists())

    def test_edit_description_visibility(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 1,
            'description': 'desc',
            'is_visible': 'on'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('desc', testcase.description)
        self.assertTrue(testcase.is_visible)

    def test_edit_input(self):
        post_data = {
            'test_input': 'the question',
            'expected_output': '42',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('', testcase.description)
        self.assertFalse(testcase.is_visible)

        self.assertFormError(response, 'form', 'test_input',
                    'Submissions must be cleared before editing a testcase.')

    def test_edit_output(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '43',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)
        self.assertEqual('', testcase.description)
        self.assertFalse(testcase.is_visible)

        self.assertFormError(response, 'form', 'expected_output',
                    'Submissions must be cleared before editing a testcase.')

    def test_edit_problem(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 2,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, self.problem.testcase_set.count())
        testcase = self.problem.testcase_set.all()[0]
        self.assertEqual('question', testcase.test_input)
        self.assertEqual('42', testcase.expected_output)

        self.assertFormError(response, 'form', 'problem',
                             'Reassigning a problem is not allowed.')

    def test_edit_with_invalid_problem_get(self):
        url = reverse('coding_problem_update_testcase',
                      kwargs={'problem': 100, 'pk': 1})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_problem_post(self):
        url = reverse('coding_problem_update_testcase',
                      kwargs={'problem': 100, 'pk': 1})
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_edit_with_no_input(self):
        post_data = {
            'expected_output': '42',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'test_input',
                             'This field is required.')

    def test_edit_with_no_output(self):
        post_data = {
            'test_input': 'question',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'expected_output',
                             'This field is required.')


class TestDeleteTestcaseView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test deleting a testcase.
    """
    url = reverse('coding_problem_delete_testcase', kwargs={'problem': 1, 'pk': 1})
    successful_redirect_url = reverse('coding_problem_update', kwargs={'pk': 1})
    template = 'problems/check_delete.html'

    def setUp(self):
        self.problem = Problem.objects.create(pk=1, name='test_problem',
                                              visibility='draft')

        TestCase(pk=1, problem=self.problem, test_input='question',
                 expected_output='42').save()
        self.assertTrue(self.problem.testcase_set.exists())

        CourseStaffViewTestMixin.setUp(self)

    def test_delete_no_submissions(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(TestRun.objects.filter(testcase_id=1).exists())

    def test_delete_with_submissions(self):
        Submission.objects.create(problem=self.problem, user=self.student,
                                  section=self.section, score=0)

        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(TestRun.objects.filter(testcase_id=1).exists())
        self.assertEqual(1, Submission.objects.filter(problem_id=1).count())


class TestCodingProblemAddSubmission(ProtectedViewTestMixin, test.TestCase):
    """
    Test submitting a solution to a coding problem.
    """
    url = reverse('coding_problem_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
        TestCase.objects.create(test_input='foo(True)', expected_output='True',
                                pk=1, problem=self.problem)

        CourseStaffViewTestMixin.setUp(self)

    def test_add_submission(self):
        post_data = {
            'problem': '1',
            'submission': 'my awesome submission',
            'user': self.student
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual('my awesome submission', submission.submission)
        self.assertEqual(0, submission.score)

        self.assertEqual(1, TestRun.objects.count())
        testrun = TestRun.objects.all()[0]
        self.assertEqual(1, testrun.testcase.pk)
        self.assertFalse(testrun.test_passed)

    def test_add_submissions(self):
        post_data = {
            'problem': '1',
            'submission': 'my awesome submission',
            'user': self.student,
            'section': self.section.pk
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual('my awesome submission', submission.submission)
        self.assertEqual(0, submission.score)
        self.assertTrue(submission.has_best_score)

        self.assertEqual(1, TestRun.objects.count())
        testrun = TestRun.objects.all()[0]
        self.assertEqual(1, testrun.testcase.pk)
        self.assertFalse(testrun.test_passed)

        # and submit again
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(2, Submission.objects.count())
        submission2, submission1 = Submission.objects.all()
        self.assertEqual('my awesome submission', submission1.submission)
        self.assertEqual(0, submission1.score)
        self.assertEqual('my awesome submission', submission2.submission)
        self.assertEqual(0, submission2.score)
        # self.assertFalse(submission1.has_best_score)
        self.assertTrue(submission2.has_best_score)

        self.assertEqual(2, TestRun.objects.count())
        testrun1, testrun2 = TestRun.objects.all()
        self.assertEqual(1, testrun1.testcase.pk)
        self.assertFalse(testrun1.test_passed)
        self.assertEqual(1, testrun2.testcase.pk)
        self.assertFalse(testrun2.test_passed)

    def test_add_valid_python(self):
        post_data = {
            'problem': '1',
            'submission': 'submission',
            'user': self.student,
            'section': self.section.pk
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual('submission', submission.submission)
        self.assertEqual(0, submission.score)
        self.assertTrue(submission.has_best_score)

        # and submit again with bteeter score

        code = 'def foo(val):\n    return val'
        post_data = {
            'problem': '1',
            'submission': code,
            'user': self.student.username
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(2, Submission.objects.count())
        submission1 = Submission.objects.filter(submission='submission')[0]
        submission2 = Submission.objects\
                      .filter(submission='def foo(val):\n    return val')[0]
        self.assertEqual(code, submission2.submission)
        self.assertEqual(1, submission2.score)
        self.assertFalse(submission1.has_best_score)
        self.assertTrue(submission2.has_best_score)

        self.assertEqual(2, TestRun.objects.count())
        testrun = TestRun.objects.filter(submission=submission2)[0]
        self.assertEqual(1, testrun.testcase.pk)
        self.assertTrue(testrun.test_passed)


class TestScoreUpdate(UsersMixin, test.TestCase):
    """
    Test updating the score on submission when a testcase is deleted.
    """
    def setUp(self):
        UsersMixin.setUp(self)

        self.problem = Problem.objects.create(pk=1, name='test_problem')
        self.t1 = TestCase.objects.create(pk=1, problem=self.problem,
                                          test_input='question',
                                          expected_output='42')
        self.t2 = TestCase.objects.create(pk=2, problem=self.problem,
                                          test_input='2+2', expected_output='4')
        self.submission = Submission(section=self.section, user=self.student,
                                     submission='sub', problem=self.problem,
                                     score=1, pk=1)
        self.submission.save()
        TestRun.objects.create(testcase=self.t1, submission=self.submission,
                               test_passed=True)
        TestRun.objects.create(testcase=self.t2, submission=self.submission,
                               test_passed=False)

    def test_no_change(self):
        self.t2.delete()
        self.assertFalse(TestRun.objects.filter(testcase=self.t2).exists())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

    def test_change(self):
        self.t1.delete()
        self.assertFalse(TestRun.objects.filter(testcase=self.t1).exists())
        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(0, submission.score)


class TestGrading(TestProblemSubmissionGradesBeforeDeadline, test.TestCase):
    """
    Test problem grading method.
    """
    problem_class = Problem
    submission_class = Submission

    def setUp(self):
        super().setUp()
        self.problem = self.problem_class.objects.create(pk=1, name='Problem1',
                                                         visibility='open')
        self.problem2 = self.problem_class.objects.create(pk=2, name='Problem2',
                                                          visibility='open')


class TestBestSubmissionCode(TestBestSubmission, UsersMixin, test.TestCase):
    """
    Test updating best submission per student.

    Note: submissions are sorted in descending order by timestamp.
    """
    def setUp(self):
        super().setUp()
        self.Submission = Submission
        self.problem = Problem.objects.create(pk=1, name='Problem1',
                                              visibility='open')


class TestSolvedBeforeDeadline(TestSingleChallengeQuest, test.TestCase):
    """
    Test calculating the number of problems solved in Challenge.
    """
    problem_class = Problem
    submission_class = Submission

    def test_no_problems_in_challenge(self):
        """
        The problem is not in the Challenge.
        """
        p1 = self.problem_class.objects.create(name='p1', description='p1')
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=p1, score=4)
        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=p1, score=1)
        Submission.objects.create(submission='subm', user=self.student2,
                                  problem=p1, score=1)

        with self.assertNumQueries(2):
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student2))

    def test_one_problem_in_challenge(self):
        """
        The problem is in the Challenge.
        One student solved it, and the other did not.
        """
        p1 = self.problem_class.objects.create(name='p1', description='p1',
                                               challenge=self.challenge)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')

        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=p1, score=4)
        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=p1, score=1)
        Submission.objects.create(submission='subm', user=self.student2,
                                  problem=p1, score=1)

        with self.assertNumQueries(2):
            self.assertEqual({1: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student2))

    def test_one_problem_outside_Challenge_solved(self):
        """
        One problem is in the Challenge, multiple submissions,
        including submissions to a problem not in Challenge.
        """
        p1 = self.problem_class.objects.create(name='p1', description='p1',
                                               challenge=self.challenge)
        p2 = self.problem_class.objects.create(name='p2', description='p2')
        p3 = self.problem_class.objects.create(name='p3', description='p3')
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')

        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=p1, score=3)
        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=p1, score=1)
        Submission.objects.create(submission='subm', user=self.student2,
                                  problem=p2, score=4)

        with self.assertNumQueries(1):
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))

    def test_two_problem_in_challenge_solved(self):
        p1 = self.problem_class.objects.create(name='p1', description='p1',
                                               challenge=self.challenge)
        p2 = self.problem_class.objects.create(name='p2', description='p2',
                                               challenge=self.challenge)
        p3 = self.problem_class.objects.create(name='p3', description='p3')
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
        for i in range(2):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')

        for i in range(3):
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2]:
            for problem in [p1, p2, p3]:
                for score in [2, 0, 1, 4, 0]:
                    self.submission_class.objects.create(submission='subm',
                        user=user, problem=problem, score=score)

        with self.assertNumQueries(1):
            self.assertEqual({1: 2},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))


class TestSolvedBeforeDeadlineChallenges(
    TestNumberSolvedBeforeDeadlineChallenges, test.TestCase):
    def test_one_problem_in_one_challenge(self):
        """
        Test one problem solved in one Challenge and 0 in another.
        """
        p1 = Problem.objects.create(name='p1', description='p1', challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2', challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3', challenge=self.challenge2)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2, self.student3]:
            for problem in [p1, p2, p3]:
                for score in [2, 0, 1, 3, 0]:
                    Submission.objects.create(submission='subm',
                        user=user, problem=problem, score=score)

        with self.assertNumQueries(1):
            self.assertEqual({2: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))

    def test_all_problem_in_one_challenge(self):
        """
        Test both problems solved in one Challenge and 0 in another.
        """
        p1 = Problem.objects.create(name='p1', description='p1', challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2', challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3', challenge=self.challenge2)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2, self.student3]:
            for problem in [p1, p2, p3]:
                for score in [2, 0, 1, 3, 0]:
                    Submission.objects.create(submission='subm',
                        user=user, problem=problem, score=score)

        with self.assertNumQueries(1):
            self.assertEqual({2: 2},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))

    def test_one_problem_in_all_challenges(self):
        """
        Test one problem solved in each Challenge.
        """
        p1 = Problem.objects.create(name='p1', description='p1', challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2', challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3', challenge=self.challenge2)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2, self.student3]:
            Submission.objects.create(submission='subm',
                user=user, problem=p1, score=1)
            Submission.objects.create(submission='subm',
                user=user, problem=p1, score=4)
            Submission.objects.create(submission='subm',
                user=user, problem=p2, score=3)
            Submission.objects.create(submission='subm',
                user=user, problem=p3, score=1)

        with self.assertNumQueries(1):
            self.assertEqual({1: 1, 2: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))

    def test_all_problem_in_all_challenges(self):
        """
        Test all problems solved in all Challenges.
        """
        p1 = Problem.objects.create(name='p1', description='p1', challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2', challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3', challenge=self.challenge2)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2, self.student3]:
            for problem in [p1, p2, p3]:
                for score in [2, 0, 4, 3, 0]:
                    Submission.objects.create(submission='subm',
                        user=user, problem=problem, score=score)

        with self.assertNumQueries(1):
            self.assertEqual({1: 1, 2: 2},
                Submission.get_completed_for_challenge_before_deadline(self.student1))


class TestSolvedBeforeDeadlines(TestNumberSolvedBeforeDeadlines, test.TestCase):
    """
    Test the number of problems solved in each Challenge with varying deadlines
    for sections.
    """
    def test_all_problems_in_all_challenges(self):
        """
        Submissions by all students were made at the same time,
        but the deadline for some students has passed
        """
        p1 = Problem.objects.create(name='p1', description='p1',
                                    challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2',
                                    challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3',
                                    challenge=self.challenge2)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2, self.student3]:
            for problem in [p1, p2, p3]:
                for score in [2, 0, 4, 3, 0]:
                    Submission.objects.create(submission='subm',
                        user=user, problem=problem, score=score)

        with self.assertNumQueries(3):
            self.assertEqual({1: 1, 2: 2},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student2))
            self.assertEqual({},
                            Submission.get_completed_for_challenge_before_deadline(self.student3))

    def test_some_after_deadline(self):
        """
        Some submissions were made after the deadline for the students section.
        """
        p1 = Problem.objects.create(name='p1', description='p1',
                                    challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2',
                                    challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3',
                                    challenge=self.challenge2)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for student in [self.student1, self.student2]:
            for problem in [p1, p2]:
                for score in [2, 0, 4, 4, 0]:
                    s = Submission.objects.create(submission='subm',
                            user=student, problem=problem, score=score)
                    s.timestamp = now() - timedelta(days=8)
                    s.save()

        with self.assertNumQueries(5):
            self.assertEqual({1: 1, 2: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))
            Submission.objects.create(submission='subm', user=self.student1, problem=p3, score=3)
            self.assertEqual({1: 1, 2: 2},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))

            Submission.objects.create(submission='subm', user=self.student2, problem=p3, score=3)
            self.assertEqual({1: 1, 2: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student2))


class TestNumberSolvedQuestsCode(TestManyQuestsDeadlines, test.TestCase):
    """
    Test the number of problems solved in each Challenge with varying deadlines
    for sections and multiple Quests.
    """
    def test_all_problems_in_all_challenges(self):
        """
        Submissions by all students were made at the same time,
        but the deadline for some students has passed
        """
        p1 = Problem.objects.create(name='p1', description='p1',
                                    challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2',
                                    challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3',
                                    challenge=self.challenge3)
        p4 = Problem.objects.create(name='p4', description='p4',
                                    challenge=self.challenge4)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p4, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for user in [self.student1, self.student2, self.student3]:
            for problem in [p1, p2, p3, p4]:
                for score in [2, 0, 4, 3, 0]:
                    Submission.objects.create(submission='subm',
                        user=user, problem=problem, score=score)

        with self.assertNumQueries(3):
            self.assertEqual({1: 1, 2: 1, 3: 1, 4: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student2))
            self.assertEqual({},
                             Submission.get_completed_for_challenge_before_deadline(self.student3))

    def test_some_after_deadline(self):
        """
        Some submissions were made after the deadline for the students section.
        """
        p1 = Problem.objects.create(name='p1', description='p1',
                                    challenge=self.challenge)
        p2 = Problem.objects.create(name='p2', description='p2',
                                    challenge=self.challenge2)
        p3 = Problem.objects.create(name='p3', description='p3',
                                    challenge=self.challenge3)
        p4 = Problem.objects.create(name='p4', description='p4',
                                    challenge=self.challenge4)
        for i in range(4):
            TestCase.objects.create(problem=p1, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p4, test_input='1',
                                    expected_output='2')
        for i in range(3):
            TestCase.objects.create(problem=p2, test_input='1',
                                    expected_output='2')
            TestCase.objects.create(problem=p3, test_input='1',
                                    expected_output='2')

        for student in [self.student1, self.student2]:
            for problem in [p1, p2, p3, p4]:
                for score in [2, 0, 4, 4, 2]:
                    s = Submission.objects.create(submission='subm',
                            user=student, problem=problem, score=score)
                    s.timestamp = now() - timedelta(days=8)
                    s.save()

        with self.assertNumQueries(6):
            self.assertEqual({1: 1, 4: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))
            self.assertEqual({1: 1, 4: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student2))

            Submission.objects.create(submission='subm', user=self.student1, problem=p3, score=3)
            self.assertEqual({1: 1, 3: 1, 4: 1},
                             Submission.get_completed_for_challenge_before_deadline(self.student1))

            Submission.objects.create(submission='subm', user=self.student2, problem=p3, score=3)
            self.assertEqual({1: 1, 4: 1, },
                             Submission.get_completed_for_challenge_before_deadline(self.student2))


class TestBestCodeAttemptSingleProblem(TestSingleChallengeQuest, test.TestCase):
    """
    Test getting the best attempts for a single problem.
    """

    def setUp(self):
        TestSingleChallengeQuest.setUp(self)
        self.problem = Problem.objects.create(pk=1, name='p1', description='p1',
                                              challenge=self.challenge)
        for i in range(4):
            TestCase.objects.create(problem=self.problem, test_input='1',
                                    expected_output='2')

    def test_single_submission(self):
        Submission.objects.create(submission='subm', user=self.student1,
                                  problem=self.problem, score=3)
        actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
        self.assertEqual({1: 3}, actual)

    def test_many_submission(self):
        for score in [2, 3, 0, 1]:
            Submission.objects.create(submission='subm', user=self.student1,
                                      problem=self.problem, score=score)
        actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
        self.assertEqual({1: 3}, actual)

    def test_best_after_deadline(self):
        for score in [2, 3, 0, 1]:
            Submission.objects.create(submission='subm', user=self.student1,
                                      problem=self.problem, score=score)
        s = Submission.objects.create(submission='subm', user=self.student1,
                                      problem=self.problem, score=4)
        s.timestamp = localtime(now()) + timedelta(days=10)
        s.save()
        actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
        self.assertEqual({1: 3}, actual)


class TestBestCodeAttemptManyProblem(TestManyQuestsDeadlines, test.TestCase):
    """
    Test getting the best attempts for multiple problems
    across many Challenges.
    """

    def setUp(self):
        TestManyQuestsDeadlines.setUp(self)

        # there are 2 students, 2 quests, each with two challenges.
        # students are enrolled in 2 different sections - deadline for student1
        # is a week from now, and the deadline for student 2 is a week ago

        # add two problems to each challenge
        challenges = [self.challenge, self.challenge2,
                      self.challenge3, self.challenge4]
        for i in range(4):
            problem = Problem.objects.create(pk=i, name=str(i), description='p',
                                             challenge=challenges[i])
            for j in range(4):
                TestCase.objects.create(problem=problem, test_input='1',
                                        expected_output='2')
            problem = Problem.objects.create(pk=i+4, name=str(i+4), description='p',
                                             challenge=challenges[i])
            for j in range(2):
                TestCase.objects.create(problem=problem, test_input='1',
                                        expected_output='2')

    def test_not_all_attempted(self):
        for problem_pk in [0, 6]:
            # one problem attempted in two challenges
            for student in [self.student1, self.student2]:
                Submission.objects.create(submission='subm', user=student,
                                          problem_id=problem_pk, score=1)
        with self.assertNumQueries(2):
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
            self.assertEqual({0: 1, 6: 1}, actual)

            # second student submission deadline has passed
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student2)
            self.assertEqual({}, actual)

    def test_best_for_student(self):
        for student in [self.student1, self.student2]:
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=1, score=0)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=1, score=2)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=1, score=1)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=2, score=0)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=6, score=1)

        with self.assertNumQueries(2):
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
            self.assertEqual({1: 2, 2: 0, 6: 1}, actual)

            # second student submission deadline has passed
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student2)
            self.assertEqual({}, actual)

    def test_best_for_student_with_best_after_deadline(self):
        for student in [self.student1, self.student2]:
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=1, score=0)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=1, score=2)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=1, score=1)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=2, score=0)
            Submission.objects.create(submission='subm', user=student,
                                      problem_id=6, score=1)
        # all submissions made before the deadlines for both sections
        Submission.objects.update(timestamp=localtime(now()) - timedelta(days=10))

        with self.assertNumQueries(2):
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
            self.assertEqual({1: 2, 2: 0, 6: 1}, actual)
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student2)
            self.assertEqual({1: 2, 2: 0, 6: 1}, actual)

        # adding a submission by student 2 that came after their deadline
        Submission.objects.create(submission='subm', user=self.student2,
                                  problem_id=6, score=4)
        with self.assertNumQueries(2):
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student1)
            self.assertEqual({1: 2, 2: 0, 6: 1}, actual)
            actual, _ = Submission.get_best_attempts_before_deadlines(self.student2)
            self.assertEqual({1: 2, 2: 0, 6: 1}, actual)


class TestSubmissionHistory(TestSubmissionHistoryDatabaseHits, UsersMixin,
                            TransactionTestCase):

    url = reverse('coding_problem_async_history', kwargs={'problem': 1})

    def setUp(self):
        UsersMixin.setUp(self)

        quest = Quest.objects.create(name='1', description='1')
        SectionQuest.objects.filter(section=self.student.section).update(due_on=localtime(now()))

        challenge = Challenge.objects.create(name='1', description='1', quest=quest, visibility='open')

        self.problem = Problem.objects.create(pk=1, name='1', description='1',
                                              visibility='open', challenge=challenge)
        TestCase.objects.bulk_create(
            [TestCase(problem=self.problem, test_input=1, expected_output=2)
             for i in range(6)])

        scores = [1, 2, 0, 5, 1, 0, 3]
        for score in scores:
            sub = Submission.objects.create(problem=self.problem,
                                            user=self.student, score=score)
            sub.set_best_submission()
            for case in TestCase.objects.all():
                TestRun.objects.create(submission=sub, testcase=case, test_passed=False)

        self.assertEqual(len(scores), Submission.objects.count())
        self.assertEqual(len(scores)*6, TestRun.objects.count())