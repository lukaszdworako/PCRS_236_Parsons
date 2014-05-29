from django import test
from django.core.urlresolvers import reverse
from problems.tests import TestProblemSubmissionGradesBeforeDeadline, \
    TestBestSubmission

from problems_multiple_choice.models import (Problem, Submission, Option,
                                             OptionSelection)
from tests.ViewTestMixins import (CourseStaffViewTestMixin,
                                  ProtectedViewTestMixin, UsersMixin)


class TestProblemListView(ProtectedViewTestMixin, test.TestCase):
    """
    Test accessing the problem list page.
    """
    url = reverse('mc_problem_list')
    template = 'problem_list'
    model = Problem


class TestProblemCreateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a problem.
    """
    url = reverse('mc_problem_create')
    successful_redirect_url = reverse('mc_problem_list')
    template = 'problem'
    model = Problem

    def setUp(self):
        CourseStaffViewTestMixin.setUp(self)
        self.post_data = {
            'description': 'test_problem',
            'visibility': 'closed'
        }

    def test_create_problem(self):
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.description)

    def test_create_problem_no_question_text(self):
        del(self.post_data['description'])
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(0, self.model.objects.count())


class TestProblemUpdateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing a problem with no submissions.
    """
    url = reverse('mc_problem_update', kwargs={'pk': 1})
    successful_redirect_url = reverse('mc_problem_list')
    template = 'problem'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(
            pk=1, description='test_problem', visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        self.post_data = {
            'description': 'test_problem',
            'visibility': 'draft'
        }

    def test_change_question(self):
        self.post_data['description'] = 'new'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new', object.description)

    def test_change_no_question(self):
        self.post_data['description'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.description)


class TestProblemUpdateViewWithSubmissions(TestProblemUpdateView):
    """
    Test editing a problem with submissions.
    """
    def setUp(self):
        TestProblemUpdateView.setUp(self)
        Submission.objects.create(problem=self.object, user=self.student,
                                  section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def tearDown(self):
        self.assertTrue(self.object.submission_set.exists())


class TestProblemClearView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test clearing submissions.
    """
    url = reverse('mc_problem_clear', kwargs={'pk': 1})
    successful_redirect_url = reverse('mc_problem_update', kwargs={'pk': 1})
    template = 'problems/submission_check_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, description='test_problem',
                                                visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.object, user=self.student,
                                  section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def test_clear(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(self.object.submission_set.exists())


class TestProblemDeleteView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test deleting a problem.
    """
    url = reverse('mc_problem_delete', kwargs={'pk': 1})
    successful_redirect_url = reverse('mc_problem_list')
    template = 'problems/problem_check_delete.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(
            pk=1, description='test_problem', visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.problem, user=self.student,
                                  section=self.section, score=0)
        self.assertTrue(self.problem.submission_set.exists())

    def test_delete(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(self.problem.submission_set.exists())
        self.assertFalse(self.model.objects.exists())

    def test_delete_with_options(self):
        Option(pk=1, problem=self.problem, answer_text='42').save()
        Option(pk=1, problem=self.problem, answer_text='42').save()

        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.problem.submission_set.exists())
        self.assertFalse(self.problem.option_set.exists())
        self.assertFalse(self.model.objects.exists())


class TestProblemAddOptionView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding an option with no submissions.
    """
    url = reverse('mc_problem_add_option', kwargs={'problem': 1})
    successful_redirect_url = reverse('mc_problem_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(
            pk=1, description='test_problem', visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

    def test_add_correct(self):
        post_data = {
            'answer_text': 'answer1',
            'is_correct': 'on',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('answer1', option.answer_text)
        self.assertTrue(option.is_correct)

    def test_add_incorrect(self):
        post_data = {
            'answer_text': 'answer1',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('answer1', option.answer_text)
        self.assertFalse(option.is_correct)

    def test_add_multiple(self):
        post_data = {
            'answer_text': 'answer1',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('answer1', option.answer_text)
        self.assertFalse(option.is_correct)

        post_data = {
            'answer_text': 'answer2',
            'is_correct': 'on',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(2, self.problem.option_set.count())
        option1, option2 = self.problem.option_set.all()
        self.assertEqual(1, option1.problem.pk)
        self.assertEqual('answer1', option1.answer_text)
        self.assertFalse(option1.is_correct)
        self.assertEqual(1, option2.problem.pk)
        self.assertEqual('answer2', option2.answer_text)
        self.assertTrue(option2.is_correct)

    def test_add_with_invalid_problem_get(self):
        url = reverse('mc_problem_add_option', kwargs={'problem': 100})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_add_with_invalid_problem_post(self):
        url = reverse('mc_problem_add_option', kwargs={'problem': 100})
        post_data = {
            'answer_text': '=(',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_add_with_no_answer(self):
        post_data = {
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'answer_text',
                             'This field is required.')


class TestProblemAddOptionViewWithSubmissions(CourseStaffViewTestMixin,
                                              test.TestCase):
    """
    Test adding an option with submissions.
    """
    url = reverse('mc_problem_add_option', kwargs={'problem': 1})
    successful_redirect_url = reverse('mc_problem_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(
            pk=1, description='test_problem', visibility='draft')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.problem, user=self.student,
                                  section=self.section, score=0)
        self.assertTrue(self.problem.submission_set.exists())

    def test_add_correct(self):
        post_data = {
            'answer_text': 'answer1',
            'is_correct': 'on',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, self.problem.option_set.count())
        self.assertFormError(response, 'form', 'is_correct',
            'Submissions must be cleared before changing an option.')

    def test_add_incorrect(self):
        post_data = {
            'answer_text': 'answer1',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('answer1', option.answer_text)
        self.assertFalse(option.is_correct)

    def test_add_with_invalid_problem_get(self):
        url = reverse('mc_problem_add_option', kwargs={'problem': 100})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_add_with_invalid_problem_post(self):
        url = reverse('mc_problem_add_option', kwargs={'problem': 100})
        post_data = {
            'answer_text': '=(',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_add_with_no_answer(self):
        post_data = {
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'answer_text',
                             'This field is required.')


class TestOptionUpdateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing an option with no submissions.
    """
    url = reverse('mc_problem_update_option',
                  kwargs={'problem': 1, 'pk': 1})
    successful_redirect_url = reverse('mc_problem_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(
            pk=1, description='test_problem', visibility='draft')
        Option(pk=1, problem=self.problem, answer_text='42').save()
        self.assertTrue(self.problem.option_set.exists())

        CourseStaffViewTestMixin.setUp(self)

    def test_make_correct(self):
        post_data = {
            'pk': 1,
            'answer_text': '42',
            'is_correct': 'on',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('42', option.answer_text)
        self.assertTrue(option.is_correct)

    def test_make_incorrect(self):
        option = Option.objects.get(pk=1)
        option.is_correct = True
        option.save()
        self.assertTrue(option.is_correct)

        post_data = {
            'pk': 1,
            'answer_text': '42',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('42', option.answer_text)
        self.assertFalse(option.is_correct)

    def test_edit_text(self):
        post_data = {
            'answer_text': '43',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('43', option.answer_text)
        self.assertFalse(option.is_correct)

    def test_edit_with_no_answer(self):
        post_data = {
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'answer_text',
                             'This field is required.')

    def test_edit_with_invalid_problem_get(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 100, 'pk': 1})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_problem_post(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 100, 'pk': 1})
        post_data = {
            'answer_text': '=(',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_option_get(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 1, 'pk': 100})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_option_post(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 1, 'pk': 100})
        post_data = {
            'answer_text': '=(',
            'pk': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)


class TestUpdateOptionViewWithSubmissions(CourseStaffViewTestMixin,
                                          test.TestCase):
    """
    Test editing an option with submissions.
    """
    url = reverse('mc_problem_update_option',
                  kwargs={'problem': 1, 'pk': 1})
    successful_redirect_url = reverse('mc_problem_update', kwargs={'pk': 1})
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(
            pk=1, description='test_problem', visibility='draft')

        Option(pk=1, problem=self.problem, answer_text='42').save()
        self.assertTrue(self.problem.option_set.exists())

        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.problem, user=self.student,
                                  section=self.section, score=0)
        self.assertTrue(self.problem.submission_set.exists())

    def test_make_correct(self):
        post_data = {
            'pk': 1,
            'answer_text': '42',
            'is_correct': 'on',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('42', option.answer_text)
        self.assertFalse(option.is_correct)
        self.assertFormError(response, 'form', 'is_correct',
            'Submissions must be cleared before changing an option.')

    def test_make_incorrect(self):
        option = Option.objects.get(pk=1)
        option.is_correct = True
        option.save()
        self.assertTrue(option.is_correct)

        post_data = {
            'pk': 1,
            'answer_text': '42',
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('42', option.answer_text)
        self.assertTrue(option.is_correct)
        self.assertFormError(response, 'form', 'is_correct',
            'Submissions must be cleared before changing an option.')

    def test_edit_text(self):
        post_data = {
            'pk': 1,
            'answer_text': '43',
            'problem': 1
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.problem.option_set.count())
        option = self.problem.option_set.all()[0]
        self.assertEqual(1, option.problem.pk)
        self.assertEqual('43', option.answer_text)
        self.assertFalse(option.is_correct)

    def test_edit_with_no_answer(self):
        post_data = {
            'problem': 1,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertFormError(response, 'form', 'answer_text',
                             'This field is required.')

    def test_edit_with_invalid_problem_get(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 100, 'pk': 1})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_problem_post(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 100, 'pk': 1})
        post_data = {
            'answer_text': '=(',
            'problem': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_option_get(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 1, 'pk': 100})
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_edit_with_invalid_option_post(self):
        url = reverse('mc_problem_update_option',
                      kwargs={'problem': 1, 'pk': 100})
        post_data = {
            'answer_text': '=(',
            'pk': 100
        }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)


