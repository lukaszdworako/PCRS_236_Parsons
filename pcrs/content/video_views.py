import json
from django.http import HttpResponse
from django.views.generic import CreateView
from django.db.utils import IntegrityError
from content.forms import VideoForm
from content.models import Video, WatchedVideo, ContentSequenceItem

from pcrs.generic_views import GenericItemListView, GenericItemCreateView, \
    GenericItemUpdateView
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin


class VideoListView(CourseStaffViewMixin, GenericItemListView):
    """
    List all Videos.
    """
    model = Video
    template_name = 'content/video_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['video_to_challenge'] = {}
        for item in ContentSequenceItem.objects\
            .select_related('content_page', 'content_page__challenge').all():
            if item.content_type.model == 'video':
                context['video_to_challenge'][item.object_id] = \
                    item.content_page.challenge.name
        return context


class VideoDetailEntry(CourseStaffViewMixin):
    model = Video
    template_name = 'pcrs/item_form.html'
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
        if not WatchedVideo.watched(user=self.request.user, video=video):
            try:
                WatchedVideo.objects.create(video=video, user=self.request.user)
            except IntegrityError:      # duplicate watched object
                pass
        return HttpResponse(json.dumps({'status': 'ok'}),
                            content_type='application/json')
