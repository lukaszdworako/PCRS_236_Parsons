import json
from django import test
from django.core.exceptions import ValidationError
from django.test.utils import override_settings

from problems_rdb.models import Dataset, Schema


@override_settings(RDB_DATABASE='crs_data_test')
class TestSchemaSave(test.TestCase):
    """
    Test the clean_fields method for Schema model.
    """

    @classmethod
    def setUpClass(cls):
        cls.valid_schema = 'CREATE TABLE WEATHER(sunny bool, temp int);'
        cls.invalid_schema = 'CREATE TABLE WEATHER;'
        cls.db = Schema.get_db()

    def test_schema_valid(self):
        """
        Test creating a schema with valid details.
        """
        schema = Schema(name='test_schema', definition=self.valid_schema)
        try:
            schema.clean_fields()
        except ValidationError:
            self.fail('Validation failed unexpectedly.')
        schema.save()

        schemas = Schema.objects.all()
        self.assertEqual(1, schemas.count())
        schema = schemas[0]

        self.assertEqual('test_schema', schema.name)
        self.assertEqual(self.valid_schema, schema.definition)
        expected_tables = {'weather': ['sunny', 'temp']}
        self.assertEqual(json.dumps(expected_tables), schema.tables)
        expected_representation = '<b>weather</b>(sunny, temp)<br>'
        self.assertEqual(expected_representation, schema.representation)

    def test_schema_invalid(self):
        """
        Test a schema with invalid details.
        """
        schema = Schema(name='test_schema', definition=self.invalid_schema)
        self.assertEqual(0, Schema.objects.all().count())
        self.assertRaises(ValidationError, schema.clean_fields)


@override_settings(RDB_DATABASE='crs_data_test')
class TestDatasetSave(test.TestCase):
    """
    Test the clean_fields method for Dataset model.
    """
    def setUp(self):
        schema = 'CREATE TABLE WEATHER(sunny bool, temperature int);'
        self.schema = Schema.objects.create(name='weather', definition=schema)

        self.valid_dataset = 'INSERT INTO WEATHER values (true, 10);'
        self.invalid_dataset = 'INSERT INTO WEATHER(true, 10);'
        self.db = Schema.get_db()

    def test_dataset_valid_create(self):
        """
        Test creating a dataset with valid details.
        """
        dataset = Dataset(name='today', definition=self.valid_dataset,
                          schema=self.schema)
        try:
            dataset.clean_fields()
        except ValidationError:
            self.fail('Validation failed')
        dataset.save()

        all_datasets = Dataset.objects.all()
        self.assertEqual(1, all_datasets.count())
        self.assertEqual('today', dataset.name)
        self.assertEqual(self.valid_dataset, dataset.definition)

        self.assertTrue(self.db.check_schema_exists('weather_today'))

        # clean-up
        dataset.delete()
        self.assertFalse(self.db.check_schema_exists(dataset.namespace))

    def test_dataset_invalid_create(self):
        """
        Test creating a dataset with invalid details.
        """
        dataset = Dataset(name='yesterday', definition=self.invalid_dataset,
                          schema=self.schema)
        self.assertRaises(ValidationError, dataset.clean_fields)
        self.assertEqual(0, Dataset.objects.all().count())
        self.assertFalse(self.db.check_schema_exists('weather_yesterday'))

    def test_no_schema_create(self):
        """
        Test creating a dataset with invalid schema.
        """
        dataset = Dataset(name='yesterday', definition=self.invalid_dataset)
        self.assertRaises(ValidationError, dataset.clean_fields)
        self.assertEqual(0, Dataset.objects.all().count())
        self.assertFalse(self.db.check_schema_exists('weather_yesterday'))

    def test_schema_invalid_create(self):
        """
        Test creating a dataset with invalid schema.
        """
        dataset = Dataset(name='yesterday', definition=self.invalid_dataset,
                          schema_id=100)
        self.assertRaises(ValidationError, dataset.clean_fields)
        self.assertEqual(0, Dataset.objects.all().count())
        self.assertFalse(self.db.check_schema_exists('weather_yesterday'))

    def test_dataset_delete(self):
        """
        Test deleting a dataset.
        """
        dataset = Dataset.objects.create(name='today',
                                         definition=self.valid_dataset,
                                         schema=self.schema)

        all_datasets = Dataset.objects.all()
        self.assertEqual(1, all_datasets.count())
        self.assertEqual('today', dataset.name)
        self.assertEqual(self.valid_dataset, dataset.definition)
        self.assertTrue(self.db.check_schema_exists('weather_today'))

        dataset.delete()
        self.assertEqual(0, all_datasets.count())
        self.assertFalse(self.db.check_schema_exists(dataset.namespace))