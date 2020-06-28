from unittest import TestCase

import functools
import psycopg2

from rapt import Rapt


class TestTranslator(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(database='rapt_test_db', user='raptor',
            password='raptolicious')
        cls.cur = cls.conn.cursor()
        cls.execute = cls.cur.execute

        cls.setup_database(cls.schema, cls.data)

        cls.translate_bag = cls.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql, use_bag_semantics=True))
        cls.translate_set = cls.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql))


    @classmethod
    def translate_func(cls, func, schema=None):
        schema = schema or cls.schema
        return functools.partial(func, schema=schema)

    @classmethod
    def tearDownClass(cls):
        cls.drop_tables(cls.schema.keys())

    @classmethod
    def setup_database(cls, schema, data):
        cls.create_tables(schema)
        cls.insert_data(data)

    @classmethod
    def create_tables(cls, schema):
        for relation, attributes in schema.items():
            attributes = ', '.join(['{} text'.format(attribute)
                                    for attribute in attributes])
            statement = 'CREATE TABLE %s (%s)' % (relation, attributes)
            cls.execute(statement)

    @classmethod
    def drop_tables(cls, tables):
        for relation in tables:
            statement = 'DROP TABLE %s;' % relation
            cls.execute(statement)

    @classmethod
    def insert_data(cls, data_set):
        for relation, data in data_set.items():
            values = ', '.join(['%s' for _ in data[0]])
            statement = 'INSERT INTO {0} VALUES ({1})'.format(relation, values)
            for row in data:
                cls.execute(statement, row)

    @classmethod
    def query(cls, statement):
        cls.execute(statement)
        return cls.cur.fetchall()

    @classmethod
    def query_list(cls, statements):
        for statement in statements:
            cls.execute(statement)
        return cls.cur.fetchall()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()


