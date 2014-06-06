from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils.timezone import now

from content.forms import ChallengeForm
from content.models import *
from pcrs.generic_views import GenericItemListView, GenericItemCreateView, \
    GenericItemUpdateView
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin
from problems.forms import ProgrammingSubmissionForm
from problems_multiple_choice.forms import SubmissionForm


class ChallengeView:
    model = Challenge
    form_class = ChallengeForm
    template_name = 'pcrs/item_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class ChallengeListView(CourseStaffViewMixin, GenericItemListView):
    model = Challenge
    template_name = 'content/challenge_list.html'


class ChallengeCreateView(CourseStaffViewMixin, ChallengeView,
                          GenericItemCreateView):
    """
    Create a new Challenge, its ContentPages and ContentObjects.
    """


class ChallengeUpdateView(CourseStaffViewMixin, ChallengeView,
                          GenericItemUpdateView):
    """
    Update a new Challenge, its ContentPages and ContentObjects.
    """


class ChallengeStartView(ProtectedViewMixin, DetailView):
    model = Challenge
    template_name = 'content/challenge.html'


class ContentPageView(ProtectedViewMixin, ListView):
    template_name = "content/content_page.html"
    model = ContentSequenceItem

    def get_page(self):
        return get_object_or_404(ContentPage,
                                 order=self.kwargs.get('page', None),
                                 challenge_id=self.kwargs.get('challenge', None))

    def get_queryset(self):
        return self.model.objects\
            .filter(content_page=self.get_page())\
            .prefetch_related('content_object').all()

    def _get_forms(self):
        forms = {}
        for item in self.get_queryset():
            classname = item.content_object.__class__.__name__
            if classname == 'Problem':
                problem = item.content_object
                # generate a submission form for this problem
                # based on the problem class
                module, _ = item.content_object.__module__.split('.')
                f = SubmissionForm(problem=problem) \
                    if module.endswith('multiple_choice') \
                    else ProgrammingSubmissionForm(problem=problem)
                for_type = forms.get(problem.get_problem_type_name(), {})
                for_type[problem.pk] = f
                forms[problem.get_problem_type_name()] = for_type
        return forms

    def _get_submissions(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_page'] = self.get_page()
        context['forms'] = self._get_forms()
        return context


class ContainerListView(ProtectedViewMixin, ListView):
    template_name = "content/container_list.html"
    model = SectionQuest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['challenge_to_completed'] = \
            ContainerAttempt.get_cont_to_num_completed(
                self.request.user, Challenge.get_content_type())


        context['visible_challenges'] = {
            challenge.pk for challenge in
            Challenge.get_visible_for_user(self.request.user)
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
