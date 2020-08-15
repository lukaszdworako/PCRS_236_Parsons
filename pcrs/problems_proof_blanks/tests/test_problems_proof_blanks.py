from django import test
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.utils.timezone import localtime, now
from django.forms.models import model_to_dict
from problems.tests.test_best_attempt_before_deadline import TestBestSubmission, \
    TestProblemSubmissionGradesBeforeDeadline
from problems_proof_blanks.models import Problem, Feedback, Submission
from tests.ViewTestMixins import ProtectedViewTestMixin, \
    CourseStaffViewTestMixin, UsersMixin
from problems.tests.test_performance import TestSubmissionHistoryDatabaseHits
from content.models import Quest, SectionQuest, Challenge
import json

class TestCodingProblemListView(ProtectedViewTestMixin, test.TestCase):
    """
    Test accessing the problem list page.
    """
    url = reverse('proof_blanks_problem_list')
    template = 'problem_list'
    model = Problem

class TestProblemCreateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a problem.
    """
    url = reverse('proof_blanks_create')
    template = 'problem'
    model = Problem

    def setUp(self):
        CourseStaffViewTestMixin.setUp(self)
        self.post_data = {
            'name': ['test_problem'], 
            'proof_statement': ['proof statement'], 
            'incomplete_proof': ['proof'], 
            'answer_keys': ['{"1": "(a + b)", "2": "a^2 + 2ab + b^2"}'], 
            'notes': [''], 
            'author': [''], 
            'visibility': ['closed'], 
            'scaling_factor': ['1'], 
            'submit': ['Save']
        }
        

    def test_create_problem(self):
        response = self.client.post(self.url, self.post_data)

        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('proof statement', object.proof_statement)
        self.assertEqual('proof', object.incomplete_proof)
        self.assertEqual({"1": "(a + b)", "2": "a^2 + 2ab + b^2"}, object.answer_keys)
        self.assertEqual('closed', object.visibility)

    def test_create_problem_no_name(self):
        del(self.post_data['name'])
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(0, self.model.objects.count())
    
    def test_create_problem_only_name(self):
        del(self.post_data['answer_keys'])
        del(self.post_data['author'])
        del(self.post_data['notes'])
        response = self.client.post(self.url, self.post_data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, self.model.objects.count())
        problem = self.model.objects.all()[0]
        self.assertEqual(0, problem.max_score)

    

class TestProofBlanksProblemUpdateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing a problem with no submissions.
    """
    url = reverse('proof_blanks_update', kwargs={'pk': 1})
    successful_redirect_url = url
    template = 'problem'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='open')
        CourseStaffViewTestMixin.setUp(self)

        self.post_data = {
            'name': ['test_problem'], 
            'proof_statement': ['proof statement'], 
            'incomplete_proof': ['proof'], 
            'answer_keys': ['{"1": "(a + b)", "2": "a^2 + 2ab + b^2"}'], 
            'notes': [''], 
            'author': [''], 
            'visibility': ['closed'], 
            'scaling_factor': ['1'], 
            'submit': ['Save']
        }

    def test_change_proof_statement(self):
        self.post_data['proof_statement'] = 'test_desc'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('test_problem', object.name)
        self.assertEqual('test_desc', object.proof_statement)
        self.assertEqual('proof', object.incomplete_proof)
        self.assertEqual({"1": "(a + b)", "2": "a^2 + 2ab + b^2"}, object.answer_keys)
        self.assertEqual('closed', object.visibility)


    def test_change_name(self):
        self.post_data['name'] = 'new_name'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('new_name', object.name)
        self.assertEqual('proof statement', object.proof_statement)
        self.assertEqual('proof', object.incomplete_proof)
        self.assertEqual({"1": "(a + b)", "2": "a^2 + 2ab + b^2"}, object.answer_keys)
        self.assertEqual('closed', object.visibility)

    def test_add_answers(self):
        self.post_data['answer_keys'] = '{"1": "a", "2": "a^2 + 2ab + b^2"}'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual({"1": "a", "2": "a^2 + 2ab + b^2"}, object.answer_keys)
        self.assertEqual('test_problem', object.name)
        self.assertEqual('proof statement', object.proof_statement)
        self.assertEqual('proof', object.incomplete_proof)
        self.assertEqual('closed', object.visibility)


    def test_make_visible(self):
        self.post_data['visibility'] = 'open'
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, self.model.objects.count())
        object = self.model.objects.all()[0]
        self.assertEqual('open', object.visibility)
        self.assertEqual({"1": "(a + b)", "2": "a^2 + 2ab + b^2"}, object.answer_keys)
        self.assertEqual('test_problem', object.name)
        self.assertEqual('proof statement', object.proof_statement)
        self.assertEqual('proof', object.incomplete_proof)