class TestRelation(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'Alpha': ['a1', 'a2']
        }
        cls.data = {
            'Alpha': [
                ('1', 'a'),
                ('2', 'b'),
                ('2', 'b')
            ]
        }
        super().setUpClass()

    def test_single_relation_set(self):
        instring = 'alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a'), ('2', 'b')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_relation_set_cased(self):
        instring = 'Alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a'), ('2', 'b')]
        self.assertCountEqual(expected, self.query_list(translation))


    def test_single_relation_bag(self):
        instring = 'alpha;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a'), ('2', 'b'), ('2', 'b')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_multiple_relations_bag(self):
        instring = 'alpha; alpha;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a'), ('2', 'b'), ('2', 'b')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestProject(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2', 'a3']
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('3', 'b', '!')
            ]
        }
        super().setUpClass()

    def test_single_project_single_attr_set_no_duplicates(self):
        instring = '\project_{a1} alpha;'
        translation = self.translate_set(instring)
        expected = [('1',), ('2',), ('3', )]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_single_attr_set_no_duplicates_cased(self):
        instring = '\project_{a1} ALPHA;'
        translation = self.translate_set(instring)
        expected = [('1',), ('2',), ('3', )]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_single_attr_set_with_duplicates(self):
        instring = '\project_{a2} alpha;'
        translation = self.translate_set(instring)
        expected = [('a',), ('b',)]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_single_attr_bag_no_duplicates(self):
        instring = '\project_{a1} alpha;'
        translation = self.translate_bag(instring)
        expected = [('1',), ('2',), ('3', )]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_single_attr_bag_with_duplicates(self):
        instring = '\project_{a2} alpha;'
        translation = self.translate_bag(instring)
        expected = [('a',), ('b',), ('b',)]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_two_attr_set_no_duplicates(self):
        instring = '\project_{a1, a2} alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a',), ('2', 'b'), ('3', 'b')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_two_attr_set_with_duplicates(self):
        instring = '\project_{a2, a3} alpha;'
        translation = self.translate_set(instring)
        expected = [('a', '!',), ('b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_two_attr_bag_no_duplicates(self):
        instring = '\project_{a1, a2} alpha;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a',), ('2', 'b'), ('3', 'b')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_two_attr_bag_with_duplicates(self):
        instring = '\project_{a2, a3} alpha;'
        translation = self.translate_bag(instring)
        expected = [('a', '!',), ('b', '!'), ('b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_all_attr(self):
        instring = '\project_{a1, a2, a3} alpha;'
        translation = self.translate_set(instring)
        expected = self.data['alpha']
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_project_all_attr_out_of_order(self):
        instring = '\project_{a2, a3, a1} alpha;'
        translation = self.translate_set(instring)
        expected = [('a', '!', '1'), ('b', '!', '2'), ('b', '!', '3')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_double_project(self):
        instring = '\project_{a2} \project_{a2, a3} alpha;'
        translation = self.translate_set(instring)
        expected = [('a',), ('b',)]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_triple_project(self):
        instring = '\project_{a1} \project_{a2, a1}' \
                   '\project_{a2, a1, a3} alpha;'
        translation = self.translate_set(instring)
        expected = [('1',), ('2',), ('3',)]
        self.assertCountEqual(expected, self.query_list(translation))


class TestSelect(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2', 'a3']
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ]
        }
        super().setUpClass()

    def test_single_select_with_no_attr_set(self):
        instring = '\select_{1=1} alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_no_attr_bag(self):
        instring = '\select_{1=1} alpha;'
        translation = self.translate_bag(instring)
        expected = self.data['alpha']
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_attr_all(self):
        instring = '\select_{a1<>\'missing\'} alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_attr_subset_set(self):
        instring = '\select_{a1<>\'1\'} alpha;'
        translation = self.translate_set(instring)
        expected = [('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_attr_subset_bag(self):
        instring = '\select_{a1<>\'1\'} alpha;'
        translation = self.translate_bag(instring)
        expected = [('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_attr_none(self):
        instring = '\select_{a1=\'1\' and a2=\'b\'} alpha;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_multiple_cond_attr_subset_set(self):
        instring = '\select_{a1<>\'1\' and a2<>\'a\'} alpha;'
        translation = self.translate_set(instring)
        expected = [('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_single_select_with_attr_case(self):
        instring = '\select_{A1=\'1\' and A2=\'b\'} Alpha;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_double_select_with_attr(self):
        instring = '\select_{a1!=\'missing\'} \select_{A2!=\'missing\'} Alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestRename(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2', 'a3']
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ]
        }
        super().setUpClass()

    def test_rename_relation(self):
        instring = '\project_{AlphaPrime.a1, AlphaPrime.a2, AlphaPrime.a3} ' \
                   '\\rename_{AlphaPrime} alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_rename_relation_bag(self):
        instring = '\project_{AlphaPrime.a1, AlphaPrime.a2, AlphaPrime.a3} ' \
                   '\\rename_{AlphaPrime} alpha;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_rename_attributes(self):
        instring = '\project_{alpha.ap1, alpha.ap2, alpha.ap3} ' \
                   '\\rename_{(ap1, ap2, ap3)} alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_rename_relation_and_attributes(self):
        instring = '\project_{APrime.ap1, APrime.ap2, APrime.ap3} ' \
                   '\\rename_{APrime(ap1, ap2, ap3)} alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestAssign(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2', 'a3']
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ]
        }
        super().setUpClass()

    def tearDown(self):
        self.drop_tables(['alpha_prime'])

    def test_assign_relation_set(self):
        instring = 'alpha_prime := alpha; alpha_prime;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_assign_relation_bag(self):
        instring = 'alpha_prime := alpha; alpha_prime;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_assign_relation_with_attr_rename(self):
        instring = 'alpha_prime(ap1, ap2, ap3) := alpha;' \
                   '\project_{alpha_prime.ap1, alpha_prime.ap2, alpha_prime.ap3} alpha_prime;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestUnion(TestTranslator):
    @classmethod
    def setUpClass(cls):
        attrs = ['a1', 'a2', 'a3']
        cls.schema = {
            'alpha': attrs,
            'alpha_copy': attrs,
            'alpha_subset': attrs,
            'alpha_superset': attrs,
            'alpha_extra': attrs,
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ],
            'alpha_copy': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ],
            'alpha_subset': [
                ('1', 'a', '!'),
            ],
            'alpha_superset': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!'),
                ('3', 'c', '?')
            ],
            'alpha_extra': [
                ('3', 'c', '?'),
            ]
        }
        super().setUpClass()

    def test_union_self_set(self):
        instring = 'alpha \\union alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_self_bag(self):
        instring = 'alpha \\union alpha;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'),
                    ('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_other_set(self):
        instring = 'alpha \\union alpha_copy;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_other_bag(self):
        instring = 'alpha \\union alpha_copy;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'),
                    ('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_superset_set(self):
        instring = 'alpha \\union alpha_superset;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_superset_bag(self):
        instring = 'alpha \\union alpha_superset;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'),
                    ('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'),
                    ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_extra_set(self):
        instring = 'alpha \\union alpha_extra;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_extra_bag(self):
        instring = 'alpha \\union alpha_extra;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'),
                    ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_subset_set(self):
        instring = 'alpha \\union alpha_subset;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_union_subset_bag(self):
        instring = 'alpha \\union alpha_extra;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'),
                    ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestDifference(TestTranslator):
    @classmethod
    def setUpClass(cls):
        attrs = ['a1', 'a2', 'a3']
        cls.schema = {
            'alpha': attrs,
            'alpha_copy': attrs,
            'alpha_subset': attrs,
            'alpha_superset': attrs,
            'alpha_extra': attrs,
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ],
            'alpha_copy': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ],
            'alpha_subset': [
                ('1', 'a', '!'),
            ],
            'alpha_superset': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!'),
                ('3', 'c', '?'),
                ('3', 'c', '?')
            ],
            'alpha_extra': [
                ('3', 'c', '?'),
                ('3', 'c', '?'),
            ]
        }
        super().setUpClass()

    def test_difference_self_set(self):
        instring = 'alpha \\difference alpha;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_self_bag(self):
        instring = 'alpha \\difference alpha;'
        translation = self.translate_bag(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_other_set(self):
        instring = 'alpha \\difference alpha_copy;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_other_bag(self):
        instring = 'alpha \\difference alpha_copy;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_subset_set(self):
        instring = 'alpha_subset \\difference alpha;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_subset_bag(self):
        instring = 'alpha_subset \\difference alpha;'
        translation = self.translate_bag(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_superset_set(self):
        instring = 'alpha_superset \\difference alpha;'
        translation = self.translate_set(instring)
        expected = [('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_superset_bag(self):
        instring = 'alpha_superset \\difference alpha;'
        translation = self.translate_bag(instring)
        expected = [('3', 'c', '?'), ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_extra_set(self):
        instring = 'alpha_extra \\difference alpha;'
        translation = self.translate_set(instring)
        expected = [('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_difference_extra_bag(self):
        instring = 'alpha_extra \\difference alpha;'
        translation = self.translate_bag(instring)
        expected = [('3', 'c', '?'), ('3', 'c', '?')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestIntersection(TestTranslator):
    @classmethod
    def setUpClass(cls):
        attrs = ['a1', 'a2', 'a3']
        cls.schema = {
            'alpha': attrs,
            'alpha_copy': attrs,
            'alpha_subset': attrs,
            'alpha_superset': attrs,
            'alpha_extra': attrs,
        }
        cls.data = {
            'alpha': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ],
            'alpha_copy': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!')
            ],
            'alpha_subset': [
                ('1', 'a', '!'),
            ],
            'alpha_superset': [
                ('1', 'a', '!'),
                ('2', 'b', '!'),
                ('2', 'b', '!'),
                ('3', 'c', '?'),
                ('3', 'c', '?')
            ],
            'alpha_extra': [
                ('3', 'c', '?'),
                ('3', 'c', '?'),
            ]
        }
        super().setUpClass()

    def test_intersect_self_set(self):
        instring = 'alpha \\intersect alpha;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_self_bag(self):
        instring = 'alpha \\intersect alpha;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_other_set(self):
        instring = 'alpha \\intersect alpha_copy;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_other_bag(self):
        instring = 'alpha \\intersect alpha_copy;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_superset_set(self):
        instring = 'alpha \\intersect alpha_superset;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_superset_bag(self):
        instring = 'alpha \\intersect alpha_superset;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!'), ('2', 'b', '!'), ('2', 'b', '!'), ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_extra_set(self):
        instring = 'alpha_extra \\intersect alpha;'
        translation = self.translate_set(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_extra_bag(self):
        instring = 'alpha_extra \\intersect alpha;'
        translation = self.translate_bag(instring)
        expected = []
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_subset_set(self):
        instring = 'alpha \\intersect alpha_subset;'
        translation = self.translate_set(instring)
        expected = [('1', 'a', '!')]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_intersect_subset_bag(self):
        instring = 'alpha \\intersect alpha_subset;'
        translation = self.translate_bag(instring)
        expected = [('1', 'a', '!')]
        self.assertCountEqual(expected, self.query_list(translation))


class TestJoin(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2'],
            'beta': ['b1'],
            'gamma': ['g1'],
        }
        cls.data = {
            'alpha': [('1', 'a'), ('2', 'b'), ('2', 'b')],
            'beta': [('3',), ('4',), ],
            'gamma': [('?',), ('!',)],
        }
        super().setUpClass()


    def test_join_other_set(self):
        instring = 'alpha \\join beta;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a', '3'), ('2', 'b', '3'),
            ('1', 'a', '4'), ('2', 'b', '4'),
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_other_bag(self):
        instring = 'alpha \\join beta;'
        translation = self.translate_bag(instring)
        expected = [
            ('1', 'a', '3'), ('2', 'b', '3'), ('2', 'b', '3'),
            ('1', 'a', '4'), ('2', 'b', '4'), ('2', 'b', '4'),
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_double(self):
        instring = 'alpha \\join beta \\join gamma;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a', '3', '?'), ('2', 'b', '3', '?'),
            ('1', 'a', '4', '?'), ('2', 'b', '4', '?'),
            ('1', 'a', '3', '!'), ('2', 'b', '3', '!'),
            ('1', 'a', '4', '!'), ('2', 'b', '4', '!'),
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_self_with_rename_set(self):
        instring = '\\rename_{a1} alpha \\join \\rename_{a2} alpha;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a', '1', 'a'), ('2', 'b', '1', 'a'),
            ('1', 'a', '2', 'b'), ('2', 'b', '2', 'b'),
        ]
        self.assertCountEqual(expected, self.query_list(translation))


class TestNaturalJoin(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2'],
            'alpha_copy': ['a1', 'a2'],
            'alpha_subset': ['a1', 'a2'],
            'alpha_prime': ['a1', 'ap2'],
            'alpha_prime_extra': ['ap2', 'ap3'],
        }
        cls.data = {
            'alpha': [('1', 'a'), ('2', 'b'), ('2', 'b')],
            'alpha_copy': [('1', 'a'), ('2', 'b'), ('2', 'b')],
            'alpha_subset': [('2', 'b'), ('2', 'b')],
            'alpha_prime': [('1', '!'), ('2', '?')],
            'alpha_prime_extra': [('?', 'this')],
        }
        super().setUpClass()


    def test_join_copy_set(self):
        instring = 'alpha \\natural_join alpha_copy;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a'), ('2', 'b')
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_copy_bag(self):
        instring = 'alpha \\natural_join alpha_copy;'
        translation = self.translate_bag(instring)
        expected = [
            ('1', 'a'), ('2', 'b'), ('2', 'b'),
            ('1', 'a'), ('2', 'b'), ('2', 'b')
        ]
        self.assertCountEqual(set(expected), set(self.query_list(translation)))

    def test_join_prime_set(self):
        instring = 'alpha \\natural_join alpha_prime;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a', '!'), ('2', 'b', '?')
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_prime_bag(self):
        instring = 'alpha \\natural_join alpha_prime;'
        translation = self.translate_bag(instring)
        expected = [
            ('1', 'a', '!'), ('2', 'b', '?'), ('2', 'b', '?')
        ]
        self.assertCountEqual(set(expected), set(self.query_list(translation)))

    def test_join_prime_extra_set(self):
        instring = 'alpha \\natural_join alpha_prime' \
                   '\\natural_join alpha_prime_extra;'
        translation = self.translate_set(instring)
        expected = [
            ('2', 'b', '?', 'this')
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_prime_extra_bag(self):
        instring = 'alpha \\natural_join alpha_prime ' \
                   '\\natural_join alpha_prime_extra;'
        translation = self.translate_bag(instring)
        expected = [
            ('2', 'b', '?', 'this'),
            ('2', 'b', '?', 'this'),
        ]
        self.assertCountEqual(set(expected), set(self.query_list(translation)))

    def test_join_self_with_rename_set(self):
        instring = '\\rename_{a1} alpha \\natural_join \\rename_{a2} alpha;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a'), ('2', 'b')
        ]
        self.assertCountEqual(expected, self.query_list(translation))


