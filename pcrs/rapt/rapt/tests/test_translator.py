import functools
from unittest import TestCase

import psycopg2

from rapt.constants import SET_SEMANTICS, BAG_SEMANTICS
from rapt.grammars import CoreGrammar
from rapt.translator import Translator


class TestTranslator(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(database='rapt_test_db', user='raptor',
                                    password='raptolicious')
        cls.cur = cls.conn.cursor()
        cls.execute = cls.cur.execute

        cls.schema = None
        cls.data = None

    @classmethod
    def create_translate_func(cls, grammar, schema, semantics):
        translator = Translator(grammar)
        return functools.partial(translator.translate, schema,
                                 semantics)

    def setUp(self):
        self.setup_database(self.schema, self.data)

    def tearDown(self):
        self.drop_tables(self.schema.keys())

    def setup_database(self, schema, data):
        self.create_tables(schema)
        self.insert_data(data)

    def create_tables(self, schema):
        for relation, attributes in schema.items():
            attributes = ', '.join(['{} text'.format(attribute)
                                    for attribute in attributes])
            statement = 'CREATE TABLE %s (%s)' % (relation, attributes)
            self.execute(statement)

    def drop_tables(self, tables):
        for relation in tables:
            statement = 'DROP TABLE %s;' % relation
            self.execute(statement)

    def insert_data(self, data_set):
        for relation, data in data_set.items():
            values = ', '.join(['%s' for _ in data[0] ])
            statement = 'INSERT INTO %s VALUES (%s)' % (relation, values)
            for row in data:
                self.execute(statement, row)

    def query(self, statement):
        self.execute(statement)
        return self.cur.fetchall()

    def query_list(self, statements):
        for statement in statements:
            self.execute(statement)
        return self.cur.fetchall()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()


class TestRelation(TestTranslator):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schema = {'letters': ['position', 'value'],
                      'numbers': ['value', 'prime']}
        cls.data = {'letters': [('1', 'a'),
                                ('2', 'b'),
                                ('2', 'b'),
                                ('3', 'c'),
                                ('3', 'c')],
                    'numbers': [('1', 'yes'),
                                ('2', 'yes'),
                                ('3', 'yes'),
                                ('4', 'no')]}
        cls.translate_set = cls.create_translate_func(CoreGrammar, cls.schema,
                                                      SET_SEMANTICS)
        cls.translate_bag = cls.create_translate_func(CoreGrammar, cls.schema,
                                                      BAG_SEMANTICS)

    def test_set_single_relation(self):
        instring = 'letters;'
        translation = self.translate_set(instring)
        expected = [('1', 'a'), ('2', 'b'), ('3', 'c')]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_set_multiple_relations(self):
        instring = 'numbers; letters;'
        translation = self.translate_set(instring)
        expected = [('1', 'a'), ('2', 'b'), ('3', 'c')]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_bag_single_relation_duplicates(self):
        instring = 'letters;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a'), ('2', 'b'), ('2', 'b'), ('3', 'c'), ('3', 'c')]
        self.assertCountEqual(expected, self.query_list(translation.sql))


