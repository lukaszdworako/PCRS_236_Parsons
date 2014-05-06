from django.views.generic import FormView
from users.forms import SectionSelectionForm

from users.views_mixins import ProtectedViewMixin


class SectionChangeView(ProtectedViewMixin, FormView):
    """
    A view to select the section for the session.
    """
    form_class = SectionSelectionForm
    referrer = None
    template_name = 'pcrs/crispy_form.html'

    def get_initial(self):
        return {'section': self.request.session.get('section', None)}

    def form_valid(self, form):
        self.request.session['section'] = form.cleaned_data['section']
        return self.render_to_response(self.get_context_data(form=form))
