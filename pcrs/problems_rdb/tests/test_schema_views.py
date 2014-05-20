from django import test
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from problems_rdb.models import Dataset, Schema
from tests.ViewTestMixins import CourseStaffViewTestMixin


@override_settings(RDB_DATABASE='crs_data_test')
class TestSchemaListView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('schema_list')
    template = 'schema_list'

    def test_queryset(self):
        def1 = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        def2 = 'CREATE TABLE WEATHER2(sunny bool, temp int);'
        Schema.objects.create(name='schema1', definition=def1)
        Schema.objects.create(name='schema2', definition=def2)
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['object_list'],
                                 [repr(s) for s in Schema.objects.all()])

    def tearDown(self):
        Schema.objects.all().delete()
        self.assertEqual(0, Schema.objects.count())
        self.assertEqual(0, Dataset.objects.count())


@override_settings(RDB_DATABASE='crs_data_test')
class TestSchemaDetailView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('schema_view', kwargs={'pk': 1})
    template = 'problems_rdb/rdb_detail'

    def setUp(self):
        self.valid_schema_def = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        self.schema = Schema.objects.create(pk=1, name='test_schema',
                                            definition=self.valid_schema_def)
        CourseStaffViewTestMixin.setUp(self)

    def tearDown(self):
        Schema.objects.all().delete()
        self.assertEqual(0, Schema.objects.count())
        self.assertEqual(0, Dataset.objects.count())


@override_settings(RDB_DATABASE='crs_data_test')
class TestSchemaCreateView(CourseStaffViewTestMixin, test.TestCase):
    url = reverse('schema_create')
    successful_redirect_url = reverse('schema_list')
    template = 'pcrs/crispy_form.html'

    @classmethod
    def setUpClass(cls):
        cls.valid_schema_def = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        cls.invalid_schema_def = 'CREATE TABLE WEATHER;'

        cls.valid_dataset_def = 'INSERT INTO WEATHER VALUES(true, 10);'
        cls.invalid_dataset_def = 'INSERT INTO WEATHER (true, 10);'

    def tearDown(self):
        Schema.objects.all().delete()

    def test_new_valid(self):
        """
        Test new schema creation with valid name and definition.
        """

        post_data = {
            'name': 'new_name',
            'definition': self.valid_schema_def,
        }

        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.successful_redirect_url)

        self.assertEqual(1, Schema.objects.count())
        schema = Schema.objects.all()[0]
        self.assertEqual('new_name', schema.name)
        self.assertEqual(self.valid_schema_def, schema.definition)

    def form_invalid(self, response):
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertEqual(0, Schema.objects.count())

    def test_new_no_schema_name(self):
        """
        Test new schema and datasets creation with no schema name.
        """

        post_data = {
            'name': '',
            'definition': self.invalid_schema_def,
        }

        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'name',
                             ['This field is required.'])

    def test_new_invalid_name(self):
        """
        Test new schema and datasets creation with invalid schema name.
        """

        post_data = {
            'name': 'new name',
            'definition': self.invalid_schema_def
        }

        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'name',
                             ['Enter a valid \'slug\' consisting of letters,'
                              ' numbers, underscores or hyphens.'])

    def test_new_no_definition(self):
        """
        Test new schema and datasets creation with invalid schema definition.
        """

        post_data = {
            'name': 'new_name',
            'definition': ''
        }
        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'definition',
                             'This field is required.')

    def test_new_invalid_definition(self):
        """
        Test new schema and datasets creation with invalid schema definition.
        """

        post_data = {
            'name': 'new_name',
            'definition': self.invalid_schema_def
        }

        response = self.client.post(self.url, post_data)
        self.form_invalid(response)
        self.assertFormError(response, 'form', 'definition',
                             'Schema definition is invalid.')