from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from problems_rating.models import Submission

from users.views import UserViewMixin
from problems.views import SubmissionViewMixin
from users.views_mixins import ProtectedViewMixin


class SubmissionView(ProtectedViewMixin, SubmissionViewMixin, FormView,
                     SingleObjectMixin , UserViewMixin):
    model = Submission
    template_name = 'problems_rating/submission.html'
    object = None

    def get_success_url(self):
        return reverse('rating_list')
    
    def get_request_info(self, request):
        info = {'user': request.user, 'section': request.user.section, 'problem': self.get_problem()}
        return info
    
    def get(self, request, *args, **kwargs):
        info = self.get_request_info(request)
        context = self.get_context_data()
        
        try:
            prev_sub = Submission.objects.filter(user=info['user'], section=info['section'], problem=info['problem'])[:1].get()
            context['previous_rating'] = True
            context['previous_rating_value'] = prev_sub.submission
        except ObjectDoesNotExist:
            context['previous_rating'] = False
        
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        info = self.get_request_info(request)
        
        try:
            sub = Submission.objects.filter(user=info['user'], section=info['section'], problem=info['problem'])[:1].get()
        except ObjectDoesNotExist:
            sub = Submission.objects.create(user=info['user'], section=info['section'], problem=info['problem'])
        
        sub.set_score(request.REQUEST['rating'])
        
        return HttpResponseRedirect('/content/quests')
