import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, \
    View
from django.views.generic.detail import SingleObjectMixin
import problems
from problems.views import SubmissionViewMixin, TestCaseView

from problems_multiple_choice.forms import SubmissionForm, OptionForm

from problems_multiple_choice.models import (Problem, Option, OptionSelection,
                                             Submission)
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin


class ProblemCreateAndAddOptView(CourseStaffViewMixin, CreateView):
    model = Problem

    def get_success_url(self):
        return reverse('mc_problem_add_option',
                       kwargs={'problem': self.object.pk})


class OptionView(TestCaseView):
    model = Option
    form_class = OptionForm
    template_name = 'problems_multiple_choice/option_form.html'

    def get_success_url(self):
        return reverse('mc_problem_add_option',
                       kwargs={'problem': self.object.problem.pk})


class OptionCreateView(OptionView, CreateView):
    """
    Create a new multiple choice answer option.
    """
    def get_success_url(self):
        return reverse('mc_problem_update',
                       kwargs={'pk': self.object.problem.pk})


class OptionsCreateView(OptionView, CreateView):
    """
    Create new multiple choice answer options.
    """


class OptionUpdateView(OptionView, UpdateView):
    """
    Edit an existing multiple choice answer option.
    """
    def get_success_url(self):
        return reverse('mc_problem_update',
                       kwargs={'pk': self.object.problem.pk})


class OptionDeleteView(OptionView, DeleteView):
    """
    Delete an option.
    """
    model = Option
    template_name = 'problems/testcase_check_delete.html'

    def get_success_url(self):
        return reverse('mc_problem_update',
                       kwargs={'pk': self.kwargs.get('problem')})


class SubmissionView_(ProtectedViewMixin, SubmissionViewMixin, FormView):
    """
    Create a submission for a coding problem by an instructor.
    """
    template_name = 'problems_multiple_choice/submission.html'
    model = Submission
    form_class = SubmissionForm

    def get_success_url(self):
        return reverse('mc_problem_submit',
                        kwargs={'pk': self.get_problem().pk})


    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST, **self.get_form_kwargs())
        self.object = self.get_problem()

        if form.is_valid():
            submission = Submission.objects.create(
                problem=self.object, student=request.user,
                section=request.user.section)

            all_options = self.object.option_set.all()
            correct_options = all_options.filter(is_correct=True)

            for option in all_options:
                correct = (option in correct_options and
                           option in form.cleaned_data['options']) or \
                          (not option in correct_options and
                           not option in form.cleaned_data['options'])
                submission.score += int(correct)
                OptionSelection(submission=submission, option=option,
                                is_correct=correct).save()
            submission.save()

        return self.render_to_response(self.get_context_data(form=form))


class SubmissionViewMixin(problems.views.SubmissionViewMixin):
    model = Submission
    template_name = 'problems_multiple_choice/submission.html'

    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        """
        problem = self.get_problem()
        self.submission = self.model.objects.create(
            problem=problem, student=request.user, section=request.user.section)

        form = self.get_form(self.get_form_class())

        form.full_clean()
        selected_options = form.cleaned_data['options']
        all_options = problem.option_set.all()
        correct_options = all_options.filter(is_correct=True)

        for option in all_options:
            selected = option in selected_options
            correct = (option in correct_options and
                       option in selected_options) or \
                      (not option in correct_options and
                       not option in selected_options)
            self.submission.score += int(correct)
            OptionSelection(submission=self.submission, option=option,
                            is_correct=correct, was_selected=selected).save()
        self.submission.save()
        return []


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin, SingleObjectMixin,
                     FormView):
    """
    Create a submission for a problem.
    """
    form_class = SubmissionForm
    object = None

    def post(self, request, *args, **kwargs):
        """
        Record the submission and redisplay the problem submission page,
        with latest submission prefilled.
        """
        form = self.get_form(self.get_form_class())
        results = self.record_submission(request)
        return self.render_to_response(
            self.get_context_data(form=form, results=results,
                                  submission=self.submission))


class SubmissionAsyncView(SubmissionViewMixin, View):
    """
    Create a submission for a problem asynchronously.
    """
    def post(self, request, *args, **kwargs):
        results = self.record_submission(request)
        return HttpResponse(json.dumps(results), mimetype='application/json')