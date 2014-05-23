from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from content.models import Challenge, OrderedContainerItem, Container
from tests.ViewTestMixins import ProtectedViewTestMixin


class SimpleTest(ProtectedViewTestMixin, TransactionTestCase):
    url = reverse('quests')
    template = 'content/container_list.html'

    def test_num_queries0(self):
        with self.assertNumQueries(3):
            response = self.client.get('/content/quests')

    def test_num_queries1(self):
        c1 = Container.objects.create(name='1', description='1')
        self.assertEqual(1, Container.objects.count())

        x = 100
        for i in range(x):
            OrderedContainerItem.objects.create(child_content_object=c1)
        self.assertEqual(x, OrderedContainerItem.objects.count())
        with self.assertNumQueries(5):
            response = self.client.get('/content/quests')

    def test_num_queries2(self):
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

    # def test_num_queries2(self):
    #     with self.assertNumQueries(1):
    #         response = self.client.get('/content/quests')
