from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView

from problems.views import SubmissionViewMixin
from problems_code.forms import SubmissionForm
from problems_code.models import Problem, Submission
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin, CreateView):
    """
    Create a submission for a coding problem.
    """
    template_name = 'problems_code/submission.html'
    model = Submission
    form_class = SubmissionForm

    def get_initial(self):
        problem = get_object_or_404(Problem,
                                    pk=self.kwargs.get('problem'))
        return {
            'problem': problem,
            'student': self.request.user,
            'section': self.get_section(),
        }

    def get_success_url(self):
        return reverse('coding_problem_submit',
                        kwargs={'problem': self.object.problem.pk})

    def form_valid(self, form):
        form.cleaned_data['section'] = self.get_section()
        submission = form.save()
        submission.run_testcases()
        submission.set_score()

        return self.render_to_response(self.get_context_data(form=form))


class TestCaseView(CourseStaffViewMixin):
    """
    Base view for creating and updating testcases for a problem.
    """
    template_name = 'problems/testcase_form.html'

    def get_problem(self):
        return get_object_or_404(self.model.get_problem_class(),
                                 pk=self.kwargs.get('problem'))

    def get_initial(self):
        return {
            'problem': self.get_problem(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.get_problem()
        return context

    def get_queryset(self):
        if self.request.user.is_student:
            allowed_problems = self.model.get_problem_class().objects.filter(
                visibility='open')
        elif self.request.user.is_ta:
            allowed_problems = self.model.get_problem_class().objects.exclude(
                visibility='closed')
        else:
            allowed_problems = self.model.get_problem_class().objects.all()
        return self.model.objects.filter(problem__in=allowed_problems)


class TestCaseCreateManyView(TestCaseView, CreateView):
    """
    Create new testcases for a coding problem.
    """
    def get_success_url(self):
        return '{}/testcase'.format(self.object.problem.get_absolute_url())


class TestCaseCreateView(TestCaseView, CreateView):
    """
    Create a new testcase for a coding problem.
    """
    def get_success_url(self):
        return self.object.problem.get_absolute_url()


class TestCaseUpdateView(TestCaseView, UpdateView):
    """
    Update an existing testcase for a coding problem.
    """
    def get_success_url(self):
        return self.object.problem.get_absolute_url()


class TestCaseDeleteView(CourseStaffViewMixin, DeleteView):
    """
    Delete a testcase.
    """
    template_name = 'problems/testcase_check_delete.html'

    def get_success_url(self):
       return self.object.problem.get_absolute_url()