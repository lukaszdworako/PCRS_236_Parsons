from django import test
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from problems_rdb.models import Dataset, Schema
from tests.ViewTestMixins import CourseStaffViewTestMixin


@override_settings(RDB_DATABASE='crs_data_test')
class TestDatasetDetailView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('dataset_view', kwargs={'schema': 1, 'pk': 1})
    template = 'problems_rdb/rdb_detail'

    def setUp(self):
        valid_schema_def = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        valid_data = 'INSERT INTO WEATHER VALUES(true, 15);'

        schema = Schema.objects.create(pk=1, name='test_schema',
                                       definition=valid_schema_def)
        Dataset.objects.create(pk=1, name='test_ds1',
                               definition=valid_data, schema=schema)
        CourseStaffViewTestMixin.setUp(self)

    def tearDown(self):
        Schema.objects.all().delete()


@override_settings(RDB_DATABASE='crs_data_test')
class TestDatasetCreateView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('dataset_create', kwargs={'schema': 1})
    template = 'problems_rdb/dataset_form.html'
    successful_redirect_url = reverse('schema_view', kwargs={'pk': 1})

    def setUp(self):
        self.valid_schema_def = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        self.schema = Schema.objects.create(pk=1, name='test_schema',
                                            definition=self.valid_schema_def)
        self.valid_dataset_def = 'INSERT INTO WEATHER VALUES(true, 10);'
        self.invalid_dataset_def = 'INSERT INTO WEATHER (true, 10);'

        CourseStaffViewTestMixin.setUp(self)

    def tearDown(self):
        Schema.objects.all().delete()

    def form_invalid(self, response):
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertEqual(0, Dataset.objects.count())

    def test_new_valid(self):
        """
        Test new dataset creation with valid data.
        """

        post_data = {
            'name': 'new_name',
            'definition': self.valid_dataset_def,
            'schema': '1'
        }

        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, Dataset.objects.count())
        dataset = Dataset.objects.all()[0]
        self.assertEqual('new_name', dataset.name)
        self.assertEqual(self.valid_dataset_def, dataset.definition)
        self.assertEqual(self.schema, dataset.schema)

    def test_new_no_schema(self):
        """
        Test new dataset creation with no schema.
        """

        post_data = {
            'name': 'name',
            'definition': self.valid_dataset_def,
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'schema',
                             ['This field is required.'])

    def test_new_invalid_schema(self):
        """
        Test new dataset creation with invalid schema.
        """

        post_data = {
            'name': 'name',
            'definition': self.valid_dataset_def,
            'schema': '100'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        error = ['Select a valid choice. '
                 'That choice is not one of the available choices.']
        self.assertFormError(response, 'form', 'schema', error)

    def test_new_no_name(self):
        """
        Test new dataset creation with no name.
        """

        post_data = {
            'definition': self.valid_dataset_def,
            'schema': '1'
        }

        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'name',
                             ['This field is required.'])

    def test_new_invalid_name(self):
        """
        Test new dataset creation with invalid name.
        """

        post_data = {
            'name': 'space not allowed',
            'definition': self.valid_dataset_def,
            'schema': '1'
        }

        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'name',
                             ['Enter a valid \'slug\' consisting of letters,'
                              ' numbers, underscores or hyphens.'])

    def test_new_no_definition(self):
        """
        Test new dataset creation with no data definition.
        """

        post_data = {
            'name': 'new_name',
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'definition',
                             ['This field is required.'])

    def test_new_invalid_definition(self):
        """
        Test new dataset creation with invalid data.
        """

        post_data = {
            'name': 'new_name',
            'definition': self.invalid_dataset_def,
            'schema': '1'
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'definition',
                             ['Dataset definition is invalid.'])