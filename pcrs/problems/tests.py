from django.utils.timezone import localtime, now, timedelta
from content.models import Challenge, Quest, SectionQuest

from users.models import PCRSUser, Section


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
            problem=self.problem, user=self.student1, score=2)
        submission.timestamp = self.nextweek
        submission.save()

        best = self.problem.best_per_user_before_time(localtime(now()))
        self.assertEqual(0, len(best))

    def test_one_submission_wrong_problem(self):
        """
        Solutions to a different problem should not be counted.
        """
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=0)
        best = self.problem2.best_per_user_before_time(localtime(now()))
        self.assertEqual(0, len(best))

    def test_one_submission(self):
        """
        Solution before time should be counted.
        """
        submission = self.submission_class.objects.create(
            pk=1, problem=self.problem, user=self.student1, score=2)
        submission.timestamp = self.yesterday
        best = self.problem.best_per_user_before_time(localtime(now()))
        self.assertCountEqual(best, [{'user_id': u'student1', 'score': 2}])

    def test_mult_submissions_best(self):
        """
        Student's best solution to problem before time should be counted
        """
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=2)
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=0)

        best = self.problem.best_per_user_before_time(self.nextweek)
        self.assertCountEqual(best, [{'user_id': u'student1', 'score': 2}])

    def test_mult_submissions_best_before(self):
        """
        Student's best solution to problem before deadline should be counted,
        even if she submitted a better solution after deadline
        """
        submission1 = self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=0)

        submission2 = self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=2)

        submission3 = self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=3)
        submission3.timestamp = self.nextweek
        submission3.save()

        best = self.problem.best_per_user_before_time(localtime(now()))
        self.assertCountEqual(best, [{'user_id': 'student1', 'score': 2}])

    def test_same_scores(self):
        """
        Only one solution should be counted if two submission have the same score
        """
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=2)
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=2)

        best = self.problem.best_per_user_before_time(self.nextweek)
        self.assertCountEqual([{'user_id': 'student1', 'score': 2}], best)

    def test_mult_students_mult_sol(self):
        """
        Each user's best solution to problem before time should be counted
        """
        # student 1' submissions
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=0)
        self.submission_class.objects.create(
            problem=self.problem, user=self.student1, score=2)

        # student 2's submissions
        self.submission_class.objects.create(
            problem=self.problem, user=self.student2, score=3)
        self.submission_class.objects.create(
            problem=self.problem, user=self.student2, score=2)
        self.submission_class.objects.create(
            problem=self.problem, user=self.student2, score=1)

        best = self.problem.best_per_user_before_time(self.nextweek)
        self.assertEqual(len(best), 2)
        self.assertCountEqual(best, [{'user_id': 'student1', 'score': 2},
                                     {'user_id': 'student2', 'score': 3}])
        
        
class TestBestSubmission:
    """
    Test updating best submission per student.

    Note: submissions are sorted in descending order by timestamp.
    """
    
    def test_single_submission(self):
        s = self.Submission.objects.create(user=self.student, section=self.section,
                                      problem=self.problem, score=0)
        s.set_best_submission()
        self.assertTrue(s.has_best_score)

    def test_new_better_submission(self):
        s = self.Submission.objects.create(user=self.student, section=self.section,
                                      problem=self.problem, score=0)
        s.set_best_submission()
        self.assertTrue(s.has_best_score)

        s2 = self.Submission.objects.create(user=self.student, section=self.section,
                                       problem=self.problem, score=2)
        s2.set_best_submission()
        s2, s1 = self.Submission.objects.all()
        self.assertFalse(s1.has_best_score)
        self.assertTrue(s2.has_best_score)

    def test_new_worse_submission(self):
        s = self.Submission.objects.create(user=self.student, section=self.section,
                                      problem=self.problem, score=2)
        s.set_best_submission()
        self.assertTrue(s.has_best_score)

        s2 = self.Submission.objects.create(user=self.student, section=self.section,
                                       problem=self.problem, score=0)
        s2.set_best_submission()
        s2, s1 = self.Submission.objects.all()
        self.assertTrue(s1.has_best_score)
        self.assertFalse(s2.has_best_score)

    def test_new_same_score_submission(self):
        s = self.Submission.objects.create(user=self.student, section=self.section,
                                      problem=self.problem, score=2)
        s.set_best_submission()
        self.assertTrue(s.has_best_score)

        s2 = self.Submission.objects.create(user=self.student, section=self.section,
                                       problem=self.problem, score=2)
        s2.set_best_submission()
        s2, s1 = self.Submission.objects.all()
        self.assertFalse(s1.has_best_score)
        self.assertTrue(s2.has_best_score)

    def test_same_score_different_user(self):
        s = self.Submission.objects.create(user=self.student, section=self.section,
                                      problem=self.problem, score=2)
        s.set_best_submission()
        self.assertTrue(s.has_best_score)

        s2 = self.Submission.objects.create(user=self.ta, section=self.section,
                                       problem=self.problem, score=2)
        s2.set_best_submission()
        s2, s1 = self.Submission.objects.all()
        self.assertTrue(s1.has_best_score)
        self.assertTrue(s2.has_best_score)

    def test_new_submission_for_user(self):
        s = self.Submission.objects.create(user=self.student, section=self.section,
                                      problem=self.problem, score=0)
        s.set_best_submission()
        self.assertTrue(s.has_best_score)

        s2 = self.Submission.objects.create(user=self.ta, section=self.section,
                                       problem=self.problem, score=2)
        s2.set_best_submission()

        s3 = self.Submission.objects.create(user=self.ta, section=self.section,
                                       problem=self.problem, score=3)
        s3.set_best_submission()

        s3, s2, s1 = self.Submission.objects.all()
        self.assertTrue(s1.has_best_score)
        self.assertFalse(s2.has_best_score)
        self.assertTrue(s3.has_best_score)


