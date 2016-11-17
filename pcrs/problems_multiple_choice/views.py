import json
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, FormView, \
    View
from django.views.generic.detail import SingleObjectMixin
from pcrs.generic_views import GenericItemCreateView

import problems.views
from problems_multiple_choice.forms import SubmissionForm, OptionForm

from problems_multiple_choice.models import (Problem, Option, OptionSelection,
                                             Submission)
from users.section_views import SectionViewMixin
from users.views import UserViewMixin
from users.views_mixins import CourseStaffViewMixin, ProtectedViewMixin

import logging
from django.utils.timezone import localtime



class ProblemCloneView(problems.views.ProblemCloneView):
    """
    Clone an existing problem, with its options.
    """
    template_name = "problems_multiple_choice/problem_form.html"

    def form_valid(self, form):
        new_problem = form.save()
        # copy the testcases
        for option in self.get_object().option_set.all():
            option.pk = None
            option.problem = new_problem
            option.save(force_insert=True)
        return redirect(new_problem.get_absolute_url())

class MCProblemExportView(DetailView):
    """
    Export an existing problem and its testcases into JSON file.
    """
    def post(self, request, pk):
        problem = self.get_object()
        serialized = serializers.serialize('json',
                                           [problem] + list(problem.option_set.all())
                                           )
        with open('../{}.json'.format(problem.name), 'w') as json_file:
            json_file.write(serialized)
        return redirect(self.get_object().get_absolute_url())

class ProblemCreateAndAddOptView(CourseStaffViewMixin, CreateView):
    model = Problem

    def get_success_url(self):
        return reverse('mc_problem_add_option',
                       kwargs={'problem': self.object.pk})


class OptionView(problems.views.TestCaseView):
    model = Option
    form_class = OptionForm
    template_name = 'problems_multiple_choice/option_form.html'

    def get_success_url(self):
        return reverse('mc_problem_add_option',
                       kwargs={'problem': self.object.problem.pk})


class OptionCreateView(OptionView, GenericItemCreateView):
    """
    Create a new multiple choice answer option.
    """
    def get_success_url(self):
        return reverse('mc_problem_update',
                       kwargs={'pk': self.object.problem.pk})


class OptionsCreateView(OptionView, GenericItemCreateView):
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


class SubmissionViewMixin(problems.views.SubmissionViewMixin, FormView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'problems_multiple_choice/submission.html'

    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        """
        problem = self.get_problem()
        self.submission = self.model.objects.create(
            problem=problem, user=request.user, section=self.get_section())

        selected_options = Option.objects.filter(
            pk__in=request.POST.getlist('submission', None))
        all_options = problem.option_set.all()
        correct_options = all_options.filter(is_correct=True)

        for option in all_options:
            selected = option in selected_options
            if problem.no_correct_response:
                correct = True
            else:
                correct = (option in correct_options and
                           option in selected_options) or \
                          (not option in correct_options and
                           not option in selected_options)
            OptionSelection(submission=self.submission, option=option,
                            is_correct=correct, was_selected=selected).save()
        self.submission.set_score()
        return []


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin, SingleObjectMixin,
                     FormView, UserViewMixin):
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


class SubmissionAsyncView(SubmissionViewMixin, SingleObjectMixin, View,
                          UserViewMixin):
    """
    Create a submission for a problem asynchronously.
    """
    def post(self, request, *args, **kwargs):
        try:
            results = self.record_submission(request)
        except AttributeError:       # Anonymous user
            return HttpResponse(json.dumps({
                                'error_msg': "Your session has expired. Please reload the page (to re-authenticate) before submitting again.",
                                'score': 0,
                                'max_score': 1,
                                'sub_pk': None,
                                'best': False,
                                'past_dead_line': False
                                }), mimetype='application/json')

        problem = self.get_problem()
        user, section = self.get_user(), self.get_section()
        try:
            deadline = problem.challenge.quest.sectionquest_set\
                .get(section=section).due_on
        except:   # content.models.DoesNotExist
            deadline = None

        logger = logging.getLogger('activity.logging')
        logger.info(str(localtime(self.submission.timestamp)) + " | " +
                    str(user) + " | Submit " +
                    str(problem.get_problem_type_name()) + " " +
                    str(problem.pk))

        return HttpResponse(json.dumps({
            'score': self.submission.score,
            'max_score': problem.max_score,
            'best': self.submission.has_best_score,
            'sub_pk': self.submission.pk,
            'past_dead_line': deadline and self.submission.timestamp > deadline,
            }), mimetype='application/json')


class SubmissionMCHistoryAsyncView(SubmissionViewMixin,  SingleObjectMixin,
                                   UserViewMixin, View):

    def post(self, request, *args, **kwargs):
        returnable = []

        problem = self.get_problem()

        user, section = self.get_user(), self.get_section()

        try:
            deadline = problem.challenge.quest.sectionquest_set\
                .get(section=section).due_on
        except:   # Not a valid section
            deadline = False
        try:
            best_score = self.model.objects\
                .filter(user=user, problem=problem, has_best_score=True).latest("id").score
        except self.model.DoesNotExist:
            best_score = -1

        data = self.model.get_submission_class().objects\
            .filter(user=user, problem=problem)\
            .prefetch_related('optionselection_set__option')

        for sub in data:
            options_list = [
                {
                    'selected': option.was_selected,
                    'option': option.option.answer_text
                }
                for option in sub.optionselection_set.all()]

            returnable.append({
                'sub_time': sub.timestamp.isoformat(),
                'score': sub.score,
                'out_of': problem.max_score,
                'best': sub.has_best_score and \
                        ((not deadline) or sub.timestamp < deadline),
                'past_dead_line': deadline and sub.timestamp > deadline,
                'problem_pk': problem.pk,
                'sub_pk': sub.pk,
                'options': options_list
            })

        return HttpResponse(json.dumps(returnable), mimetype='application/json')
