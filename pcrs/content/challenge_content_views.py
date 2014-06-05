import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, DeleteView

from content.models import (Challenge, ContentPage, ContentSequenceItem,
                            TextBlock)
from problems.models import get_problem_labels
from users.views_mixins import CourseStaffViewMixin


class ChallengeAddContentView:
    """
    Base class for working with ContentObjects in Challenges.
    """
    def get_challenge(self):
        return get_object_or_404(Challenge.objects.select_related(),
                                 pk=self.kwargs.get('challenge', None))

    def get_page(self):
        return get_object_or_404(ContentPage, pk=self.kwargs.get('page', None))


class ChallengeObjectsView(CourseStaffViewMixin, DetailView):
    """
    Manage the ContentObjects for a Challenge
    """
    template_name = 'content/challenge_objects.html'
    model = Challenge

    def get_queryset(self):
        return self.model.get_visible_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = ContentSequenceItem.get_unassigned_video()
        context['problems'] = {}
        for problem_type in get_problem_labels():
            context['problems'][problem_type] = \
                ContentSequenceItem.get_unassigned_problems(problem_type)
        return context


class ChallengePagesObjectsView(CourseStaffViewMixin, CreateView):
    """
    Create the content object for the ContentPages in a Challenge.
    """
    model = Challenge

    def post(self, *args, **kwargs):
        # a list of lists with the outer list corresponding to a page,
        # and the inner one to ids of objects
        page_object_list = json.loads(self.request.POST.get('page_object_list'))
        pages = self.get_object().contentpage_set.all().order_by('order')

        for i in range(len(page_object_list)):
            page, objects = pages[i], page_object_list[i]
            page.contentsequenceitem_set.all().delete()
            # the items are in format type-pk where type can be video, text, or
            # a problem app label
            for object_index in range(len(objects)):
                object_type, pk = objects[object_index].split('-')
                try:
                    model = ContentType.objects\
                        .get(model=object_type).model_class()
                except ContentType.DoesNotExist:
                    model = ContentType.objects\
                        .get(model='problem', app_label=object_type).model_class()
                content_object = get_object_or_404(model, pk=pk)
                ContentSequenceItem.objects.create(
                    content_object=content_object, content_page=page,
                    order=object_index)

        return HttpResponse(json.dumps({'status': 'ok'}))


class TextCreateView(CourseStaffViewMixin, ChallengeAddContentView, CreateView):
    """
    Create a new TextBlock from text sent in with an Ajax post request.
    """
    model = TextBlock

    def post(self, request, *args, **kwargs):
        text = request.POST.get('text', None)
        if text:
            textblock = self.model.objects.create(text=text)
            return HttpResponse(json.dumps({'status': 'ok',
                                            'pk': textblock.pk}),
                                mimetype='application/json')


class PageCreateView(CourseStaffViewMixin, ChallengeAddContentView, CreateView):
    """
    Create a new ContentPage for some Challenge.
    """
    model = ContentPage

    def post(self, request, *args, **kwargs):
        challenge = self.get_challenge()
        last_page = challenge.contentpage_set.aggregate(last=Max('order'))
        order = last_page['last'] + 1 if last_page['last'] is not None else 0

        new_page = self.model.objects.create(challenge=challenge,
                                             order=order)
        return HttpResponse(json.dumps({'status': 'ok', 'pk': new_page.pk}),
                            mimetype='application/json')


class ItemDeleteView(CourseStaffViewMixin, DeleteView):
    """
    Delete a ContentObject or ContentPage.
    """
    def post(self, *args, **kwargs):
        get_object_or_404(self.model, pk=self.kwargs.get('pk', None)).delete()
        return HttpResponse(json.dumps({'status': 'ok'}),
                            mimetype='application/json')