class TestNumberSolvedBeforeDeadline:
    """
    Test getting the number of problems a student has solved in a Challenge.
    """

    def setUp(self):
        self.s1 = Section.objects.create(section_id='001', location='BA', lecture_time='10-11')
        self.s2 = Section.objects.create(section_id='002', location='BA', lecture_time='11-12')
        self.s3 = Section.objects.create(section_id='003', location='BA', lecture_time='12-13')

        self.student1 = PCRSUser.objects.create(username='student1', section=self.s1)
        self.student2 = PCRSUser.objects.create(username='student2', section=self.s1)
        self.student3 = PCRSUser.objects.create(username='student3', section=self.s2)

        self.quest = Quest.objects.create(name='c1', description='c2')
        SectionQuest.objects.create(quest=self.quest, due_on=localtime(now()) + timedelta(days=7), section=self.s1)
        self.challenge = Challenge.objects.create(pk=1, name='c1', description='c2', quest=self.quest)


class TestNumberSolvedBeforeDeadlineChallenges:
    """
    Test getting the number of problems a student has solved in a Challenge,
    with multiple Challenges.
    """

    def setUp(self):
        self.s1 = Section.objects.create(section_id='001', location='BA', lecture_time='10-11')
        self.s2 = Section.objects.create(section_id='002', location='BA', lecture_time='11-12')
        self.s3 = Section.objects.create(section_id='003', location='BA', lecture_time='12-13')

        self.student1 = PCRSUser.objects.create(username='student1', section=self.s1)
        self.student2 = PCRSUser.objects.create(username='student2', section=self.s1)
        self.student3 = PCRSUser.objects.create(username='student3', section=self.s2)

        self.quest = Quest.objects.create(name='c1', description='c2')
        SectionQuest.objects.create(quest=self.quest, due_on=localtime(now()) + timedelta(days=7), section=self.s1)
        self.challenge = Challenge.objects.create(pk=1, name='c1', description='c1', quest=self.quest)
        self.challenge2 = Challenge.objects.create(pk=2, name='c2', description='c2', quest=self.quest)


class TestNumberSolvedBeforeDeadlines:
    """
    Test getting the number of problems a student has solved in a Challenge.
    """

    def setUp(self):
        self.s1 = Section.objects.create(section_id='001', location='BA', lecture_time='10-11')
        self.s2 = Section.objects.create(section_id='002', location='BA', lecture_time='11-12')
        self.s3 = Section.objects.create(section_id='003', location='BA', lecture_time='12-13')

        self.student1 = PCRSUser.objects.create(username='student1', section=self.s1)
        self.student2 = PCRSUser.objects.create(username='student2', section=self.s2)
        self.student3 = PCRSUser.objects.create(username='student3', section=self.s2)

        self.quest = Quest.objects.create(name='c1', description='c2')
        SectionQuest.objects.create(quest=self.quest, due_on=localtime(now()) + timedelta(days=7), section=self.s1)
        SectionQuest.objects.create(quest=self.quest, due_on=localtime(now()) - timedelta(days=7), section=self.s2)
        self.challenge = Challenge.objects.create(pk=1, name='c1', description='c1', quest=self.quest)
        self.challenge2 = Challenge.objects.create(pk=2, name='c2', description='c2', quest=self.quest)


class TestNumberSolvedQuests:
    """
    Test getting the number of problems a student has solved in a Challenge,
    with multiple Challenges in multiple Quests.
    """

    def setUp(self):
        self.s1 = Section.objects.create(section_id='001', location='BA', lecture_time='10-11')
        self.s2 = Section.objects.create(section_id='002', location='BA', lecture_time='11-12')
        self.s3 = Section.objects.create(section_id='003', location='BA', lecture_time='12-13')

        self.student1 = PCRSUser.objects.create(username='student1', section=self.s1)
        self.student2 = PCRSUser.objects.create(username='student2', section=self.s2)
        self.student3 = PCRSUser.objects.create(username='student3', section=self.s2)

        self.quest = Quest.objects.create(name='q1', description='q1')
        SectionQuest.objects.create(quest=self.quest, section=self.s1,
                                    due_on=localtime(now()) + timedelta(days=7))
        SectionQuest.objects.create(quest=self.quest, section=self.s2,
                                    due_on=localtime(now()) - timedelta(days=7))

        self.quest2 = Quest.objects.create(name='q2', description='q2')
        SectionQuest.objects.create(quest=self.quest2, section=self.s1,
                                    due_on=localtime(now()) + timedelta(days=7))
        SectionQuest.objects.create(quest=self.quest2, section=self.s2,
                                    due_on=localtime(now()) - timedelta(days=7))

        self.challenge = Challenge.objects.create(pk=1, name='c1', description='c1', quest=self.quest)
        self.challenge2 = Challenge.objects.create(pk=2, name='c2', description='c2', quest=self.quest)
        self.challenge3 = Challenge.objects.create(pk=3, name='c3', description='c3', quest=self.quest2)
        self.challenge4 = Challenge.objects.create(pk=4, name='c4', description='c4', quest=self.quest2)