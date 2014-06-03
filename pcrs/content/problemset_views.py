from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import UpdateView, ListView

from content.forms import ProblemSetForm
from content.models import ProblemSet, ContainerProblem
from pcrs.generic_views import GenericItemListView, GenericItemCreateView
from problems.models import get_problem_labels
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin


class ProblemSetListView(CourseStaffViewMixin, GenericItemListView, ListView):
    """
    List all problem sets.
    """
    model = ProblemSet
    template_name = 'content/challenge_list.html'


class ProblemSetCreateOrUpdateView(CourseStaffViewMixin):
    """
    Create or update a ProblemSet.
    """
    model = ProblemSet
    form_class = ProblemSetForm
    template_name = 'pcrs/crispy_form.html'

    def form_valid(self, form):
        self.object = form.save()
        changed = set(form.changed_data).intersection(set(get_problem_labels()))
        for label in changed:
            # delete all existing problems of this type
            self.object.get_problems_for_type(label).delete()
            # add all selected problems
            for problem in form.cleaned_data[label]:
                ContainerProblem(problem_set=self.object,
                                  content_object=problem).save()
        return redirect(reverse('problem_set_list'))


class ProblemSetCreateView(ProblemSetCreateOrUpdateView, GenericItemCreateView):
    """
    Create a new ProblemSet.
    """


class ProblemSetUpdateView(ProblemSetCreateOrUpdateView, UpdateView):
    """
    Update an existing ProblemSet.
    """
    def get_initial(self):
        initial = super().get_initial()

        # include problems of all types
        for label in get_problem_labels():
            initial[label] = [
                c_type.content_object
                for c_type in self.get_object().get_problems_for_type(label)
            ]
        return initial


class ProblemSetDetailView(ProtectedViewMixin, ListView):
    """
    List the Problems in this ProblemSet.
    """
    model = ContainerProblem
    template_name = 'content/problem_set.html'

    def get_problem_set(self):
        return get_object_or_404(ProblemSet,
                                 pk=self.kwargs.get('problemset', None))

    def get_queryset(self):
        return self.model.objects.filter(problem_set=self.get_problem_set())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem_set'] = self.get_problem_set()
        return context