from django import test
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase

from problems.tests.test_best_attempt_before_deadline import *
from problems.tests.test_performance import TestSubmissionHistoryDatabaseHits
from problems_parsons.models import Problem, TestCase, Submission, TestRun
from ViewTestMixins import ProtectedViewTestMixin, \
    CourseStaffViewTestMixin, UsersMixin


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
        self.assertEqual('0', object.evaluation_type)

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
        self.assertEqual('0', object.evaluation_type)
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
        self.assertEqual('0', object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)
    
    def test_make_visible(self):
        self.post_data['visibility'] = 'open'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new_name', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('open', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual('0', object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)

    def test_edit_evaluation_type(self):
        self.post_data['evaluation_type'] = '2'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new_name', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('open', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual('2', object.evaluation_type)
        self.assertEqual('def function(a,b,c):\n  a = a+b\n  b = b+c<br>c = a+b\n  return (a,b,c)', object.starter_code)

    def test_edit_starter_code(self):
        self.post_data['starter_code'] = 'def function(a,b,c):\n  a = a+b\n  b = b+c\n  c = a+b\n  return (a,b,c)'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new_name', object.name)
        self.assertEqual('test_desc', object.description)
        self.assertEqual('open', object.visibility)
        self.assertEqual('problem_invariant', object.invariant)
        self.assertEqual('2', object.evaluation_type)
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