class TestDeleteOptionView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test deleting an option.
    """
    url = reverse('mc_problem_delete_option', kwargs={'problem': 1, 'pk': 1})
    successful_redirect_url = reverse('mc_problem_update', kwargs={'pk': 1})
    template = 'problems/check_delete.html'

    def setUp(self):
        self.problem = Problem.objects.create(pk=1, description='test_problem',
                                              visibility='draft')

        Option(pk=1, problem=self.problem, answer_text='42').save()
        self.assertTrue(self.problem.option_set.exists())

        CourseStaffViewTestMixin.setUp(self)

    def test_delete_no_submissions(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(OptionSelection.objects.filter(option_id=1).exists())

    def test_delete_with_submissions(self):
        Submission.objects.create(problem=self.problem, user=self.student,
                                  section=self.section, score=0)

        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(OptionSelection.objects.filter(option_id=1).exists())
        self.assertEqual(1, Submission.objects.filter(problem_id=1).count())


class TestScoreUpdate(UsersMixin, test.TestCase):
    """
    Test updating the score on submission when an option is deleted.
    """
    def setUp(self):
        UsersMixin.setUp(self)

        self.problem = Problem.objects.create(pk=1, description='test_problem')
        self.o1 = Option.objects.create(pk=1, problem=self.problem,
                                        answer_text='42', is_correct=True)
        self.o2 = Option.objects.create(pk=2, problem=self.problem,
                                        answer_text='43')

    def test_change(self):
        submission = Submission.objects.create(section=self.section,
                                               user=self.student,
                                               problem=self.problem,
                                               score=2, pk=1)
        OptionSelection.objects.create(option=self.o1, submission=submission,
                                       is_correct=True)
        OptionSelection.objects.create(option=self.o2, submission=submission,
                                       is_correct=True)
        self.o2.delete()
        self.assertFalse(OptionSelection.objects.filter(option=self.o2).exists())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

    def test_no_change(self):
        submission = Submission.objects.create(section=self.section,
                                               user=self.student,
                                               problem=self.problem,
                                               score=1, pk=1)
        OptionSelection.objects.create(option=self.o1, submission=submission,
                                       is_correct=True)
        OptionSelection.objects.create(option=self.o2, submission=submission,
                                       is_correct=False)
        self.o2.delete()
        self.assertFalse(OptionSelection.objects.filter(option=self.o2).exists())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)


class TestProblemAddSubmission(ProtectedViewTestMixin, test.TestCase):
    """
    Test submitting a solution to a problem.
    """
    url = reverse('mc_problem_submit', kwargs={'problem': 1})
    successful_redirect_url = url

    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(
            pk=1, description='description', visibility='open')

        self.o1 = Option.objects.create(pk=1, problem=self.problem,
                                        answer_text='42', is_correct=True)
        self.o2 = Option.objects.create(pk=2, problem=self.problem,
                                        answer_text='43')
        self.assertEqual(2, Option.objects.count())


        ProtectedViewTestMixin.setUp(self)

    def test_add_submission_nothing_selected(self):
        post_data = {
            'problem': '1',
            'user': self.student.username,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'problems/submission.html')

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

        self.assertEqual(2, OptionSelection.objects.count())
        o1, o2 = OptionSelection.objects.all()

        self.assertEqual(1, o1.option.pk)
        self.assertFalse(o1.is_correct)

        self.assertEqual(2, o2.option.pk)
        self.assertTrue(o2.is_correct)

    def test_add_submission_all_selected(self):
        post_data = {
            'problem': '1',
            'user': self.student.username,
            'options': ['1', '2']
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'problems/submission.html')

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

        self.assertEqual(2, OptionSelection.objects.count())
        o1, o2 = OptionSelection.objects.all()

        self.assertEqual(1, o1.option.pk)
        self.assertTrue(o1.is_correct)

        self.assertEqual(2, o2.option.pk)
        self.assertFalse(o2.is_correct)

    def test_completely_wrong(self):
        post_data = {
            'problem': '1',
            'user': self.student.username,
            'options': ['2']
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'problems/submission.html')

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(0, submission.score)

        self.assertEqual(2, OptionSelection.objects.count())
        o1, o2 = OptionSelection.objects.all()

        self.assertEqual(1, o1.option.pk)
        self.assertFalse(o1.is_correct)

        self.assertEqual(2, o2.option.pk)
        self.assertFalse(o2.is_correct)

    def test_completely_correct(self):
        post_data = {
            'problem': '1',
            'user': self.student.username,
            'options': ['1']
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'problems/submission.html')

        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(2, submission.score)

        self.assertEqual(2, OptionSelection.objects.count())
        o1, o2 = OptionSelection.objects.all()

        self.assertEqual(1, o1.option.pk)
        self.assertTrue(o1.is_correct)

        self.assertEqual(2, o2.option.pk)
        self.assertTrue(o2.is_correct)


class TestGrading(TestProblemSubmissionGradesBeforeDeadline, test.TestCase):
    problem_class = Problem
    submission_class = Submission

    def setUp(self):
        super().setUp()
        self.problem = self.problem_class.objects.create(description='Q1')
        self.problem2 = self.problem_class.objects.create(description='Q2')


class TestBestSubmissionCode(TestBestSubmission, UsersMixin, test.TestCase):
    """
    Test updating best submission per student.

    Note: submissions are sorted in descending order by timestamp.
    """
    def setUp(self):
        super().setUp()
        self.Submission = Submission
        self.problem = Problem.objects.create(pk=1, description='Q1',
                                              visibility='open')