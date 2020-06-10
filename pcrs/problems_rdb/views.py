from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  TemplateView)
from django.views.generic.base import RedirectView

from pcrs.generic_views import GenericItemListView, GenericItemCreateView
from problems.views import TestCaseView

from users.views_mixins import CourseStaffViewMixin
from problems_rdb.forms import SchemaForm, DatasetForm
from problems_rdb.models import Schema, Dataset


class SchemaView(CourseStaffViewMixin):
    """
    Base Schema view.
    """
    model = Schema

    def get_success_url(self):
        return reverse('schema_list')


class SchemaListView(SchemaView, GenericItemListView):
    """
    List schemas.
    """
    template_name = 'pcrs/item_list.html'


class SchemaCreateView(SchemaView, GenericItemCreateView):
    """
    Create a new schema.
    """
    form_class = SchemaForm
    template_name = 'pcrs/item_form.html'


class SchemaCreateAndAddDatasetView(SchemaCreateView):
    def get_success_url(self):
        return '{}/dataset'.format(self.object.get_absolute_url())


class SchemaDetailView(SchemaView, DetailView):
    """
    View an existing schema.
    """
    template_name = 'problems_rdb/schema_detail.html'


class SchemaDeleteView(SchemaView, DeleteView):
    """
    Delete an existing schema.
    """
    template_name = 'problems_rdb/schema_check_delete.html'


class DatasetView(CourseStaffViewMixin):
    """
    Base Dataset view.
    """
    model = Dataset

    def get_schema(self):
        return get_object_or_404(Schema, pk=self.kwargs.get('schema'))

    def get_initial(self):
            return {
                'schema': self.get_schema(),
            }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema'] = self.get_schema()
        return context

    def get_success_url(self):
        return self.get_schema().get_absolute_url()


class DatasetCreateView(DatasetView, GenericItemCreateView):
    """
    Create a new dataset.
    """
    template_name = 'problems_rdb/dataset_form.html'
    form_class = DatasetForm


class DatasetsCreateView(DatasetCreateView):
    def get_success_url(self):
        return '{}/dataset'.format(self.object.schema.get_absolute_url())


class DatasetDetailView(DatasetView, DetailView):
    """
    View an existing dataset.
    """
    template_name = 'problems_rdb/dataset_detail.html'


class DatasetDeleteView(DatasetView, DeleteView):
    """
    Delete an existing dataset.
    """
    template_name = 'problems_rdb/dataset_check_delete.html'


class RDBTestCaseView(TestCaseView, GenericItemCreateView):
    """
    Base view for creating and updating testcases for an RDB problem.
    """

    def get_schema(self):
        return self.get_problem().schema

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # the testcases will be limited to the problem schema
        kwargs['schema'] = self.get_schema()
        return kwargs


class RDBTestCaseCreateView(RDBTestCaseView):
    """
    Create a new TestCase for an RDB problem.
    """


class RDBTestCaseCreateManyView(RDBTestCaseView):
    """
    Create new TestCases for an RDB problem.
    """
    def get_success_url(self):
        return '{}/testcase'.format(self.get_problem().get_absolute_url())


class RDBTestCaseEditRedirectView(RedirectView, RDBTestCaseView):
    def get_redirect_url(self, *args, **kwargs):
        testcase = get_object_or_404(self.model, pk=kwargs['pk'])
        return testcase.dataset.get_absolute_url()


class DocumentationView(CourseStaffViewMixin, TemplateView):
    """
    RDB instructor documentation page.
    """
    template_name = 'problems_rdb/docs.html'
