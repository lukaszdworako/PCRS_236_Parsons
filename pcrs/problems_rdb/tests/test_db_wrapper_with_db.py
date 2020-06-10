from collections import OrderedDict

from django import test
from django.test.utils import override_settings
from problems_rdb.models import Schema


@override_settings(RDB_DATABASE='crs_data_test')
class TestSchemaDetails(test.TestCase):
    def test_table(self):
        schema_def = 'CREATE TABLE a (a1 int, a2 int);'
        with Schema.get_db() as db:
            info = db.get_information(schema_def)

        self.assertIsNotNone(info.get('tables', None))
        self.assertEqual(OrderedDict({'a': ['a1', 'a2']}), info['tables'])
        self.assertEqual({}, info.get('pkeys', None))
        self.assertEqual([], info.get('fkeys', None))

    def test_table_with_pk(self):
        schema_def = 'CREATE TABLE a (a1 int primary key, a2 int);'
        with Schema.get_db() as db:
            info = db.get_information(schema_def)
            self.assertIsNotNone(info.get('tables'), None)
        self.assertEqual(OrderedDict({'a': ['a1', 'a2']}), info['tables'])
        self.assertIsNotNone(info.get('pkeys', None))
        self.assertEqual({'a': ['a1']}, info['pkeys'])
        self.assertEqual([], info.get('fkeys', None))

    def test_table_with_pks(self):
        schema_def = 'CREATE TABLE a (a1 int, a2 int, a3 int, ' \
                     'PRIMARY KEY (a1, a2));'
        with Schema.get_db() as db:
            info = db.get_information(schema_def)
            self.assertIsNotNone(info.get('tables'), None)
        self.assertEqual(OrderedDict({'a': ['a1', 'a2', 'a3']}), info['tables'])
        self.assertIsNotNone(info.get('pkeys', None))
        self.assertEqual({'a': ['a1', 'a2']}, info['pkeys'])
        self.assertEqual([], info.get('fkeys', None))

    def test_table_with_fk(self):
        schema_def = 'CREATE TABLE a(a1 int unique, a2 int, a3 int);' \
                     'CREATE TABLE b(b1 int references a(a1));'
        with Schema.get_db() as db:
            info = db.get_information(schema_def)
            self.assertIsNotNone(info.get('tables'), None)
        self.assertEqual({'a': ['a1', 'a2', 'a3'],
                                      'b': ['b1']}, info['tables'])
        self.assertIsNotNone(info.get('pkeys', None))
        self.assertEqual({}, info['pkeys'])
        self.assertEqual([(('b', 'b1'), ('a', 'a1'))], info.get('fkeys', None))

    def test_table_with_fks(self):
        schema_def = 'CREATE TABLE a(a1 int unique, a2 int unique, a3 int);' \
                     'CREATE TABLE b(b1 int references a(a1),' \
                                    'b2 int references a(a2));'
        with Schema.get_db() as db:
            info = db.get_information(schema_def)
            self.assertIsNotNone(info.get('tables'), None)
        self.assertEqual({'a': ['a1', 'a2', 'a3'], 'b': ['b1', 'b2']},
                         info['tables'])
        self.assertIsNotNone(info.get('pkeys', None))
        self.assertEqual({}, info['pkeys'])
        fkeys = [(('b', 'b1'), ('a', 'a1')), (('b', 'b2'), ('a', 'a2'))]
        self.assertEqual(set(fkeys), set(info.get('fkeys', None)))