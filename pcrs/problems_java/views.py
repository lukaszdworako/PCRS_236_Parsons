from editor.views import EditorView
from .models import *

class JavaEditorVisualizeView(EditorView):
    """
    View a given submission in the visualizer
    """
    def get_form_kwargs(self):
        submission = Submission.objects.get(pk=self.kwargs['pk'])

        code = submission.fuseStudentCodeIntoStarterCode()
        code = submission.removeTags(code)

        kwargs = super().get_form_kwargs()
        kwargs['initial_code'] = code
        return kwargs

