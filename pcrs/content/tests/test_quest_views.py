from django import test
from django.core.urlresolvers import reverse

from content.models import Quest, SectionQuest
from ViewTestMixins import CourseStaffViewTestMixin
from users.models import Section


class TestQuestCreateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a Quest.
    """
    url = reverse('quest_create')
    successful_redirect_url = reverse('quest_list')
    template = 'pcrs/item_form.html'

    def setUp(self):
        CourseStaffViewTestMixin.setUp(self)
        self.section2 = Section.objects.create(
            section_id='LEC001', lecture_time='10-11', location='BA')

    def test_create_quest(self):
        post_data = {
            'name': 'Quest 1',
            'description': 'Quest 1 desc',
            'mode': 'live'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, Quest.objects.count())
        quest = Quest.objects.all()[0]
        self.assertEqual('Quest 1', quest.name)
        self.assertEqual('Quest 1 desc', quest.description)

        self.assertEqual(2, SectionQuest.objects.count())
        self.assertTrue(SectionQuest.objects
            .filter(section=self.section, quest=quest).exists())
        self.assertTrue(SectionQuest.objects
            .filter(section=self.section2, quest=quest).exists())


class TestQuestUpdateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test updating a Quest.
    """
    url = reverse('quest_update', kwargs={'pk': 1})
    successful_redirect_url = reverse('quest_list')
    template = 'pcrs/item_form.html'

    def setUp(self):
        Quest.objects.create(pk=1, name='Quest 1', description='Quest 1 desc')
        CourseStaffViewTestMixin.setUp(self)
        self.section2 = Section.objects.create(
            section_id='LEC001', lecture_time='10-11', location='BA')

    def test_update_quest(self):

        post_data = {
            'name': 'Updated Quest 1',
            'description': 'Updated Quest 1 desc',
            'mode': 'live'
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, Quest.objects.count())
        quest = Quest.objects.all()[0]
        self.assertEqual('Updated Quest 1', quest.name)
        self.assertEqual('Updated Quest 1 desc', quest.description)

        # section quest exist
        self.assertEqual(2, SectionQuest.objects.count())
        self.assertTrue(SectionQuest.objects
            .filter(section=self.section, quest=quest).exists())
        self.assertTrue(SectionQuest.objects
            .filter(section=self.section2, quest=quest).exists())