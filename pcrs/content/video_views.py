from content.forms import VideoForm
from content.models import Video

from pcrs.generic_views import GenericItemListView, GenericItemCreateView, \
    GenericItemUpdateView
from users.views_mixins import CourseStaffViewMixin


class VideoListView(CourseStaffViewMixin, GenericItemListView):
    """
    List all Videos.
    """
    model = Video
    template_name = 'pcrs/item_list.html'


class VideoDetailEntry(CourseStaffViewMixin):
    model = Video
    template_name = 'pcrs/crispy_form.html'
    form_class = VideoForm


class VideoCreateView(VideoDetailEntry, GenericItemCreateView):
    """
    Create a new Video.
    """


class VideoUpdateView(VideoDetailEntry, GenericItemUpdateView):
    """
    Update a Video.
    """