class TestThetaJoin(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'alpha': ['a1', 'a2'],
            'alpha_copy': ['a1', 'a2'],
            'alpha_prime': ['ap1', 'ap2'],
            'alpha_prime_subset': ['ap1', 'ap2'],
        }
        cls.data = {
            'alpha': [('1', 'a'), ('2', 'b'), ('2', 'b')],
            'alpha_copy': [('1', 'a'), ('2', 'b'), ('2', 'b')],
            'alpha_prime': [('1', 'a'), ('2', 'b'), ('2', 'b')],
            'alpha_prime_subset': [('1', '!')],
        }
        super().setUpClass()


    def test_join_copy_set(self):
        instring = 'alpha \\join_{alpha.a1=alpha_copy.a1} alpha_copy;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a', '1', 'a'),
            ('2', 'b', '2', 'b'),
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_join_copy_bag(self):
        instring = 'alpha \\join_{alpha.a1=alpha_copy.a1} alpha_copy;'
        translation = self.translate_bag(instring)
        expected = [
            ('1', 'a', '1', 'a'),
            ('2', 'b', '2', 'b'),
            ('2', 'b', '2', 'b'),
        ]
        self.assertCountEqual(set(expected), set(self.query_list(translation)))

    def test_join_prime_set(self):
        instring = 'alpha \\join_{alpha.a1=alpha_prime.ap1} alpha_prime;'
        translation = self.translate_set(instring)
        expected = [
            ('1', 'a', '1', 'a'),
            ('2', 'b', '2', 'b'),
        ]
        self.assertCountEqual(expected, self.query_list(translation))

