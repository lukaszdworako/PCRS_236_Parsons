from django.utils.timezone import localtime, now, timedelta

from users.models import PCRSUser


class TestProblemSubmissionGradesBeforeDeadline:
    """
    Tests problem grading.
    """
    problem_class = None
    submission_class = None

    def setUp(self):
        self.student1 = PCRSUser.objects.create(username='student1')
        self.student2 = PCRSUser.objects.create(username='student2')
        self.student3 = PCRSUser.objects.create(username='student3')

        # these are used to force update a submission with a time,
        # since we cannot pass in a value to field that has auto_now True
        self.yesterday = localtime(now()) - timedelta(days=7)
        self.nextweek = localtime(now()) + timedelta(days=7)

    def test_one_submission_wrong_time(self):
        """
        Solutions after the deadline should not be counted.
        """
        submission = self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=2)
        submission.timestamp = self.nextweek
        submission.save()

        best = self.problem.best_per_student_before_time(localtime(now()))
        self.assertEqual(0, len(best))

    def test_one_submission_wrong_problem(self):
        """
        Solutions to a different problem should not be counted.
        """
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=0)
        best = self.problem2.best_per_student_before_time(localtime(now()))
        self.assertEqual(0, len(best))

    def test_one_submission(self):
        """
        Solution before time should be counted.
        """
        submission = self.submission_class.objects.create(
            pk=1, problem=self.problem, student=self.student1, score=2)
        submission.timestamp = self.yesterday
        best = self.problem.best_per_student_before_time(localtime(now()))
        self.assertCountEqual(best, [{'student_id': u'student1', 'score': 2}])

    def test_mult_submissions_best(self):
        """
        Student's best solution to problem before time should be counted
        """
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=2)
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=0)

        best = self.problem.best_per_student_before_time(self.nextweek)
        self.assertCountEqual(best, [{'student_id': u'student1', 'score': 2}])

    def test_mult_submissions_best_before(self):
        """
        Student's best solution to problem before deadline should be counted,
        even if she submitted a better solution after deadline
        """
        submission1 = self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=0)

        submission2 = self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=2)

        submission3 = self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=3)
        submission3.timestamp = self.nextweek
        submission3.save()

        best = self.problem.best_per_student_before_time(localtime(now()))
        self.assertCountEqual(best, [{'student_id': 'student1', 'score': 2}])

    def test_same_scores(self):
        """
        Only one solution should be counted if two submission have the same score
        """
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=2)
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=2)

        best = self.problem.best_per_student_before_time(self.nextweek)
        self.assertCountEqual([{'student_id': 'student1', 'score': 2}], best)

    def test_mult_students_mult_sol(self):
        """
        Each student's best solution to problem before time should be counted
        """
        # student 1' submissions
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=0)
        self.submission_class.objects.create(
            problem=self.problem, student=self.student1, score=2)

        # student 2's submissions
        self.submission_class.objects.create(
            problem=self.problem, student=self.student2, score=3)
        self.submission_class.objects.create(
            problem=self.problem, student=self.student2, score=2)
        self.submission_class.objects.create(
            problem=self.problem, student=self.student2, score=1)

        best = self.problem.best_per_student_before_time(self.nextweek)
        self.assertEqual(len(best), 2)
        self.assertCountEqual(best, [{'student_id': 'student1', 'score': 2},
                                     {'student_id': 'student2', 'score': 3}])