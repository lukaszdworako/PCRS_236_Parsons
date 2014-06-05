from content.forms import TagForm
from content.tags import Tag

from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from users.views_mixins import CourseStaffViewMixin


class TagListView(CourseStaffViewMixin, GenericItemListView):
    """
    List all Tags.
    """
    model = Tag
    template_name = 'pcrs/item_list.html'


class TagDetailEntry(CourseStaffViewMixin):
    model = Tag
    template_name = 'pcrs/crispy_form.html'
    form_class = TagForm


class TagCreateView(TagDetailEntry, GenericItemCreateView):
    """
    Create a new Tag.
    """


class TagUpdateView(TagDetailEntry, GenericItemUpdateView):
    """
    Update a Tag.
    """

