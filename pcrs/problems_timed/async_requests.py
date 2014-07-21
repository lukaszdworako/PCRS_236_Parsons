import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from problems_timed.models import Problem, Submission
from django.views.generic.detail import SingleObjectMixin
from users.views_mixins import CourseStaffViewMixin


class AsyncAttempt:
    
    @csrf_exempt
    def problem_attempt(request, problem_pk):
        
        # check if user is logged in
        try:
            user = request.user
            section = request.user.section
        except AttributeError:
            return HttpResponseForbidden()

        problem = Problem.objects.get(pk=problem_pk)
        total = Submission.objects.filter(user=user, section=section,
                                          problem=problem).count()

        # check if user has attempts remaining
        # only staff can submit an attempt if problem is not open
        if (((not problem.is_open()) and (not request.user.is_staff)) or
            (total >= problem.attempts)):
            return HttpResponseForbidden()
        
        attempt_submission = Submission.objects.create(user=user, section=section,
                                                       problem=problem, attempt=total+1)
        attempt_submission.save()
        
        return HttpResponse()

class AsyncDownload:
    
    @csrf_exempt
    def download_submissions(request, problem_pk):
        
        if not request.user.is_staff:
            return HttpResponseForbidden()
        
        problem = Problem.objects.get(pk=problem_pk)
        submissions = Submission.objects.filter(problem=problem).order_by('id')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="submissions.csv"'
        
        writer = csv.writer(response)
        
        headers = ['user_id', 'section_id', 'timestamp', 'timestamp_complete',
                   'attempt', 'score', 'score_max', 'percent', 'has_best_score',
                   'submission', 'terms_list_student', 'terms_list_problem',
                   'terms_match', 'terms_miss']
        writer.writerow(headers)
        
        for sub in submissions:
            row = []
            for title in headers:
                row.append(getattr(sub, title))
            writer.writerow(row)
        return response
