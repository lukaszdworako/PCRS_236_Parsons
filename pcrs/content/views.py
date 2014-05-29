from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView, ListView, CreateView, \
    DeleteView, DetailView
from django.utils.timezone import localtime, now, timedelta

from content.forms import ChallengeForm
from content.models import *
from pcrs.generic_views import GenericItemListView, GenericItemCreateView
from problems.models import CompletedProblem
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class ChallengeView:
    model = Challenge
    form_class = ChallengeForm
    template_name = 'content/challenge_form.html'

    def get_success_url(self):
        return reverse('challenge_list')


class ChallengeListView(ProtectedViewMixin, GenericItemListView):
    model = Challenge
    template_name = 'content/challenge_list.html'


class ChallengeCreateView(CourseStaffViewMixin, ChallengeView,
                          GenericItemCreateView):
    """
    Create a new Challenge, its ContentPages and ContentObjects.
    """


class ChallengeUpdateView(CourseStaffViewMixin, ChallengeView, UpdateView):
    """
    Update a new Challenge, its ContentPages and ContentObjects.
    """


class ChallengeDeleteView(ChallengeView, DeleteView):
    """
    Delete a Challenge.
    """
    template_name = "pcrs/check_delete.html"


class ChallengeStartView(ProtectedViewMixin, DetailView):
    model = Challenge
    template_name = 'content/challenge.html'


class ContentPageView(ProtectedViewMixin, ListView):
    template_name = "content/content_page.html"

    def get_page(self):
        return get_object_or_404(ContentPage,
                                 order=self.kwargs.get('page', None),
                                 challenge_id=self.kwargs.get('challenge', None))

    def get_queryset(self):
        return ContentSequenceItem.objects.filter(content_page=self.get_page())\
            .prefetch_related('content_object').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_page'] = self.get_page()
        return context


class ContainerListView(ProtectedViewMixin, ListView):
    template_name = "content/container_list.html"
    model = SectionContainer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['challenge_to_completed'] = \
            ContainerAttempt.get_cont_to_num_completed(
                self.request.user, Challenge.get_content_type())
        context['problemset_to_completed'] = \
            ContainerAttempt.get_cont_to_num_completed(
                self.request.user, ProblemSet.get_content_type())

        context['visible_challenges'] = {
            challenge.pk for challenge in
            Challenge.get_visible_for_user(self.request.user)
        }
        context['visible_problemsets'] = {
            problemset.pk for problemset in
            ProblemSet.get_visible_for_user(self.request.user)
        }
        return context

    def get_queryset(self):
        section = (self.request.session.get('section', None) or
                   self.request.user.section)
        visible_containers = self.model.get_visible_for_user(self.request.user)
        return visible_containers\
            .filter(section=section)\
            .filter(open_on__lt=now())\
            .prefetch_related('container', 'container__challenge_set',
                              'container__problemset_set')

# class ChallengeSaveContentOrder(SingleObjectMixin, View):
#     model = Challenge
#
#     def post(self, request, *args, **kwargs):
#         order = 1
#
#         for item_pk in request.POST.getlist('order'):
#             item = ContentObject.objects.get(pk=item_pk)
#             try:
#                 item_link = ContentSequence.objects.get(
#                     challenge=self.get_object(), content_module=item)
#             except ContentSequence.DoesNotExist:
#                 item_link = ContentSequence(
#                     challenge=self.get_object(), content_module=item)
#             item_link.order = order
#             item_link.save()
#             order += 1
#
#         return HttpResponse(json.dumps({'success': True}),
#                             mimetype='application/json')