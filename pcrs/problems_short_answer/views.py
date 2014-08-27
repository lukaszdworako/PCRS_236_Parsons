from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, FormView
from django.views.generic.detail import SingleObjectMixin

from problems_short_answer.models import Problem, Submission
from problems_short_answer.forms import SubmissionForm

from users.views import UserViewMixin
from problems.views import SubmissionViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


class ProblemCreateRedirectView(CourseStaffViewMixin, CreateView):
    model = Problem

    def get_success_url(self):
        return reverse('short_answer_update',
                       kwargs={'pk': self.object.pk})

class SubmissionView(ProtectedViewMixin, SubmissionViewMixin,
                     SingleObjectMixin, FormView, UserViewMixin):
    model = Submission
    form_class = SubmissionForm
    template_name = 'problems_short_answer/submission.html'
    object = None

    def get_success_url(self):
        return reverse('rating_list')
    
    def get_request_info(self, request):
        info = {'user': request.user, 'section': request.user.section, 'problem': self.get_problem()}
        return info
    
    def post(self, request, *args, **kwargs):
        info = self.get_request_info(request)
        
        submission = Submission.objects.create(user=info['user'], section=info['section'], problem=info['problem'])
        submission.set_score(request.REQUEST['submission'])
        
        return HttpResponseRedirect('/content/quests')
