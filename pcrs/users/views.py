from django.views.generic import FormView

from users.forms import SettingsForm
from users.views_mixins import ProtectedViewMixin


class UserSettingsView(ProtectedViewMixin, FormView):
    template_name = 'pcrs/crispy_form.html'
    form_class = SettingsForm

    def form_valid(self, form):
        self.request.user.code_style = form.cleaned_data['colour_scheme']
        self.request.user.save()
        return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['colour_scheme'] = self.request.user.code_style
        return initial