class TestUnary(TestTranslator):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'Alpha': ['a1', 'a2']
        }
        cls.data = {
            'Alpha': [
                ('1', 'a'),
                ('2', 'b'),
                ('2', 'b')
            ]
        }
        super().setUpClass()


    def test_select_project(self):
        instring = '\select_{a2=\'b\'} \project_{a2 } alpha;'
        translation = self.translate_set(instring)
        expected = [
            ('b',)
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_project_select(self):
        instring = ' \project_{a2} \select_{a2=\'b\'} alpha;'
        translation = self.translate_set(instring)
        expected = [
            ('b',)
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_select_rename(self):
        instring = '\select_{ap2=\'b\'} \\rename_{A(ap1, ap2)} alpha;'
        translation = self.translate_set(instring)
        expected = [
            ('2', 'b',)
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_project_rename(self):
        instring = '\project_{ap2} \\rename_{A(ap1, ap2)} alpha;'
        translation = self.translate_set(instring)
        expected = [
            ('a', ), ('b',)
        ]
        self.assertCountEqual(expected, self.query_list(translation))

    def test_assign_project_rename(self):
        instring = 'A := \project_{ap2} \\rename_{A(ap1, ap2)} alpha; A;'
        translation = self.translate_set(instring)
        expected = [
            ('a', ), ('b',)
        ]
        self.assertCountEqual(expected, self.query_list(translation))