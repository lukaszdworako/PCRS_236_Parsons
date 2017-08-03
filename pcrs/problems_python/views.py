from django.http import HttpResponse
from django.views.generic import TemplateView

from pcrs.settings_local import PYTA

from problems.views import SubmissionViewMixin, SubmissionView, SubmissionAsyncView

class PythonSubmissionViewMixin(SubmissionViewMixin):
    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        Record PyTA output if PYTA is True.
        """
        results, error = super().record_submission(request)
        if (PYTA):
            submission_model = self.model.get_submission_class()
            submission_code = request.POST.get('submission', '')
            if submission_code:
                submission = submission_model.objects.filter(user_id=request.user).order_by('-id')[0]
                #PyTA result must always be last
                results.append(submission.run_pyta())
        return results, error

class PythonSubmissionView(SubmissionView, PythonSubmissionViewMixin):
    """
    Create a submission for a python problem.
    """
    def record_submission(self, request):
        return PythonSubmissionViewMixin.record_submission(self,request)

class PythonSubmissionAsyncView(SubmissionAsyncView, PythonSubmissionViewMixin):
    """
    Create a submission for a python problem asynchronously.
    """
    def record_submission(self, request):
        return PythonSubmissionViewMixin.record_submission(self,request)

class PyTAClickEventView(TemplateView):
    """
    Create a PyTAClickEvent for a submission.
    """
    model = None
    def post(self, request, *args, **kwargs):
        submission_model = self.model.get_submission_class()
        recent_submission = submission_model.objects.filter(user_id=request.user).order_by('-id')[0]
        if self.model.objects.filter(submission_id=recent_submission.id).exists():
            clickevent = self.model.objects.get(submission=recent_submission.id)
            clickevent.click_count += 1
            clickevent.save()
        else:
            clickevent = self.model.objects.create(submission=recent_submission)
        return HttpResponse(status=204)
