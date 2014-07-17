from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from problems_timed.models import Problem, Submission
from django.views.generic.detail import SingleObjectMixin


@csrf_exempt
def problem_attempt(request, problem_pk):
    
    user = request.user
    section = request.user.section
    problem = Problem.objects.get(pk=problem_pk)
    total = Submission.objects.filter(user=user, section=section, problem=problem).count()
    
    if total >= problem.attempts:
        return HttpResponseForbidden()
#        raise Exception("(user: {}, section: {}, problem: {} -- Allowed attempts exceeded.)"
#                        .format(user.username, section.section_id, problem.pk))
    
    attempt_submission = Submission.objects.create(user=user, section=section,
                                                   problem=problem, attempt=total+1)
    attempt_submission.save()

    return HttpResponse()
