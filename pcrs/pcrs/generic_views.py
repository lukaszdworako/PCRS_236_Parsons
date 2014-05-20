from django.views.generic import DeleteView, ListView, CreateView
from users.views_mixins import CourseStaffViewMixin


class GenericItemListView(ListView):
    """
    A generic List View.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '{thing}s'\
            .format(thing=self.model.get_pretty_name())
        return context


class GenericItemCreateView(CreateView):
    """
    A generic List View.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'New {thing}'\
            .format(thing=self.model.get_pretty_name())
        return context


class GenericCourseStaffDeleteView(CourseStaffViewMixin, DeleteView):
    """
    A generic Delete view accessible to only the course staff.
    """
    template_name = 'pcrs/check_delete.html'