class TestProject(TestTranslator):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schema = {'magic_wand': ['owner', 'manufacturer', 'wood', 'core',
                                     'length', 'rigidity']}
        cls.translate_set = cls.create_translate_func(CoreGrammar, cls.schema,
                                                      SET_SEMANTICS)
        cls.translate_bag = cls.create_translate_func(CoreGrammar, cls.schema,
                                                      BAG_SEMANTICS)
        cls.data = {'magic_wand': [
            ('Harry', 'Ollivander', 'holly', 'phoenix', '11', 'supple'),
            ('Ron', 'unknown', 'ash', 'unicorn', '12', 'rigid'),
            ('Hermione', 'Ollivander', 'vine', 'dragon', '14', 'rigid'),
            ('Harry', 'Ollivander', 'holly', 'phoenix', '11', 'supple'),
            ('Ron', 'unknown', 'ash', 'unicorn', '12', 'rigid'),
            ('Hermione', 'Ollivander', 'vine', 'dragon', '14', 'rigid'),
        ]}

    def test_single_project_single_attr(self):
        instring = '\project_{owner} magic_wand;'
        translation = self.translate_set(instring)
        expected = [('Harry',), ('Ron',), ('Hermione', )]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_single_project_two_attr(self):
        instring = '\project_{owner, wood} magic_wand;'
        translation = self.translate_set(instring)
        expected = [('Harry', 'holly'), ('Ron', 'ash'), ('Hermione', 'vine')]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_single_project_most_attr(self):
        instring = '\project_{owner, wood, core, length, rigidity} magic_wand;'
        translation = self.translate_set(instring)
        expected = [
            ('Harry', 'holly', 'phoenix', '11', 'supple'),
            ('Ron', 'ash', 'unicorn', '12', 'rigid'),
            ('Hermione', 'vine', 'dragon', '14', 'rigid')
        ]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_single_project_all_attr(self):
        instring = '\project_{owner, manufacturer, wood, core, length, ' \
                   'rigidity} magic_wand;'
        translation = self.translate_set(instring)
        expected = [
            ('Harry', 'Ollivander', 'holly', 'phoenix', '11', 'supple'),
            ('Ron', 'unknown', 'ash', 'unicorn', '12', 'rigid'),
            ('Hermione', 'Ollivander', 'vine', 'dragon', '14', 'rigid')
        ]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_single_project_all_attr_out_of_order(self):
        instring = '\project_{owner, wood, core, length, rigidity, ' \
                   'manufacturer} ' \
                   'magic_wand;'
        translation = self.translate_set(instring)
        expected = [
            ('Harry', 'holly', 'phoenix', '11', 'supple', 'Ollivander'),
            ('Ron', 'ash', 'unicorn', '12', 'rigid', 'unknown'),
            ('Hermione', 'vine', 'dragon', '14', 'rigid', 'Ollivander')
        ]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_single_project_single_attr_bag(self):
        instring = '\project_{owner} magic_wand;'
        translation = self.translate_bag(instring)
        expected = [('Harry',), ('Ron',), ('Hermione', ),
                    ('Harry',), ('Ron',), ('Hermione', )]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_double_project(self):
        instring = '\project_{owner} \project_{owner, wood} magic_wand;'
        translation = self.translate_set(instring)
        expected = [('Harry',), ('Ron',), ('Hermione', )]
        self.assertCountEqual(expected, self.query_list(translation.sql))

    def test_triple_project(self):
        instring = '\project_{owner} \project_{owner, wood}' \
                   '\project_{owner, wood, core} magic_wand;'
        translation = self.translate_set(instring)
        expected = [('Harry',), ('Ron',), ('Hermione', )]
        self.assertCountEqual(expected, self.query_list(translation.sql))


class TestMystery(TestTranslator):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schema = {'magic_wand': ['owner', 'manufacturer', 'wood', 'core',
                                     'length', 'rigidity']}
        cls.translate_set = cls.create_translate_func(CoreGrammar, cls.schema,
                                                      SET_SEMANTICS)
        cls.translate_bag = cls.create_translate_func(CoreGrammar, cls.schema,
                                                      BAG_SEMANTICS)
        cls.data = {'magic_wand': [
            ('Harry', 'Ollivander', 'holly', 'phoenix', '11', 'supple'),
            ('Ron', 'unknown', 'ash', 'unicorn', '12', 'rigid'),
            ('Hermione', 'Ollivander', 'vine', 'dragon', '14', 'rigid'),
            ('Harry', 'Ollivander', 'holly', 'phoenix', '11', 'supple'),
            ('Ron', 'unknown', 'ash', 'unicorn', '12', 'rigid'),
            ('Hermione', 'Ollivander', 'vine', 'dragon', '14', 'rigid'),
        ]}

    def test_single_project_single_attr(self):
        instring = '' \
                   '\\project_{m1.manufacturer} ' \
                   '\\select_{m2.manufacturer="Ollivander"} ' \
                   '(\\rename_{m1} magic_wand ' \
                   '\\join ' \
                   '\\rename_{m2} magic_wand);'
        translation = self.translate_set(instring)
        expected = [('Ollivander',), ('unknown',)]
        actual = self.query_list(translation.sql)
        self.assertCountEqual(expected, actual)
