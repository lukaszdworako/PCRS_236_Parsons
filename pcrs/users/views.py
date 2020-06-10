from django.views.generic import FormView

from users.forms import SettingsForm, UserForm
from users.section_views import SectionViewMixin
from users.views_mixins import ProtectedViewMixin, CourseStaffViewMixin


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


class UserViewView(CourseStaffViewMixin, FormView):
    """
    A view to select a user to view the pages as.
    """
    template_name = 'pcrs/crispy_form.html'
    form_class = UserForm

    def form_valid(self, form):
        self.request.session['viewing_as'] = form.cleaned_data['user']
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'View pages as'
        return context


class UserViewMixin(SectionViewMixin):
    """
    A mixin for viewing a page as some other user.
    """

    def get_user(self):
        return self.request.session.get('viewing_as', None) or self.request.user

    def get_section(self):
        user = self.get_user()
        section = user.section if user != self.request.user \
                               else super().get_section()
        return section