import json
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.generic import FormView, View
from django.views.generic.detail import SingleObjectMixin

import problems.views
from problems_rating.forms import SubmissionForm
from problems_rating.models import Submission

from users.views import UserViewMixin
from users.views_mixins import ProtectedViewMixin

import logging
from django.utils.timezone import localtime


class SubmissionViewMixin(problems.views.SubmissionViewMixin, FormView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'problems_rating/submission.html'

    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        """
        info = {'user': request.user, 'section': request.user.section, 'problem': self.get_problem()}
        try:
            self.submission = Submission.objects.filter(user=info['user'], section=info['section'], problem=info['problem'])[:1].get()
        except ObjectDoesNotExist:
            self.submission = Submission.objects.create(user=info['user'], section=info['section'], problem=info['problem'])
        

        # This does not exist -- javascript sends what?
        # Go back to the beginning (javascript): how do you pull the value out of a radio button?
        self.submission.set_score(request.POST['rating'])
        return []


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin, SingleObjectMixin,
                     FormView, UserViewMixin):
    form_class = SubmissionForm
    object = None

    def get(self, request, *args, **kwargs):
        info = {'user': request.user, 'section': request.user.section, 'problem': self.get_problem()}
        context = self.get_context_data()
        
        try:
            prev_sub = Submission.objects.filter(user=info['user'], section=info['section'], problem=info['problem'])[:1].get()
            context['previous_rating'] = True
            context['previous_rating_value'] = prev_sub.submission
        except ObjectDoesNotExist:
            context['previous_rating'] = False
        
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        """
        Record the submission and redisplay the problem submission page,
        with latest submission prefilled.
        """
        form = self.get_form(self.get_form_class())
        results = self.record_submission(request)
        context = self.get_context_data(form=form, results=results, submission=self.submission)
        context['previous_rating'] = True
        context['previous_rating_value'] = request.REQUEST['rating']
        return self.render_to_response(context)


class SubmissionAsyncView(SubmissionViewMixin, SingleObjectMixin, View,
                          UserViewMixin):
    """
    Create a submission for a problem asynchronously.
    """
    def post(self, request, *args, **kwargs):
        results = self.record_submission(request)

        problem = self.get_problem()
        user, section = self.get_user(), self.get_section()
        deadline = problem.challenge.quest.sectionquest_set\
            .get(section=section).due_on

        logger = logging.getLogger('activity.logging')
        logger.info(str(localtime(self.submission.timestamp)) + " | " +
                    str(user) + " | Submit " +
                    str(problem.get_problem_type_name()) + " " +
                    str(problem.pk))

        # context['previous_rating'] = True
        # context['previous_rating_value'] = request.REQUEST['rating']

        return HttpResponse(json.dumps({
            'sub_pk': self.submission.pk,
            'past_dead_line': deadline and self.submission.timestamp > deadline,
        }
        ), mimetype='application/json')
