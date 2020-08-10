from django import test
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase

from problems.tests.test_best_attempt_before_deadline import *
from problems.tests.test_performance import TestSubmissionHistoryDatabaseHits
from problems_parsons.models import Problem, TestCase, Submission, TestRun
from tests.ViewTestMixins import ProtectedViewTestMixin, \
    CourseStaffViewTestMixin, UsersMixin
import json


class TestParsonsProblemListView(ProtectedViewTestMixin, test.TestCase):
    """
    Test accessing the problem list page.
    """
    url = reverse('parsons_list')
    template = 'problem_list'
    model = Problem


class TestParsonsProblemCreateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a problem.
    """
    url = reverse('parsons_create')
    successful_redirect_url = reverse('parsons_list')
    template = 'problem'
    model = Problem

    def setUp(self):
        CourseStaffViewTestMixin.setUp(self)
        self.post_data = {
            'name'              :'test_problem',
            'description'       :'test_desc',
            'visibility'        :'closed',
            'starter_code'      :'def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)',
            'evaluation_type'   :'0',
            'invariant'         :'problem_invariant'
        }

    def test_create_problem(self):
        response = self.client.post(self.url, self.post_data)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('closed', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)
        self.assertEqual(['0'], object.evaluation_type)

    def test_create_problem_no_name(self):
        del(self.post_data['name'])
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(0, self.model.objects.count())

    def test_create_problem_no_evaluation_type(self):
        del(self.post_data['evaluation_type'])
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(0, self.model.objects.count())

class TestParsonsProblemUpdateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing a problem with no submissions.
    """
    url = reverse('parsons_update', kwargs={'pk': 1})
    successful_redirect_url = url
    template = 'problem'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem', visibility='open')
        CourseStaffViewTestMixin.setUp(self)

        self.post_data = {
            'name'              :'test_problem',
            'description'       :'test_desc',
            'visibility'        :'closed',
            'starter_code'      :'def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)',
            'evaluation_type'   :'0',
            'invariant'         :'problem_invariant'
        }

    def test_add_description(self):
        self.post_data['description'] = 'test_desc'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('closed', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual(['0'], object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)

    def test_change_name(self):
        self.post_data['name'] = 'new_name'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new_name', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('closed', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual(['0'], object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)
    
    def test_make_visible(self):
        self.post_data['visibility'] = 'open'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('open', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual(['0'], object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)

    def test_edit_evaluation_type(self):
        self.post_data['evaluation_type'] = '2'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('closed', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual(['2'], object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)

    def test_edit_starter_code(self):
        self.post_data['starter_code'] = 'def function(a,b,c):\n  a = a+b\n  b = b+c\n  c = a+b\n  return (a,b,c)'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('closed', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual(['0'], object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c\n  c = a+b\n  return (a,b,c)', object.starter_code)

class TestParsonsProblemUpdateViewWithSubmission(TestParsonsProblemUpdateView):
    """
    Test editing a problem with submissions.
    """
    def setUp(self):
        TestParsonsProblemUpdateView.setUp(self)
        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

class TestParsonsProblemClearView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test clearing submissions.
    """
    url = reverse('parsons_clear', kwargs={'pk': 1})
    successful_redirect_url = reverse('parsons_update', kwargs={'pk': 1})
    template = 'problems/submission_check_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='open')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def test_clear(self):
        post_data = {}
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.object.submission_set.exists())

class TestParsonsProblemDeleteView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test deleting a problem.
    """
    url = reverse('parsons_delete', kwargs={'pk': 1})
    successful_redirect_url = reverse('parsons_list')
    template = 'problems/problem_check_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='open')
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

class TestparsonsAddTestcaseView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a testcase with no submissions.
    """
    url = reverse('coding_problem_add_testcase', kwargs={'problem': 1})
    successful_redirect_url = reverse('parsons_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem', visibility='open')
        CourseStaffViewTestMixin.setUp(self)

    def test_add_minimal(self):
        post_data = {
            'test_input': 'question',
            'expected_output': '42',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

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
        self.assertRedirects(response, self.successful_redirect_url)

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

class TestparsonsAddTestcaseViewWithSubmissions(CourseStaffViewTestMixin,
                                                      test.TestCase):
    """
    Test adding a testcase with submissions.
    """
    url = reverse('coding_problem_add_testcase', kwargs={'problem': 1})
    template = 'testcase'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
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
    successful_redirect_url = reverse('parsons_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
        self.problem2 = self.model.objects.create(pk=2, name='test_problem2',
                                                  visibility='open')
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
    successful_redirect_url = reverse('parsons_update', kwargs={'pk': 1})
    template = 'testcase'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
        self.problem2 = self.model.objects.create(pk=2, name='test_problem2',
                                                  visibility='open')
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
    successful_redirect_url = reverse('parsons_update', kwargs={'pk': 1})
    template = 'problems/check_delete.html'

    def setUp(self):
        self.problem = Problem.objects.create(pk=1, name='test_problem',
                                              visibility='open')

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

class TestParsonsProblemAddSubmission(ProtectedViewTestMixin, test.TestCase):
    """
    Test submitting a solution to a coding problem.
    """
    url = reverse('parsons_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem
    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem', visibility='open', evaluation_type='2', starter_code="def foo(uinp):\n\treturn uinp", max_score=1)
        TestCase.objects.create(test_input='foo(True)', expected_output='True', pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)
    
    def test_add_submission(self):
        post_data = {
            'submission': "[{\"code\": \"my awesome submission\", \"indent\":0}]"
        }

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual('my awesome submission\n', submission.submission)
        self.assertEqual(0, submission.score)

        self.assertEqual(1, TestRun.objects.count())
        testrun = TestRun.objects.all()[0]
        self.assertEqual(1, testrun.testcase.pk)
        self.assertFalse(testrun.test_passed)

    def test_add_submissions(self):
        post_data = {
            'submission': "[{\"code\": \"my awesome submission\", \"indent\":0}]"
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual('my awesome submission\n', submission.submission)
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
        self.assertEqual('my awesome submission\n', submission1.submission)
        self.assertEqual(0, submission1.score)
        self.assertEqual('my awesome submission\n', submission2.submission)
        self.assertEqual(0, submission2.score)
        self.assertTrue(submission2.has_best_score)

        self.assertEqual(2, TestRun.objects.count())
        testrun1, testrun2 = TestRun.objects.all()
        self.assertEqual(1, testrun1.testcase.pk)
        self.assertFalse(testrun1.test_passed)
        self.assertEqual(1, testrun2.testcase.pk)
        self.assertFalse(testrun2.test_passed)
        

    def test_valid_submission(self):
        submit_1 = "[{\"code\": \"my awesome submission\", \"indent\":0}]"
        submit_1_back = "my awesome submission\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual('my awesome submission\n', submission.submission)
        self.assertEqual(0, submission.score)
        self.assertTrue(submission.has_best_score)

        self.assertEqual(1, TestRun.objects.count())
        testrun = TestRun.objects.all()[0]
        self.assertEqual(1, testrun.testcase.pk)
        self.assertFalse(testrun.test_passed)
        self.assertEqual(1, Submission.objects.count())

        # and now, we submit with an actually valid input
        submit_2 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":1}]"
        submit_2_back = "def foo(uinp):\n\treturn uinp\n"
        post_data = {
            'submission': submit_2
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(2, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        submission2 = Submission.objects.filter(submission=submit_2_back)[0]
        self.assertEqual(1, submission2.score)
        self.assertFalse(submission1.has_best_score)
        self.assertTrue(submission2.has_best_score)

        self.assertEqual(2, TestRun.objects.count())
        testrun = TestRun.objects.filter(submission=submission2)[0]
        self.assertEqual(1, testrun.testcase.pk)
        self.assertTrue(testrun.test_passed)

    def test_wrong_order_still_execute(self):

        # and now, we submit with an actually valid input
        submit_1 = "[{\"code\":\"return uinp\", \"indent\":0}, {\"code\":\"def foo(uinp):\", \"indent\":1}]"
        submit_1_back = "return uinp\n\tdef foo(uinp):\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(1, TestRun.objects.count())
        # 5 because we are still going to run the tests
        self.assertEqual(5, submission1.reason_incorrect)


class TestParsonsProblemGradingLines(ProtectedViewTestMixin, test.TestCase):
    """
    Test submitting a solution to a coding problem.
    """
    url = reverse('parsons_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem
    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem', visibility='open', evaluation_type='1', starter_code="def foo(uinp):\n\treturn uinp", max_score=1)
        TestCase.objects.create(test_input='foo(True)', expected_output='True', pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)
    
    def test_correct_submission(self):
        # and now, we submit with an actually valid input
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":1}]"
        submit_1_back = "def foo(uinp):\n\treturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(1, submission1.score)
        self.assertEqual(0, submission1.reason_incorrect)

    def test_wrong_indent(self):
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":0}]"
        submit_1_back = "def foo(uinp):\nreturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(4, submission1.reason_incorrect)
        
        # due to complications of indents, cannot allow misindented from counting in pure line comparison
        submit_2 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":2}]"
        submit_2_back = "def foo(uinp):\n\t\treturn uinp\n"
        post_data = {
            'submission': submit_2
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_2_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(2, Submission.objects.count())
        submission2 = Submission.objects.filter(submission=submit_2_back)[0]
        self.assertEqual(0, submission2.score)
        self.assertEqual(4, submission2.reason_incorrect)
        
    def test_too_few_lines(self):
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}]"
        submit_1_back = "def foo(uinp):\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(2, submission1.reason_incorrect)

    def test_too_many_lines(self):
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"extra_line()\", \"indent\":1}, {\"code\":\"return uinp\", \"indent\":1}]"
        submit_1_back = "def foo(uinp):\n\textra_line()\n\treturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(1, submission1.reason_incorrect)

    def test_special_case_br_lines(self):
        # and now, we submit with an actually valid input
        submit_1 = r'[{"code":"def foo(uinp):<br>\treturn uinp", "indent":0}]'
        submit_1_back = "def foo(uinp):\n\treturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(1, submission1.score)
        self.assertEqual(0, submission1.reason_incorrect)

class TestParsonsProblemGradingTestCase(ProtectedViewTestMixin, test.TestCase):
    """
    Test submitting a solution to a coding problem.
    """
    url = reverse('parsons_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem
    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem', visibility='open', evaluation_type='2', starter_code="def foo(uinp):\n\treturn uinp", max_score=1)
        TestCase.objects.create(test_input='foo(True)', expected_output='True', pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)

    def test_correct_submission(self):
        # and now, we submit with an actually valid input
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":1}]"
        submit_1_back = "def foo(uinp):\n\treturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(1, submission1.score)
        self.assertEqual(0, submission1.reason_incorrect)

    def test_wrong_indent(self):
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":0}]"
        submit_1_back = "def foo(uinp):\nreturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(5, submission1.reason_incorrect)
        
        # due to complications of indents, cannot allow misindented from counting in pure line comparison
        submit_2 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"return uinp\", \"indent\":2}]"
        submit_2_back = "def foo(uinp):\n\t\treturn uinp\n"
        post_data = {
            'submission': submit_2
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_2_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(2, Submission.objects.count())
        submission2 = Submission.objects.filter(submission=submit_2_back)[0]
        self.assertEqual(1, submission2.score)
        self.assertEqual(0, submission2.reason_incorrect)
        
    def test_too_few_lines(self):
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}]"
        submit_1_back = "def foo(uinp):\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(5, submission1.reason_incorrect)

    def test_too_many_lines(self):
        submit_1 = "[{\"code\":\"def foo(uinp):\", \"indent\":0}, {\"code\":\"extra_line()\", \"indent\":1}, {\"code\":\"return uinp\", \"indent\":1}]"
        submit_1_back = "def foo(uinp):\n\textra_line()\n\treturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(0, submission1.score)
        self.assertEqual(5, submission1.reason_incorrect)

    def test_special_case_br_lines(self):
        # and now, we submit with an actually valid input
        submit_1 = r'[{"code":"def foo(uinp):<br>\treturn uinp", "indent":0}]'
        submit_1_back = "def foo(uinp):\n\treturn uinp\n"
        post_data = {
            'submission': submit_1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        submission = Submission.objects.all()[0]
        self.assertEqual(submit_1_back, submission.submission)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission1 = Submission.objects.filter(submission=submit_1_back)[0]
        self.assertEqual(1, submission1.score)
        self.assertEqual(0, submission1.reason_incorrect)

class TestParsonsProblemGradingMixed(TestParsonsProblemGradingTestCase):
    """
    Test submitting a solution to a coding problem.
    """
    url = reverse('parsons_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem
    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem', visibility='open', evaluation_type='0', starter_code="def foo(uinp):\n\treturn uinp", max_score=1)
        TestCase.objects.create(test_input='foo(True)', expected_output='True', pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)
        

class TestSubmissionHistory(TestSubmissionHistoryDatabaseHits, UsersMixin,
                            TransactionTestCase):

    url = reverse('parsons_async_history', kwargs={'problem': 1})

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