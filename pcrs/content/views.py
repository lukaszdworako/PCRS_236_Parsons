from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import UpdateView, View, ListView, CreateView, \
    DeleteView, DetailView
from django.db import models


from content.parse_page import parse
from content.forms import ChallengeForm,  ProblemSetForm
from content.models import Challenge, ContentPage, Container, \
    OrderedContainerItem, ProblemSet, ProblemSetProblem
from problems.models import CompletedProblem
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class ChallengeView:
    model = Challenge
    form_class = ChallengeForm
    template_name = 'content/challenge_form.html'

    def get_success_url(self):
        return reverse('challenge_list')


class ChallengeListView(ProtectedViewMixin, ListView):
    model = Challenge
    template_name = 'content/challenge_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Challenges'
        return context


class ChallengeCreateView(CourseStaffViewMixin, ChallengeView, CreateView):
    """
    Create a new Challenge, its ContentPages and ContentObjects.
    """


class ChallengeUpdateView(CourseStaffViewMixin, ChallengeView, UpdateView):
    """
    Update a new Challenge, its ContentPages and ContentObjects.
    """
    def form_invalid(self, form):
        print(form)


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
        return self.get_page().contentsequenceitem_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_page'] = self.get_page()
        return context


class ContainerListView(ProtectedViewMixin, ListView):
    template_name = "content/container_list.html"
    model = Container

    def get_queryset(self):
        container_type = ContentType.objects.get(model='container')

        children_pks = OrderedContainerItem.objects\
            .filter(child_content_type=container_type.id)\
            .values_list('child_object_id', flat=True)
        return Container.objects.filter(~Q(pk__in=set(children_pks)))

    def get_context_data(self, **kwargs):
        challenges = {}
        context = super().get_context_data(**kwargs)
        completed_set = CompletedProblem.get_completed(user=self.request.user)

        for challenge in Challenge.objects.select_related().all():
            problems = challenge.get_all_problems()
            completed = [p for p in problems if p in completed_set]
            challenges[challenge.pk] = [len(completed), len(problems)]
        context['challenges'] = challenges
        return context

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


class ProblemSetCreateView(CourseStaffViewMixin, CreateView):
    model = ProblemSet
    form_class = ProblemSetForm

    def form_valid(self, form):
        self.object = form.save()
        for key, value in form.cleaned_data.items():
            # add all selected problems regardless of type to the problem set
            if key.startswith('problems_'):
                for problem in form.cleaned_data[key]:
                    ProblemSetProblem(problem_set=self.object,
                                      content_object=problem).save()
        return redirect(self.object.get_absolute_url())


class ProblemSetDetailView(ProtectedViewMixin, ListView):
    model = ProblemSetProblem

    def get_problem_set(self):
        return get_object_or_404(ProblemSet,
                                 self.kwargs.get('problemset', None))

    def get_queryset(self):
        return self.model.objects.filter(problem_set_id=1)