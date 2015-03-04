import functools

from rapt.rapt import Rapt
from rapt.transformers.sql import sql_translator
from rapt.treebrd.grammars import CoreGrammar
from rapt.treebrd.grammars.extended_grammar import ExtendedGrammar
from rapt.treebrd.errors import AttributeReferenceError
from rapt.treebrd.treebrd import TreeBRD

from tests.transformers.test_transfomer import TestTransformer


class TestSQL(TestTransformer):
    grammar = CoreGrammar()

    def setUp(self):
        self.translate = self.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql, use_bag_semantics=True))
        self.translate_set = self.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql))


class TestRelation(TestSQL):
    def test_single_relation(self):
        ra = 'alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_relation_set(self):
        ra = 'alpha;'
        expected = ['SELECT DISTINCT alpha.a1, alpha.a2, alpha.a3 FROM alpha']
        actual = self.translate_set(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'alpha; beta;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha',
                    'SELECT beta.b1, beta.b2, beta.b3 FROM beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSelect(TestSQL):
    def test_single_select(self):
        ra = '\\select_{a1=a2} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 '
                    'FROM alpha WHERE a1 = a2']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_select_set(self):
        ra = '\\select_{a1=a2} alpha;'
        expected = ['SELECT DISTINCT alpha.a1, alpha.a2, alpha.a3 '
                    'FROM alpha WHERE a1 = a2']
        actual = self.translate_set(ra)
        self.assertEqual(expected, actual)

    def test_single_select_with_relation(self):
        ra = '\\select_{alpha.a1=a2} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha '
                    'WHERE alpha.a1 = a2']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_selects(self):
        ra = '\\select_{a1=1} \\select_{a2=2} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha '
                    'WHERE (a2 = 2) AND (a1 = 1)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_select_with_precedence(self):
        ra = '\\select_{a2=a3} (\\select_{a1=a2} alpha);'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha '
                    'WHERE (a1 = a2) AND (a2 = a3)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_select_with_multiple_conditions(self):
        ra = '\\select_{a1=2 or a1=1} \\select_{a2=2 or a2=1} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha '
                    'WHERE (a2 = 2 or a2 = 1) AND (a1 = 2 or a1 = 1)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_select_wrong_attrs(self):
        ra = '\\select_{b1=bee_one} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_multiple_selects_wrong_attrs(self):
        ra = '\\select_{b1=1} \\select_{bee_two=2} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_multiple_selects_wrong_attrs_both(self):
        ra = '\\select_{bee_one=1} \\select_{a_two=2} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)


