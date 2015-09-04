from django import test
from django.core.urlresolvers import reverse
from content.models import Quest, SectionQuest
from tests.ViewTestMixins import CourseStaffViewTestMixin
from users.models import Section


class TestSectionCreateView(CourseStaffViewTestMixin, test.TestCase):
    """
    Test adding a Section.
    """
    url = reverse('section_create')
    successful_redirect_url = reverse('section_quests', kwargs={'section': 'LEC001'})
    template = 'pcrs/item_form.html'

    def setUp(self):
        CourseStaffViewTestMixin.setUp(self)
        self.post_data =  {
            'section_id': 'LEC001', 'lecture_time': '10-11', 'location': 'BA'
        }

    def test_create_section(self):
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)
        self.assertTrue(Section.objects
            .filter(section_id='LEC001', lecture_time='10-11', location='BA')
            .exists())

    def test_create_section_add_section_quests(self):
        q1 = Quest.objects.create(pk=1, name='Quest 1', description='Quest 1')
        q2 = Quest.objects.create(pk=2, name='Quest 2', description='Quest 2')

        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        new_section = Section.objects\
            .get(section_id='LEC001', lecture_time='10-11', location='BA')

        # section quests should be added for the newly created section
        self.assertTrue(SectionQuest.objects
            .filter(section=new_section, quest=q1).exists())
        self.assertTrue(SectionQuest.objects
            .filter(section=new_section, quest=q2).exists())