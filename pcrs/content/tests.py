# from django.core.urlresolvers import reverse
# from django.db import connection
# from django.test import TransactionTestCase
# from django.utils.timezone import localtime, now, timedelta
#
# from content.models import *
# from problems_code.models import Problem, TestCase, Submission
# from tests.ViewTestMixins import ProtectedViewTestMixin
#
#
# class TestQuestsPageDatabaseHits(ProtectedViewTestMixin, TransactionTestCase):
#     """
#     Test the number of database hits when loading the quests page.
#
#     Should be kept constant.
#     """
#     db_hits = 9
#     url = reverse('quests')
#     template = 'content/container_list.html'
#
#     def test_no_quests(self):
#         with self.assertNumQueries(self.db_hits):
#             response = self.client.get(self.url)
#             print(connection.queries)
#
#     def test_quests_only(self):
#         num_quests = 50
#         for i in range(num_quests):
#             c = Quest.objects.create(name=str(i), description='c')
#             SectionQuest.objects.create(open_on=now(), due_on=now(),
#                                             container=c, is_graded=True,
#                                             section=self.section,
#                                             visibility='open')
#         self.assertEqual(num_quests, Quest.objects.count())
#         self.assertEqual(num_quests, SectionQuest.objects.count())
#         with self.assertNumQueries(self.db_hits):
#             response = self.client.get('/content/quests')
#             print(connection.queries)
#
#
#     def test_quests_and_challenges(self):
#         num_quests = 10
#         num_challenges = 10
#         for i in range(num_quests):
#             c = Quest.objects.create(name=str(i), description='c')
#             SectionQuest.objects.create(open_on=now(), due_on=now(),
#                                             container=c, is_graded=True,
#                                             section=self.section,
#                                             visibility='open')
#             for j in range(num_challenges):
#                 clnge = Challenge.objects.create(name=str(i)+'_'+str(j),
#                                                  description='c',
#                                                  container=c, visibility='open')
#
#         self.assertEqual(num_quests, Quest.objects.count())
#         self.assertEqual(num_quests, SectionQuest.objects.count())
#         self.assertEqual(num_quests*num_challenges, Challenge.objects.count())
#         with self.assertNumQueries(self.db_hits):
#             response = self.client.get('/content/quests')
#
#     def test_quests_problem_sets_problems(self):
#         num_quests = 10
#         num_ps = 10
#         num_problems = 10
#         for i in range(num_quests):
#             c = Quest.objects.create(name=str(i), description='c')
#             SectionQuest.objects.create(open_on=now(), due_on=now(),
#                                             container=c, is_graded=True,
#                                             section=self.section,
#                                             visibility='open')
#             for j in range(num_ps):
#                 ps = ProblemSet.objects.create(name=str(i)+'_'+str(j),
#                                                description='c',
#                                                container=c, visibility='open')
#                 for k in range(num_problems):
#                     name = '{0}_{1}_{2}'.format(i, j, k)
#                     p = Problem.objects.create(name=name, description='d',
#                                                visibility='open')
#                     ChallengeProblem(problem_object=p, container_object=ps)\
#                         .save()
#
#         self.assertEqual(num_quests, Quest.objects.count())
#         self.assertEqual(num_quests, SectionQuest.objects.count())
#         self.assertEqual(num_quests*num_ps, ProblemSet.objects.count())
#         self.assertEqual(num_quests*num_ps*num_problems,
#                          Problem.objects.count())
#         with self.assertNumQueries(self.db_hits):
#             response = self.client.get('/content/quests')
#             print(connection.queries)
#
#     def test_quests_problem_sets_problems_submissions(self):
#         num_quests = 10
#         num_ps = 10
#         num_problems = 10
#         num_sub = 10
#         for i in range(num_quests):
#             c = Quest.objects.create(name=str(i), description='c')
#             SectionQuest.objects.create(open_on=now(), due_on=now(),
#                 container=c, is_graded=True,
#                 section=self.section,
#                 visibility='open')
#             for j in range(num_ps):
#                 ps = ProblemSet.objects.create(name=str(i)+'_'+str(j),
#                     description='c',
#                     container=c, visibility='open')
#                 ContainerAttempt(content_object=ps, user=self.student).save()
#                 for k in range(num_problems):
#                     name = '{0}_{1}_{2}'.format(i, j, k)
#                     p = Problem.objects.create(name=name, description='d',
#                         visibility='open')
#                     ChallengeProblem(problem_object=p, container_object=ps) \
#                         .save()
#                     for l in range(num_sub):
#                         Submission(problem=p, user=self.student,
#                             section=self.section)
#
#         self.assertEqual(num_quests, Quest.objects.count())
#         self.assertEqual(num_quests, SectionQuest.objects.count())
#         self.assertEqual(num_quests*num_ps, ProblemSet.objects.count())
#         self.assertEqual(num_quests*num_ps*num_problems,
#             Problem.objects.count())
#
#         self.client.login(username=self.student.username)
#         with self.assertNumQueries(self.db_hits):
#             response = self.client.get('/content/quests')
#             print(connection.queries)
#             # def test_quests_with_second_level(self):
#             #     # linear in second level
#             #     c1 = Quest.objects.create(name='1', description='1')
#             #     c2 = Quest.objects.create(name='2', description='2')
#             #     self.assertEqual(2, Quest.objects.count())
#             #
#             #     x = 10
#             #     for i in range(x):
#             #         OrderedContainerItem.objects.create(child_content_object=c1)
#             #         OrderedContainerItem.objects.create(parent_content_object=c1,
#             #             child_content_object=c2)
#             #     self.assertEqual(x*2, OrderedContainerItem.objects.count())
#             #     with self.assertNumQueries(5):
#             #         response = self.client.get('/content/quests')
#             #
#             # def test_content_page(self):
#             #     """
#             #     Test the number of database hits on a page containing 10 videos,
#             #     10 textblocks, and 10 problems (each having 10 testcases).
#             #
#             #     Constant O(10).
#             #     """
#             #     c = Challenge.objects.create(pk=1, name='c1', description='c1')
#             #     page = ContentPage.objects.create(challenge=c, order=0)
#             #
#             #     def create_content_objects(iters, name):
#             #         for i in range(iters):
#             #             t = TextBlock.objects.create(text='foo')
#             #             ContentSequenceItem.objects.create(content_page=page,
#             #                                                content_object=t)
#             #
#             #             v = Video.objects.create(name=name+str(i),
#             #                                      description=name+str(i),
#             #                                      link='www.google.ca')
#             #             ContentSequenceItem.objects.create(content_page=page,
#             #                                                content_object=v)
#             #
#             #             p = Problem.objects.create(name=name+str(i),
#             #                                        description=name+str(i))
#             #             TestCase.objects.create(test_input=1, expected_output=2,
#             #                                     problem=p)
#             #             TestCase.objects.create(test_input=1, expected_output=2,
#             #                                     problem=p)
#             #             ContentSequenceItem.objects.create(content_page=page,
#             #                                                content_object=p)
#             #
#             #     iters = 10
#             #     create_content_objects(10, 'i')
#             #     self.assertEqual(iters*3, ContentSequenceItem.objects.count())
#             #     with self.assertNumQueries(10):
#             #         response = self.client.get('/content/challenge/1/0')
#             #
#             #     iters2 = 20
#             #     create_content_objects(20, 'j')
#             #     self.assertEqual((iters+iters2)*3, ContentSequenceItem.objects.count())
#             #     with self.assertNumQueries(10):
#             #         response = self.client.get('/content/challenge/1/0')
