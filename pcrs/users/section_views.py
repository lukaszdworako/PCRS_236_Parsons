from pcrs.generic_views import GenericItemListView, GenericItemCreateView, \
    GenericItemUpdateView
from users.forms import SectionForm
from users.models import Section
from users.views_mixins import CourseStaffViewMixin


class SectionListView(CourseStaffViewMixin, GenericItemListView):
    model = Section


class SectionCreateView(CourseStaffViewMixin, GenericItemCreateView):
    model = Section
    form_class = SectionForm

    def get_success_url(self):
        return self.object.get_manage_section_quests_url()


class SectionUpdateView(CourseStaffViewMixin, GenericItemUpdateView):
    model = Section
    form_class = SectionForm