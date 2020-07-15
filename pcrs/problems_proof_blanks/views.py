import json
import logging
import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import localtime, utc
from django.views.generic import CreateView, FormView, View
from django.views.generic.detail import SingleObjectMixin

from problems_proof_blanks.models import Problem, Submission
from problems_proof_blanks.forms import SubmissionForm
from pcrs.generic_views import GenericItemCreateView
import problems.views
from users.views import UserViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class ProblemCloneView(problems.views.ProblemCloneView):
    def form_valid(self, form):
        new_problem = form.save()
        return redirect(new_problem.get_absolute_url())


class ProblemCreateRedirectView(CourseStaffViewMixin, CreateView):
    model = Problem

    def get_success_url(self):
        return reverse('proof_blanks_update',
                       kwargs={'pk': self.object.pk})

class ProblemCreateAndAddTCView(problems.views.ProblemCreateView):
    """
    Create a new problem and add testcases.
    """
    def get_success_url(self):
        return '{}/feedback'.format(self.object.get_absolute_url())

class SubmissionViewMixin(problems.views.SubmissionViewMixin, FormView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'problems_proof_blanks/submission.html'

    def record_submission(self, request):
        """
        Record the submission and return the results of running the solution code.
        """
        problem = self.get_problem()
        self.submission = self.model.objects.create(problem=problem,
                              user=request.user, section=self.get_section())
        print("## Submission ##")
        submission = {}
        '''
        <QueryDict: {'csrfmiddlewaretoken': ['MZIkJ8Q2vP4upf2xBvzKBBTvCRscvjvhsq1zk6q3jTlVQbzD3wRn2svsmGTzZ1Jx'], 'sub2': ['{"a": "b"}'], 'Submit': ['Submit']}>
        '''
        for key in request.POST:
            if key.split("_")[0] == "submission":
                submission[key.split("_")[1]] = request.POST[key]
        print(submission)
        self.submission.set_score(submission)
        #submission = {}



        return []


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin,
                     SingleObjectMixin, FormView, UserViewMixin):
    object = None

    def post(self, request, *args, **kwargs):
        """
        Record the submission and redisplay the problem submission page,
        with latest submission prefilled.
        """
        form = self.get_form(self.get_form_class())
        results = self.record_submission(request)
        return self.render_to_response(self.get_context_data(form=form, results=results,
                                                             submission=self.submission))


class SubmissionAsyncView(SubmissionViewMixin, SingleObjectMixin, View,
                          UserViewMixin):
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
                                'past_dead_line': False,
                                'message': self.submission.message,
                                }), content_type='application/json')

        problem = self.get_problem()
        user, section = self.get_user(), self.get_section()
        try:
            deadline = problem.challenge.quest.sectionquest_set.get(section=section).due_on
        except:   # content.models.DoesNotExist
            deadline = None

        logger = logging.getLogger('activity.logging')
        logger.info(str(localtime(self.submission.timestamp)) + " | " +
                    str(user) + " | Submit " +
                    str(problem.get_problem_type_name()) + " " +
                    str(problem.pk))

        return HttpResponse(json.dumps({
            'submission': self.submission.submission,
            'score': self.submission.score,
            'max_score': problem.max_score,
            'best': self.submission.has_best_score,
            'sub_pk': self.submission.pk,
            'past_dead_line': deadline and self.submission.timestamp > deadline,
            'message': self.submission.message,
            }), content_type='application/json')


class SubmissionHistoryAsyncView(SubmissionViewMixin, SingleObjectMixin,
                                 UserViewMixin, View):
    def post(self, request, *args, **kwargs):
        problem = self.get_problem()
        user, section = self.get_user(), self.get_section()

        try:
            deadline = problem.challenge.quest.sectionquest_set\
                              .get(section=section).due_on
        except Exception:
            deadline = False

        try:
            best_score = self.model.objects\
                .filter(user=user, problem=problem, has_best_score=True).latest("id").score
        except self.model.DoesNotExist:
            best_score = -1

        data = self.model.objects.filter(user=user, problem=problem)
        returnable = []
        for sub in data:
            returnable.append({
                'sub_time': sub.timestamp.isoformat(),
                'submission': sub.submission,
                'score': sub.score,
                'out_of': problem.max_score,
                'best': sub.has_best_score and \
                        ((not deadline) or sub.timestamp < deadline),
                'past_dead_line': deadline and sub.timestamp > deadline,
                'problem_pk': problem.pk,
                'sub_pk': sub.pk
            })

        return HttpResponse(json.dumps(returnable), content_type='application/json')

class FeedbackCreateView(CourseStaffViewMixin, GenericItemCreateView):
    """
    Base view for creating and updating testcases for a problem.
    """
    template_name = 'problems_proof_blanks/feedback_form.html'

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
        visible_problems = self.get_visible_problems(self.request)
        return self.model.objects.filter(problem__in=visible_problems)

    def get_success_url(self):
        return self.get_problem().get_absolute_url()
