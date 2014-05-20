from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from content.models import Challenge
from tests.ViewTestMixins import ProtectedViewTestMixin


class SimpleTest(ProtectedViewTestMixin, TransactionTestCase):
    url = reverse('quests')
    template = 'content/container_list.html'

    def test_num_queries(self):
        with self.assertNumQueries(1):
            response = self.client.get('/content/quests')
