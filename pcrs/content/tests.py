from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from content.models import Challenge, OrderedContainerItem, Container, \
    ContentPage, ContentSequenceItem, TextBlock, Video
from problems_code.models import Problem, TestCase
from tests.ViewTestMixins import ProtectedViewTestMixin


class TestDatabaseHits(ProtectedViewTestMixin, TransactionTestCase):
    url = reverse('quests')
    template = 'content/container_list.html'

    def test_quests_no_quests(self):
        with self.assertNumQueries(3):
            response = self.client.get('/content/quests')

    def test_quests_only_top_level(self):
        c1 = Container.objects.create(name='1', description='1')
        self.assertEqual(1, Container.objects.count())

        x = 100
        for i in range(x):
            OrderedContainerItem.objects.create(child_content_object=c1)
        self.assertEqual(x, OrderedContainerItem.objects.count())
        with self.assertNumQueries(5):
            response = self.client.get('/content/quests')

    def test_quests_with_second_level(self):
        # linear in second level
        c1 = Container.objects.create(name='1', description='1')
        c2 = Container.objects.create(name='2', description='2')
        self.assertEqual(2, Container.objects.count())

        x = 10
        for i in range(x):
            OrderedContainerItem.objects.create(child_content_object=c1)
            OrderedContainerItem.objects.create(parent_content_object=c1,
                child_content_object=c2)
        self.assertEqual(x*2, OrderedContainerItem.objects.count())
        with self.assertNumQueries(5):
            response = self.client.get('/content/quests')

    def test_content_page(self):
        """
        Test the number of database hits on a page containing 10 videos,
        10 textblocks, and 10 problems (each having 10 testcases).

        Constant O(10).
        """
        c = Challenge.objects.create(pk=1, name='c1', description='c1')
        page = ContentPage.objects.create(challenge=c, order=0)

        def create_content_objects(iters, name):
            for i in range(iters):
                t = TextBlock.objects.create(text='foo')
                ContentSequenceItem.objects.create(content_page=page,
                                                   content_object=t)

                v = Video.objects.create(name=name+str(i),
                                         description=name+str(i),
                                         link='www.google.ca')
                ContentSequenceItem.objects.create(content_page=page,
                                                   content_object=v)

                p = Problem.objects.create(name=name+str(i),
                                           description=name+str(i))
                TestCase.objects.create(test_input=1, expected_output=2,
                                        problem=p)
                TestCase.objects.create(test_input=1, expected_output=2,
                                        problem=p)
                ContentSequenceItem.objects.create(content_page=page,
                                                   content_object=p)

        iters = 10
        create_content_objects(10, 'i')
        self.assertEqual(iters*3, ContentSequenceItem.objects.count())
        with self.assertNumQueries(10):
            response = self.client.get('/content/challenge/1/0')

        iters2 = 20
        create_content_objects(20, 'j')
        self.assertEqual((iters+iters2)*3, ContentSequenceItem.objects.count())
        with self.assertNumQueries(10):
            response = self.client.get('/content/challenge/1/0')
