import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView

from content.models import (Challenge, ContentPage, ContentSequenceItem,
                            TextBlock)
from problems.models import get_problem_labels, get_problem_content_types
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
        text_block_ctype = ContentType.objects.get(model='textblock')

        # remove all problems from this challenge
        challenge = self.get_object()
        for ct in get_problem_content_types():
            ct.model_class().objects.filter(challenge=challenge)\
                                    .update(challenge=None)

        # a list of lists with the outer list corresponding to a page,
        # and the inner one to ids of objects
        page_object_list = json.loads(self.request.POST.get('page_object_list'))
        pages = self.get_object().contentpage_set.all().order_by('order')

        current_text_objects = set(
            ContentSequenceItem.objects
                .filter(content_type=text_block_ctype, content_page__in=pages)
                .values_list('object_id', flat=True))
        new_text_objects = set()

        for i in range(len(page_object_list)):
            page, objects = pages[i], page_object_list[i]
            page.contentsequenceitem_set.exclude(content_type=text_block_ctype)\
                .delete()
            # the items are in format type-pk where type can be video, text, or
            # a problem app label
            for object_index in range(len(objects)):
                object_type, pk = objects[object_index].split('-')

                if object_type.startswith('problem'):
                    ctype = ContentType.objects\
                        .get(model='problem', app_label=object_type)
                    problem = get_object_or_404(ctype.model_class(), pk=pk)
                    problem.challenge = challenge
                    problem.save()
                else:
                    ctype = ContentType.objects.get(model=object_type)
                    if ctype == text_block_ctype:
                        new_text_objects.add(int(pk))
                try:
                    item = ContentSequenceItem.objects.get(
                        content_type=ctype, object_id=pk)
                    item.order = object_index
                    item.content_page = page
                    item.save()
                except ContentSequenceItem.DoesNotExist:
                    ContentSequenceItem.objects.create(
                        content_type=ctype, object_id=pk, order=object_index,
                        content_page=page)

        ContentSequenceItem.objects.filter(content_type=text_block_ctype,
            object_id__in=(current_text_objects-new_text_objects))\
            .delete()
        TextBlock.objects.filter(pk__in=current_text_objects-new_text_objects).delete()


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


class TextUpdateView(CourseStaffViewMixin, UpdateView):
    """
    Update a TextBlock from text sent in with an Ajax post request.
    """
    model = TextBlock

    def post(self, request, *args, **kwargs):
        textblock = get_object_or_404(self.model, pk=self.kwargs.get('pk', None))
        text = request.POST.get('text', None)
        if text:
            textblock.text = text
            textblock.save()
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
        order = last_page['last'] + 1 if last_page['last'] is not None else 1

        new_page = self.model.objects.create(challenge=challenge,
                                             order=order)
        return HttpResponse(json.dumps({'status': 'ok', 'pk': new_page.pk}),
                            mimetype='application/json')


class ItemDeleteView(CourseStaffViewMixin, DeleteView):
    """
    Delete a ContentObject from a page.
    """
    def post(self, *args, **kwargs):
        get_object_or_404(self.model, pk=self.kwargs.get('pk', None)).delete()
        return HttpResponse(json.dumps({'status': 'ok'}),
                            mimetype='application/json')


class PageDeleteView(CourseStaffViewMixin, DeleteView):
    """
    Delete a ContentPage.
    """
    def post(self, *args, **kwargs):
        page = get_object_or_404(self.model, pk=self.kwargs.get('pk', None))
        text_ids = ContentSequenceItem.objects\
                .filter(content_type=ContentType.objects.get(model='textblock'),
                        content_page=page)\
                .values_list('object_id', flat=True)
        TextBlock.objects.filter(pk__in=text_ids).delete()
        page.delete()
        return HttpResponse(json.dumps({'status': 'ok'}),
                            mimetype='application/json')


class ChangeProblemVisibilityView(CourseStaffViewMixin, ChallengeAddContentView, CreateView):
    """
    Change a problems visibility.
    """

    def post(self, request, *args, **kwargs):
        app_label = request.POST.get('problem_type', None)
        pk = request.POST.get('problem_pk', None)
        problem_class = ContentType.objects.get(app_label=app_label, model='problem').model_class()
        problem = problem_class.objects.get(pk=pk)
        if problem.is_open():
            old_visibility = 'open'
            problem.closed()
        else:  # problem.is_closed()
            old_visibility = 'closed'
            problem.open()

        return HttpResponse(json.dumps({'status': 'ok','old_visibility':old_visibility, 'new_visibility':problem.visibility}),
                                mimetype='application/json')
