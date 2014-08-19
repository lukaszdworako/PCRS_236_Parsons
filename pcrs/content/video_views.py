import json
from django.http import HttpResponse
from django.views.generic import CreateView
from content.forms import VideoForm
from content.models import Video, WatchedVideo

from pcrs.generic_views import GenericItemListView, GenericItemCreateView, \
    GenericItemUpdateView
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin


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


class VideoRecordWatchView(ProtectedViewMixin, CreateView):
    """
    Create a record of a user watching a video.
    """
    model = Video

    def post(self, request, *args, **kwargs):
        video = self.get_object()
        # WatchedVideo.objects.create(video=video, user=self.request.user)
        return HttpResponse(json.dumps({'status': 'ok'}),
                            mimetype='application/json')