class TestProofBlanksUpdateViewWithSubmissions(TestProofBlanksProblemUpdateView):
    """
    Test editing a problem with submissions.
    """
    def setUp(self):
        TestProofBlanksProblemUpdateView.setUp(self)
        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())


class TestProofBlanksClearView(CourseStaffViewTestMixin, test.TestCase):
    """
     Test clearing submissions.
    """
    url = reverse('proof_blanks_clear', kwargs={'pk': 1})
    successful_redirect_url = reverse('proof_blanks_update', kwargs={'pk': 1})
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

class TestProblemClearView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test clearing submissions.
    """
    url = reverse('proof_blanks_clear', kwargs={'pk': 1})
    successful_redirect_url = reverse('proof_blanks_update', kwargs={'pk': 1})
    template = 'problems/submission_check_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='open')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.object, user=self.student,
                                  section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def test_clear(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertFalse(self.object.submission_set.exists())


class TestProofBlanksDeleteView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test deleting a problem.
    """
    url = reverse('proof_blanks_delete', kwargs={'pk': 1})
    successful_redirect_url = reverse('proof_blanks_problem_list')
    template = 'problems/proof_blanks_delete.html'
    model = Problem

    def setUp(self):
        self.object = self.model.objects.create(pk=1, name='test_problem',
                                                visibility='open')
        CourseStaffViewTestMixin.setUp(self)

        Submission.objects.create(problem=self.object,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.object.submission_set.exists())

    def test_delete_no_feedback(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.object.submission_set.exists())
        self.assertFalse(self.model.objects.exists())

    def test_delete_with_feedback(self):
        Feedback(problem=self.object, feedback_keys={},
                 hint_keys={}).save()

        response = self.client.post(self.url, {})
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertFalse(self.object.submission_set.exists())
        self.assertFalse(self.object.feedback is None)
        self.assertFalse(self.model.objects.exists())


