from django.views.generic import DeleteView, ListView, CreateView, UpdateView
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


class GenericItemDetailView:
    """
    A generic detail entry view. Redirect to the item list on success.
    """
    def get_success_url(self):
        return '{}/list'.format(self.model.get_base_url())


class GenericItemCreateView(GenericItemDetailView, CreateView):
    """
    A generic creation view.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'New {thing}'\
            .format(thing=self.model.get_pretty_name())
        return context


class GenericItemUpdateView(GenericItemDetailView, UpdateView):
    """
    A generic update view.
    """


class GenericCourseStaffDeleteView(CourseStaffViewMixin, GenericItemDetailView,
                                   DeleteView):
    """
    A generic Delete view accessible to only the course staff.
    """
    template_name = 'pcrs/check_delete.html'