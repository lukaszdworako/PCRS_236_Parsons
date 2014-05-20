from django import test
from django.core.urlresolvers import reverse

from problems.tests import TestProblemSubmissionGradesBeforeDeadline
from problems_code.models import Problem, TestCase, Submission, TestRun
from tests.ViewTestMixins import (CourseStaffViewTestMixin,
                                  ProtectedViewTestMixin, UsersMixin)


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
            student=self.student, section=self.section, score=0)
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
            student=self.student, section=self.section, score=0)
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
            student=self.student, section=self.section, score=0)
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
            student=self.student, section=self.section, score=0)
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
            student=self.student, section=self.section, score=0)
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
        Submission.objects.create(problem=self.problem, student=self.student,
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
            'student': self.student
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
            'student': self.student,
            'section': self.section.pk
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

        # and submit again
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(2, Submission.objects.count())
        submission1, submission2 = Submission.objects.all()
        self.assertEqual('my awesome submission', submission1.submission)
        self.assertEqual(0, submission1.score)
        self.assertEqual('my awesome submission', submission2.submission)
        self.assertEqual(0, submission2.score)

        self.assertEqual(2, TestRun.objects.count())
        testrun1, testrun2 = TestRun.objects.all()
        self.assertEqual(1, testrun1.testcase.pk)
        self.assertFalse(testrun1.test_passed)
        self.assertEqual(1, testrun2.testcase.pk)
        self.assertFalse(testrun2.test_passed)

    def test_add_valid_python(self):
        code = 'def foo(val):\n    return val'
        post_data = {
            'problem': '1',
            'submission': code,
            'student': self.student.username
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(code, submission.submission)
        self.assertEqual(1, submission.score)

        self.assertEqual(1, TestRun.objects.count())
        testrun = TestRun.objects.all()[0]
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
        self.submission = Submission(section=self.section, student=self.student,
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
    problem_class = Problem
    submission_class = Submission

    def setUp(self):
        super().setUp()
        self.problem = self.problem_class.objects.create(pk=1, name='Problem1',
                                                         visibility='open')
        self.problem2 = self.problem_class.objects.create(pk=2, name='Problem2',
                                                          visibility='opne')