class TestProject(TestSQL):
    def test_simple(self):
        ra = '\\project_{a1, a2, a3} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_prefixed(self):
        ra = '\\project_{alpha.a1, alpha.a2, alpha.a3} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_subset(self):
        ra = '\\project_{a1, alpha.a2} alpha;'
        expected = ['SELECT alpha.a1, alpha.a2 FROM alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_not_a_subset(self):
        ra = '\\project_{b} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_not_a_subset2(self):
        ra = '\\project_{Alpha.a1, b} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_not_a_subset3(self):
        ra = '\\project_{a1, Alpha.b} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)


class TestRename(TestSQL):
    def test_relation(self):
        ra = '\\rename_{apex} alpha;'
        expected = ['SELECT apex.a1, apex.a2, apex.a3 '
                    'FROM (SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) '
                    'AS apex(a1, a2, a3)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{(a, b, c)} alpha;'
        expected = ['SELECT alpha.a, alpha.b, alpha.c '
                    'FROM (SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) '
                    'AS alpha(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_all(self):
        ra = '\\rename_{apex(a, b, c)} alpha;'
        expected = ['SELECT apex.a, apex.b, apex.c '
                    'FROM (SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) '
                    'AS apex(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_with_select(self):
        ra = '\\rename_{apex(a, b, c)} \\select_{a1 = a2} alpha;'
        expected = ['SELECT apex.a, apex.b, apex.c '
                    'FROM (SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha '
                    'WHERE a1 = a2) AS apex(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_is_projected(self):
        ra = '\\project_{a, c} \\rename_{apex(a, b, c)} alpha;'
        expected = ['SELECT apex.a, apex.c '
                    'FROM (SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) '
                    'AS apex(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestAssignment(TestSQL):
    def test_relation(self):
        ra = 'newalpha := alpha;'
        expected = ['CREATE TEMPORARY TABLE newalpha(a1, a2, a3) AS '
                    'SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_relation_with_attributes(self):
        ra = 'newalpha(a, b, c) := alpha;'
        expected = ['CREATE TEMPORARY TABLE newalpha(a, b, c) AS '
                    'SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_relation_with_ambiguous_attributes(self):
        ra = 'newalpha(a, b, c) := ambiguous;'
        expected = ['CREATE TEMPORARY TABLE newalpha(a, b, c) AS '
                    'SELECT ambiguous.a, ambiguous.a, ambiguous.b '
                    'FROM ambiguous']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select(self):
        ra = 'niche := \select_{b1=1} beta;'
        expected = ['CREATE TEMPORARY TABLE niche(b1, b2, b3) AS '
                    'SELECT beta.b1, beta.b2, beta.b3 FROM beta '
                    'WHERE b1 = 1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_with_attributes(self):
        ra = 'niche(a, b, c) := \select_{b1=1} beta;'
        expected = ['CREATE TEMPORARY TABLE niche(a, b, c) AS '
                    'SELECT beta.b1, beta.b2, beta.b3 FROM beta '
                    'WHERE b1 = 1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_project(self):
        ra = 'bilk := \\project_{b1, b2} beta;'
        expected = ['CREATE TEMPORARY TABLE bilk(b1, b2) AS '
                    'SELECT beta.b1, beta.b2 FROM beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_project_with_attributes(self):
        ra = 'bilk(a, b) := \\project_{b1, b2} beta;'
        expected = ['CREATE TEMPORARY TABLE bilk(a, b) AS '
                    'SELECT beta.b1, beta.b2 FROM beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_project_select(self):
        ra = 'combine := \\project_{b1, b2} \\select_{b1 = 1} beta;'
        expected = ['CREATE TEMPORARY TABLE combine(b1, b2) AS '
                    'SELECT beta.b1, beta.b2 FROM beta '
                    'WHERE b1 = 1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_join(self):
        ra = 'bound := alpha \\join beta;'
        expected = ['CREATE TEMPORARY TABLE bound(a1, a2, a3, b1, b2, b3) AS '
                    'SELECT alpha.a1, alpha.a2, alpha.a3, beta.b1, beta.b2, '
                    'beta.b3 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_join_with_attributes(self):
        ra = 'bound(a, b, c, d, e, f) := alpha \\join beta;'
        expected = ['CREATE TEMPORARY TABLE bound(a, b, c, d, e, f) AS '
                    'SELECT alpha.a1, alpha.a2, alpha.a3, beta.b1, beta.b2, '
                    'beta.b3 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestJoin(TestSQL):
    def test_relation(self):
        ra = 'alpha \\join beta;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3, '
                    'beta.b1, beta.b2, beta.b3 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        self.maxDiff = None
        ra = 'alpha \\join beta \\join gamma;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3, beta.b1, beta.b2, '
                    'beta.b3, gamma.g1, gamma.g2 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta '
                    'CROSS JOIN '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma) AS gamma']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'alpha \\join beta \\join gamma \\join delta;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3, beta.b1, beta.b2, '
                    'beta.b3, gamma.g1, gamma.g2, delta.d1, delta.d2 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta '
                    'CROSS JOIN '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma) AS gamma '
                    'CROSS JOIN '
                    '(SELECT delta.d1, delta.d2 FROM delta) AS delta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_right_join_first(self):
        ra = 'alpha \\join (beta \\join gamma);'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3, beta.b1, beta.b2, '
                    'beta.b3, gamma.g1, gamma.g2 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta '
                    'CROSS JOIN '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma) AS gamma']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_right(self):
        ra = 'delta \\join \\select_{g1 = g2} gamma;'
        expected = ['SELECT delta.d1, delta.d2, gamma.g1, gamma.g2 FROM '
                    '(SELECT delta.d1, delta.d2 FROM delta) AS delta '
                    'CROSS JOIN '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma '
                    'WHERE g1 = g2) AS gamma']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_left(self):
        ra = '\\select_{g1 = g2} gamma \\join  delta;'
        expected = ['SELECT gamma.g1, gamma.g2, delta.d1, delta.d2 FROM '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma '
                    'WHERE g1 = g2) AS gamma '
                    'CROSS JOIN '
                    '(SELECT delta.d1, delta.d2 FROM delta) AS delta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_on_join(self):
        ra = '\\select_{g1 = g2} (gamma \\join delta);'
        translation = self.translate(ra)
        expected = ['SELECT gamma.g1, gamma.g2, delta.d1, delta.d2 FROM '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma) AS gamma '
                    'CROSS JOIN '
                    '(SELECT delta.d1, delta.d2 FROM delta) AS delta '
                    'WHERE g1 = g2']
        actual = translation
        self.assertEqual(expected, actual)

    def test_join_with_rename(self):
        ra = '\\rename_{g} gamma \\join \\rename_{h} gamma;'
        translation = self.translate(ra)
        expected = ['SELECT g.g1, g.g2, h.g1, h.g2 FROM '
                    '(SELECT g.g1, g.g2 FROM (SELECT gamma.g1, gamma.g2 '
                    'FROM gamma) AS g(g1, g2)) AS g '
                    'CROSS JOIN '
                    '(SELECT h.g1, h.g2 FROM (SELECT gamma.g1, gamma.g2 '
                    'FROM gamma) AS h(g1, g2)) AS h']
        actual = translation
        self.assertEqual(expected, actual)

    def test_join_with_rename_set(self):
        ra = '\\rename_{g} gamma \\join \\rename_{h} gamma;'
        translation = self.translate_set(ra)
        expected = ['SELECT DISTINCT g.g1, g.g2, h.g1, h.g2 FROM '
                    '(SELECT DISTINCT g.g1, g.g2 '
                    'FROM (SELECT DISTINCT gamma.g1, gamma.g2 '
                    'FROM gamma) AS g(g1, g2)) AS g '
                    'CROSS JOIN '
                    '(SELECT DISTINCT h.g1, h.g2 '
                    'FROM (SELECT DISTINCT gamma.g1, gamma.g2 '
                    'FROM gamma) AS h(g1, g2)) AS h']
        actual = translation
        self.assertEqual(expected, actual)

    def test_join_with_rename_attributes(self):
        ra = '\\rename_{g(a, b)} gamma \\join \\rename_{h(a, b)} gamma;'
        translation = self.translate(ra)
        expected = ['SELECT g.a, g.b, h.a, h.b FROM '
                    '(SELECT g.a, g.b FROM (SELECT gamma.g1, gamma.g2 '
                    'FROM gamma) AS g(a, b)) AS g '
                    'CROSS JOIN '
                    '(SELECT h.a, h.b FROM (SELECT gamma.g1, gamma.g2 '
                    'FROM gamma) AS h(a, b)) AS h']
        actual = translation
        self.assertEqual(expected, actual)


class TestNaturalJoin(TestSQL):
    grammar = ExtendedGrammar()

    def test_relation_simple(self):
        ra = 'alpha \\natural_join alphatwin;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'NATURAL JOIN '
                    '(SELECT alphatwin.a1, alphatwin.a2, alphatwin.a3 '
                    'FROM alphatwin) AS alphatwin']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        ra = 'alpha \\natural_join alphatwin \\natural_join alphaprime;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3, alphaprime.a4, '
                    'alphaprime.a5 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'NATURAL JOIN '
                    '(SELECT alphatwin.a1, alphatwin.a2, alphatwin.a3 '
                    'FROM alphatwin) AS alphatwin '
                    'NATURAL JOIN '
                    '(SELECT alphaprime.a1, alphaprime.a4, alphaprime.a5 '
                    'FROM alphaprime) AS alphaprime']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestThetaJoin(TestSQL):
    grammar = ExtendedGrammar()

    def test_relation(self):
        ra = 'alpha \\join_{a1 = b1} beta;'
        expected = ['SELECT alpha.a1, alpha.a2, alpha.a3, '
                    'beta.b1, beta.b2, beta.b3 FROM '
                    '(SELECT alpha.a1, alpha.a2, alpha.a3 FROM alpha) AS alpha '
                    'CROSS JOIN '
                    '(SELECT beta.b1, beta.b2, beta.b3 FROM beta) AS beta '
                    'WHERE a1 = b1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSet:
    def test_simple(self):
        ra = 'gamma {operator} gammatwin;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0])
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g1, g2 FROM ('
                    'SELECT gamma.g1, gamma.g2 FROM gamma '
                    '{operator} ALL '
                    'SELECT gammatwin.g1, gammatwin.g2 FROM gammatwin) '
                    'AS _{name}'.format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_simple_multiple(self):
        ra = 'gamma {operator} gammatwin {operator} gammaprime;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        root_name = id(root_list[0])
        child_name = id(root_list[0].left)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g1, g2 FROM ('
                    'SELECT g1, g2 FROM '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma '
                    '{operator} ALL '
                    'SELECT gammatwin.g1, gammatwin.g2 FROM gammatwin) AS _{name1} '
                    '{operator} ALL '
                    'SELECT gammaprime.g1, gammaprime.g2 FROM gammaprime) AS _{name2}'
                        .format(operator=self.sql_operator, name1=child_name, name2=root_name)]
        self.assertEqual(expected, actual)

    def test_select_simple(self):
        ra = '\\select_{{g1 = g2}} (gamma {operator} gammatwin);'.format(operator=self.ra_operator)
        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)
        expected = ['SELECT g1, g2 FROM '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma '
                    '{operator} ALL '
                    'SELECT gammatwin.g1, gammatwin.g2 FROM gammatwin) '
                    'AS _{name} WHERE g1 = g2'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_project_simple(self):
        ra = '\\project_{{g2}} (gamma {operator} gammatwin);'.format(operator=self.ra_operator)
        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)
        expected = ['SELECT g2 FROM '
                    '(SELECT gamma.g1, gamma.g2 FROM gamma '
                    '{operator} ALL '
                    'SELECT gammatwin.g1, gammatwin.g2 FROM gammatwin) '
                    'AS _{name}'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_project_left(self):
        ra = '\\project_{{g1, g2}} gammaprime {operator} gamma;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0])
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g1, g2 FROM '
                    '(SELECT gammaprime.g1, gammaprime.g2 FROM gammaprime '
                    '{operator} ALL '
                    'SELECT gamma.g1, gamma.g2 FROM gamma) AS _{name}'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_rename_simple(self):
        ra = '\\rename_{{g}} (gamma {operator} gammatwin);'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g.g1, g.g2 FROM '
                    '(SELECT g1, g2 FROM (SELECT gamma.g1, gamma.g2 FROM gamma '
                    '{operator} ALL '
                    'SELECT gammatwin.g1, gammatwin.g2 FROM gammatwin) '
                    'AS _{name}) AS g(g1, g2)'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{{g(a, b)}} (gamma {operator} gammatwin);'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g.a, g.b FROM '
                    '(SELECT g1, g2 FROM (SELECT gamma.g1, gamma.g2 FROM gamma '
                    '{operator} ALL '
                    'SELECT gammatwin.g1, gammatwin.g2 FROM gammatwin) AS _{name}) '
                    'AS g(a, b)'.format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)


class TestUnion(TestSQL, TestSet):
    ra_operator = '\\union'
    sql_operator = 'UNION'


class TestDifference(TestSQL, TestSet):
    ra_operator = '\\difference'
    sql_operator = 'EXCEPT'


class TestIntersection(TestSQL, TestSet):
    grammar = ExtendedGrammar()
    ra_operator = '\\intersect'
    sql_operator = 'INTERSECT'