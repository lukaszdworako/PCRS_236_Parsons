from django.http import HttpResponse
from django.views.generic import TemplateView

from pcrs.settings import PYTA

from problems.views import SubmissionViewMixin, SubmissionView, SubmissionAsyncView

class PythonSubmissionViewMixin(SubmissionViewMixin):
    def record_submission(self, request):
        """
        Record the submission and return the results of running the testcases.
        Record PyTA output if PYTA is True.
        """
        results, error = super().record_submission(request)
        if PYTA:
            submission_model = self.model.get_submission_class()
            submission_code = request.POST.get('submission', '')
            if submission_code:
                submission = submission_model.objects.filter(user_id=request.user).order_by('-id')[0]
                #PyTA result must always be last
                results.append(submission.run_pyta())
                if "PyTA" in [tag.name for tag in submission.problem.tags.all()]:
                    results.insert(len(results)-1,submission.run_pyta_testcase(results[len(results)-1]))
                    self.object = submission
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
        dropdown_id = request.POST.get('problem_id', 'PyTADropdownError')[12:]
        try:
            submission = submission_model.objects.filter(problem_id=dropdown_id, user_id=request.user).order_by("-id")[0]
        except (IndexError, AttributeError):
            return HttpResponse(status=500)
        if self.model.objects.filter(submission_id=submission.id).exists():
            click_event = self.model.objects.get(submission_id=submission.id)
            click_event.click_count += 1
            click_event.save()
        else:
            self.model.objects.create(submission=submission)
        return HttpResponse(status=204)