class TestProofBlanksAddFeedbackView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a testcase with no submissions.
    """
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
        self.url = "{}/feedback".format(self.problem.get_absolute_url())
        self.successful_redirect_url = "{}/feedback/1/".format(self.problem.get_absolute_url())
        CourseStaffViewTestMixin.setUp(self)

    def test_add_minimal(self):
        post_data = {
            'feedback_keys': ['{}'], 
            'hint_keys': ['{}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)
        feedback = self.problem.feedback
        self.assertEqual({}, feedback.feedback_keys)
        self.assertEqual({}, feedback.hint_keys)

    def test_add_full(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"}'''], 
            'hint_keys': ['{"1": "this is an int"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        feedback = self.problem.feedback
        self.assertEqual({"1": "{'type': 'int'}"}, feedback.feedback_keys)
        self.assertEqual({"1": "this is an int"}, feedback.hint_keys)

    def test_add_feedback_only(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"}'''], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        feedback = self.problem.feedback
        self.assertEqual({"1": "{'type': 'int'}"}, feedback.feedback_keys)
        self.assertIsNone(feedback.hint_keys)
    
    def test_add_hints_only(self):
        post_data = {
            'hint_keys': ['{"1": "this is an int"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        feedback = self.problem.feedback
        self.assertEqual({"1": "this is an int"}, feedback.hint_keys)
        self.assertIsNone(feedback.feedback_keys)



    def test_add_with_invalid_problem_get(self):
        url = "{}/100/feedback".format(self.problem.get_absolute_url()[:-2])
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)

    def test_add_with_invalid_problem_post(self):
        url = "{}/100/feedback".format(self.problem.get_absolute_url()[:-2])
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"'''], 
            'hint_keys': ['{"1": "this is an int"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(url, post_data)
        self.assertEqual(404, response.status_code)

class TestUpdateFeedbackView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test editing a testcase with no submissions.
    """
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
        self.problem2 = self.model.objects.create(pk=2, name='test_problem2',
                                                  visibility='open')
        self.url = self.successful_redirect_url = "{}/feedback/1/".format(self.problem.get_absolute_url())

        self.url2 = self.successful_redirect_url2 = "{}/feedback/2/".format(self.problem2.get_absolute_url())                                              
        Feedback.objects.create(hint_keys={"1": "this is an int"},feedback_keys={"1": "{'type': 'int'}"},
                                pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)

    def test_edit_feedback(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'mathexpr'}"}'''], 
            'hint_keys': ['{"1": "this is an int"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)
        feedback = self.problem.feedback
        feedback.refresh_from_db()
        self.assertEqual({"1": "{'type': 'mathexpr'}"}, feedback.feedback_keys)
        self.assertEqual({"1": "this is an int"}, feedback.hint_keys)

    def test_edit_hints(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"}'''], 
            'hint_keys': ['{"1": "this is a number"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)
        feedback = self.problem.feedback
        feedback.refresh_from_db()
        self.assertEqual({"1": "{'type': 'int'}"}, feedback.feedback_keys)
        self.assertEqual({"1": "this is a number"}, feedback.hint_keys)


    def test_edit_problem(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"}'''], 
            'hint_keys': ['{"1": "this is a number"}'], 
            'problem': ['2'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        # one to one relation so shouldn't work
        self.assertEqual(302, response.status_code)

    def test_edit_with_invalid_problem_get(self):
        url = "{}/100/feedback/100".format(self.problem.get_absolute_url()[:-2])
        response = self.client.get(url, {})
        self.assertEqual(404, response.status_code)
    
class TestUpdateFeedbackViewWithSubmissions(CourseStaffViewTestMixin,
                                                      test.TestCase):
    """
    Test adding an testcase with submissions.
    """
    template = 'problems/crispy_form.html'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem',
                                                 visibility='open')
        self.problem2 = self.model.objects.create(pk=2, name='test_problem2',
                                                  visibility='open')
        self.url = self.successful_redirect_url = "{}/feedback/1/".format(self.problem.get_absolute_url())

        self.url2 = self.successful_redirect_url2 = "{}/feedback/2/".format(self.problem2.get_absolute_url())                                              
        Feedback.objects.create(hint_keys={"1": "this is an int"},feedback_keys={"1": "{'type': 'int'}"},
                                pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)
        Submission.objects.create(problem=self.problem,
            user=self.student, section=self.section, score=0)
        self.assertTrue(self.problem.submission_set.exists())
    
    def test_edit_feedback(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'mathexpr'}"}'''], 
            'hint_keys': ['{"1": "this is an int"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)
        feedback = self.problem.feedback
        feedback.refresh_from_db()
        self.assertEqual({"1": "{'type': 'mathexpr'}"}, feedback.feedback_keys)
        self.assertEqual({"1": "this is an int"}, feedback.hint_keys)

    def test_edit_hints(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"}'''], 
            'hint_keys': ['{"1": "this is a number"}'], 
            'problem': ['1'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)
        feedback = self.problem.feedback
        feedback.refresh_from_db()
        self.assertEqual({"1": "{'type': 'int'}"}, feedback.feedback_keys)
        self.assertEqual({"1": "this is a number"}, feedback.hint_keys)


    def test_edit_problem(self):
        post_data = {
            'feedback_keys': ['''{"1": "{'type': 'int'}"}'''], 
            'hint_keys': ['{"1": "this is a number"}'], 
            'problem': ['2'], 
            'submit': ['Save']
            }
        response = self.client.post(self.url, post_data)
        # one to one relation so shouldn't work
        self.assertEqual(302, response.status_code)
    

class ProofBlanksAddSubmission(ProtectedViewTestMixin, test.TestCase):
    """
    Test submitting a solution to a coding problem.
    """
    url = reverse('proof_blanks_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem

    def setUp(self):
        self.problem = self.model.objects.create(pk=1, name='test_problem', answer_keys={"1": "string", 
        "2": "3", "3": "x", "4": "y", "5": "x * y"}, visibility='open')
        Feedback.objects.create(hint_keys={"1": "this is a string"}, feedback_keys={"2": "{'type': 'int', 'lambda x : x >= 3': 'correct'}", 
        "3": "{'type': 'mathexpr', 'map-variables': 'True'}",
        "4": "{'type': 'mathexpr', 'map-variables': 'True'}",
        "5": "{'type': 'mathexpr', 'map-variables': 'True'}"},
                                pk=1, problem=self.problem)
        CourseStaffViewTestMixin.setUp(self)

    def test_add_submission(self):
        post_data = {
            'problem': '1',
            'submission_1': ['string'],
            'user': self.student
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

    def test_add_submissions(self):
        post_data = {
            'problem': '1',
            'submission_1': ['string'],
            'user': self.student
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

        # submit again
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(2, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

    def test_int_function(self):
        post_data = {
            'problem': '1',
            'submission_2': ['3'],
            'user': self.student
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(1, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)

        # now with a value greater than 3
        post_data['submission_3'] = ['100']
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(2, Submission.objects.count())
        submission = Submission.objects.all()[0]
        self.assertEqual(1, submission.score)
    
    def  test_variable_mapping(self):
        post_data = {
            'problem': '1',
            'submission_3': ['u'],
            'submission_5': ['u * v'],
            'user': self.student
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        submission = Submission.objects.all()[0]
        self.assertEqual(2, submission.score)
        # same next var
        post_data['submission_4'] = ['u']
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        submission = Submission.objects.all()[1]
        self.assertEqual(1, submission.score)

        # not an alphabet 
        post_data['submission_4'] = ['1']

        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        submission = Submission.objects.all()[2]
        print(submission.submission)

        # delete last equation
        post_data['submission_4'] = ['v']
        
        del(post_data['submission_5'])
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

        submission = Submission.objects.all()[3]     

        post_data['submission_5'] = ["u * v"]
        response = self.client.post(self.url, post_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(5, Submission.objects.count())
        submission = Submission.objects.all()[4]
        self.assertEqual(3, submission.score)

       
    

class TestScoreUpdate(UsersMixin, test.TestCase):
    """
    Test updating the score on submission when a blank is deleted
    """
    url = reverse('proof_blanks_submit', kwargs={'problem': 1})

    template = 'submissions'
    model = Problem

    def setUp(self):
        UsersMixin.setUp(self)
        self.problem = self.model.objects.create(pk=1, name='test_problem', answer_keys={"1": "2", "2": "3", "3": "4"},
                                                 visibility='open')
        Feedback.objects.create(hint_keys={"1": "this is an int"},feedback_keys={"1": "{'type': 'int'}"},
                                pk=1, problem=self.problem)
        self.submission = Submission(section=self.section, user=self.student,
                                     submission={"1": "2", "2": "3"}, problem=self.problem,
                                     score=2, pk=1)
        self.submission.save()
    
    def test_no_change(self):
        self.model.objects.filter(pk=1).update(answer_keys={"1": "2", "2": "3"})
        self.problem.refresh_from_db()
        submission = Submission.objects.all()[0]
        submission.refresh_from_db()
        self.assertEqual(2, submission.score)
    
    def test_change(self):
        submission = Submission.objects.all()[0]
        self.problem.answer_keys = {"1": "2"}
        self.problem.save()
        submission = Submission.objects.all()[0]
        submission.refresh_from_db()
        self.assertEqual(1, submission.score)



class TestBestSubmissionCode(TestBestSubmission, UsersMixin, test.TestCase):
    """
    Test updating best submission per student.

    Note: submissions are sorted in descending order by timestamp.
    """
    def setUp(self):
        super().setUp()
        self.Submission = Submission
        self.problem = Problem.objects.create(pk=1, name='Problem1', answer_keys={"1": "2", "2": "3"},
                                              visibility='open')
        self.problem.save
    
class TestSubmissionHistory(TestSubmissionHistoryDatabaseHits, UsersMixin,
                            TransactionTestCase):

    url = reverse('proof_blanks_async_history', kwargs={'problem': 1})
    db_hits = 9
    def setUp(self):
        UsersMixin.setUp(self)

        quest = Quest.objects.create(name='1', description='1')
        SectionQuest.objects.filter(section=self.student.section).update(due_on=localtime(now()))

        challenge = Challenge.objects.create(name='1', description='1', quest=quest, visibility='open')

        self.problem = Problem.objects.create(pk=1, name='1',
                                              visibility='open', challenge=challenge, answer_keys={"1": "2", "2": "3", "3": "4"})

        scores = [1, 2, 0, 5, 1, 0, 3]
        for score in scores:
            sub = Submission.objects.create(problem=self.problem,
                                            user=self.student, score=score)
            sub.set_best_submission()

        self.assertEqual(len(scores), Submission.objects.count())

# does not work right now
class TestGrading(TestProblemSubmissionGradesBeforeDeadline, test.TestCase):
    problem_class = Problem
    submission_class = Submission

    def setUp(self):
        super().setUp()
        self.problem = self.problem_class.objects.create(name='Q1')
        self.problem2 = self.problem_class.objects.create(name='Q2')
