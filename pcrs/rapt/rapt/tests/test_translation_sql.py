import functools
from unittest import TestCase

from rapt.constants import BAG_SEMANTICS, SET_SEMANTICS
from rapt.grammars.core_grammar import CoreGrammar
from rapt.grammars.extended_grammar import ExtendedGrammar
from rapt.translator import Translator
from rapt.translation_error import RelationReferenceError, \
    AttributeReferenceError


class TestSQL(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'AlphaTwin': ['a1', 'a2', 'a3'],
            'AlphaPrime': ['a1', 'a4', 'a5'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2', 'g3'],
            'Ambiguous': ['a', 'a', 'b']
        }
        cls.translator = Translator(CoreGrammar)
        cls.translate = functools.partial(cls.translator.translate, cls.schema,
                                          BAG_SEMANTICS)
        cls.translate_set = functools.partial(cls.translator.translate,
                                              cls.schema, SET_SEMANTICS)


class TestRelation(TestSQL):
    def test_single_relation(self):
        ra = 'Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'Alpha; Beta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha;',
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_relation_exp(self):
        ra = 'Alpha; Beatrice;'
        self.assertRaises(RelationReferenceError, self.translate, ra)


class TestSelect(TestSQL):
    def test_single_select(self):
        ra = '\\select_{a1=a2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 '
                    'FROM Alpha WHERE (a1 = a2);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_single_select_set(self):
        ra = '\\select_{a1=a2} Alpha;'
        expected = ['SELECT DISTINCT Alpha.a1, Alpha.a2, Alpha.a3 '
                    'FROM Alpha WHERE (a1 = a2);']
        actual = self.translate_set(ra).sql
        self.assertEqual(expected, actual)

    def test_single_select_with_relation(self):
        ra = '\\select_{Alpha.a1=a2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (Alpha.a1 = a2);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_selects(self):
        ra = '\\select_{a1=1} \\select_{a2=2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a2 = 2) AND (a1 = 1);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_select_with_precedence(self):
        ra = '\\select_{a2=a3} (\\select_{a1=a2} Alpha);'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a1 = a2) AND (a2 = a3);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_select_with_multiple_conditions(self):
        ra = '\\select_{a1=2 or a1=1} \\select_{a2=2 or a2=1} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a2 = 2 or a2 = 1) AND (a1 = 2 or a1 = 1);']
        actual = self.translate(ra).sql
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
        ra = '\\project_{a1, a2, a3} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_prefixed(self):
        ra = '\\project_{Alpha.a1, Alpha.a2, Alpha.a3} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_subset(self):
        ra = '\\project_{a1, Alpha.a2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2 FROM Alpha;']
        actual = self.translate(ra).sql
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
        ra = '\\rename_{Apex} Alpha;'
        expected = ['SELECT Apex.a1, Apex.a2, Apex.a3 '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a1, a2, a3);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{(a, b, c)} Alpha;'
        expected = ['SELECT a, b, c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Alpha(a, b, c);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_rename_all(self):
        ra = '\\rename_{Apex(a, b, c)} Alpha;'
        expected = ['SELECT Apex.a, Apex.b, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a, b, c);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_rename_with_select(self):
        ra = '\\rename_{Apex(a, b, c)} \\select_{a1 = a2} Alpha;'
        expected = ['SELECT Apex.a, Apex.b, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a1 = a2)) AS Apex(a, b, c);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_rename_is_projected(self):
        ra = '\\project_{a, c} \\rename_{Apex(a, b, c)} Alpha;'
        expected = ['SELECT Apex.a, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a, b, c);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)


class TestAssignment(TestCase):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'AlphaTwin': ['a1', 'a2', 'a3'],
            'AlphaPrime': ['a1', 'a4', 'a5'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2', 'g3'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(CoreGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)

    def test_relation(self):
        ra = 'NewAlpha := Alpha;'
        expected = ['CREATE TEMPORARY TABLE NewAlpha(a1, a2, a3) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_relation_with_attributes(self):
        ra = 'NewAlpha(a, b, c) := Alpha;'
        expected = ['CREATE TEMPORARY TABLE NewAlpha(a, b, c) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_relation_with_ambiguous_attributes(self):
        ra = 'NewAlpha(a, b, c) := Ambiguous;'
        expected = ['CREATE TEMPORARY TABLE NewAlpha(a, b, c) AS '
                    'SELECT Ambiguous.a, Ambiguous.a, Ambiguous.b '
                    'FROM Ambiguous;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select(self):
        ra = 'Niche := \select_{b1=1} Beta;'
        expected = ['CREATE TEMPORARY TABLE Niche(b1, b2, b3) AS '
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta '
                    'WHERE (b1 = 1);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_with_attributes(self):
        ra = 'Niche(a, b, c) := \select_{b1=1} Beta;'
        expected = ['CREATE TEMPORARY TABLE Niche(a, b, c) AS '
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta '
                    'WHERE (b1 = 1);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_project(self):
        ra = 'Bilk := \\project_{b1, b2} Beta;'
        expected = ['CREATE TEMPORARY TABLE Bilk(b1, b2) AS '
                    'SELECT Beta.b1, Beta.b2 FROM Beta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_project_with_attributes(self):
        ra = 'Bilk(a, b) := \\project_{b1, b2} Beta;'
        expected = ['CREATE TEMPORARY TABLE Bilk(a, b) AS '
                    'SELECT Beta.b1, Beta.b2 FROM Beta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_project_select(self):
        ra = 'Combine := \\project_{b1, b2} \\select_{b1 = 1} Beta;'
        expected = ['CREATE TEMPORARY TABLE Combine(b1, b2) AS '
                    'SELECT Beta.b1, Beta.b2 FROM Beta '
                    'WHERE (b1 = 1);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_join(self):
        ra = 'Bound := Alpha \\join Beta;'
        expected = ['CREATE TEMPORARY TABLE Bound(a1, a2, a3, b1, b2, b3) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_join_with_attributes(self):
        ra = 'Bound(a, b, c, d, e, f) := Alpha \\join Beta;'
        expected = ['CREATE TEMPORARY TABLE Bound(a, b, c, d, e, f) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)


class TestJoin(TestSQL):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'AlphaTwin': ['a1', 'a2', 'a3'],
            'AlphaPrime': ['a1', 'a4', 'a5'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(CoreGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)
        self.translate_set = functools.partial(self.translator.translate,
                                               self.schema, SET_SEMANTICS)

    def test_relation(self):
        ra = 'Alpha \\join Beta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, '
                    'Beta.b1, Beta.b2, Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        ra = 'Alpha \\join Beta \\join Gamma;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3, Gamma.g1, Gamma.g2 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'Alpha \\join Beta \\join Gamma \\join Delta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3, Gamma.g1, Gamma.g2, Delta.d1, Delta.d2 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma '
                    'CROSS JOIN '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_right_join_first(self):
        ra = 'Alpha \\join (Beta \\join Gamma);'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3, Gamma.g1, Gamma.g2 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_right(self):
        ra = 'Delta \\join \\select_{g1 = g2} Gamma;'
        expected = ['SELECT Delta.d1, Delta.d2, Gamma.g1, Gamma.g2 FROM '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'WHERE (g1 = g2)) AS Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_left(self):
        ra = '\\select_{g1 = g2} Gamma \\join  Delta;'
        expected = ['SELECT Gamma.g1, Gamma.g2, Delta.d1, Delta.d2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'WHERE (g1 = g2)) AS Gamma '
                    'CROSS JOIN '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_on_join(self):
        ra = '\\select_{g1 = g2} (Gamma \\join Delta);'
        translation = self.translate(ra)
        expected = ['SELECT Gamma.g1, Gamma.g2, Delta.d1, Delta.d2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma '
                    'CROSS JOIN '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta '
                    'WHERE (g1 = g2);']
        actual = translation.sql
        self.assertEqual(expected, actual)

    def test_join_with_rename(self):
        ra = '\\rename_{G} Gamma \\join \\rename_{H} Gamma;'
        translation = self.translate(ra)
        expected = ['SELECT G.g1, G.g2, H.g1, H.g2 FROM '
                    '(SELECT G.g1, G.g2 FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS G(g1, g2)) AS G '
                    'CROSS JOIN '
                    '(SELECT H.g1, H.g2 FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS H(g1, g2)) AS H;']
        actual = translation.sql
        self.assertEqual(expected, actual)

    def test_join_with_rename_set(self):
        ra = '\\rename_{G} Gamma \\join \\rename_{H} Gamma;'
        translation = self.translate_set(ra)
        expected = ['SELECT DISTINCT G.g1, G.g2, H.g1, H.g2 FROM '
                    '(SELECT DISTINCT G.g1, G.g2 '
                    'FROM (SELECT DISTINCT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS G(g1, g2)) AS G '
                    'CROSS JOIN '
                    '(SELECT DISTINCT H.g1, H.g2 '
                    'FROM (SELECT DISTINCT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS H(g1, g2)) AS H;']
        actual = translation.sql
        self.assertEqual(expected, actual)

    def test_join_with_rename_attributes(self):
        ra = '\\rename_{G(a, b)} Gamma \\join \\rename_{H(a, b)} Gamma;'
        translation = self.translate(ra)
        expected = ['SELECT G.a, G.b, H.a, H.b FROM '
                    '(SELECT G.a, G.b FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS G(a, b)) AS G '
                    'CROSS JOIN '
                    '(SELECT H.a, H.b FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS H(a, b)) AS H;']
        actual = translation.sql
        self.assertEqual(expected, actual)


class TestNaturalJoin(TestSQL):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'AlphaTwin': ['a1', 'a2', 'a3'],
            'AlphaPrime': ['a1', 'a4', 'a5'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(ExtendedGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)

    def test_relation_simple(self):
        ra = 'Alpha \\natural_join AlphaTwin;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'NATURAL JOIN '
                    '(SELECT AlphaTwin.a1, AlphaTwin.a2, AlphaTwin.a3 '
                    'FROM AlphaTwin) AS AlphaTwin;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        ra = 'Alpha \\natural_join AlphaTwin \\natural_join AlphaPrime;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, AlphaPrime.a4, '
                    'AlphaPrime.a5 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'NATURAL JOIN '
                    '(SELECT AlphaTwin.a1, AlphaTwin.a2, AlphaTwin.a3 '
                    'FROM AlphaTwin) AS AlphaTwin '
                    'NATURAL JOIN '
                    '(SELECT AlphaPrime.a1, AlphaPrime.a4, AlphaPrime.a5 '
                    'FROM AlphaPrime) AS AlphaPrime;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)


class TestThetaJoin(TestSQL):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'AlphaTwin': ['a1', 'a2', 'a3'],
            'AlphaPrime': ['a1', 'a4', 'a5'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(ExtendedGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)
        self.translate_set = functools.partial(self.translator.translate,
                                               self.schema, SET_SEMANTICS)

    def test_relation(self):
        ra = 'Alpha \\join_{a1 = b1} Beta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, '
                    'Beta.b1, Beta.b2, Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'WHERE (a1 = b1);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)


class TestUnion(TestSQL):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'GammaTwin': ['g1', 'g2'],
            'GammaPrime': ['g1', 'g2', 'g3'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(CoreGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)

    def test_simple(self):
        ra = 'Gamma \\union GammaTwin;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'UNION ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_simple_multiple(self):
        ra = 'Gamma \\union GammaTwin \\union Gamma;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'UNION ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin '
                    'UNION ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_simple(self):
        ra = '\\select_{g1 = g2} (Gamma \\union GammaTwin);'
        translation = self.translate(ra)
        exp_name = translation.parse_tree[0].child.name
        expected = ['SELECT g1, g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'UNION ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS {name} WHERE (g1 = g2);'.format(name=exp_name)]
        self.assertEqual(expected, translation.sql)

    def test_project_simple(self):
        ra = '\\project_{g2} (Gamma \\union GammaTwin);'
        translation = self.translate(ra)
        exp_name = translation.parse_tree[0].child.name
        expected = ['SELECT g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'UNION ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS {name};'.format(name=exp_name)]
        self.assertEqual(expected, translation.sql)

    def test_project_left(self):
        ra = '\\project_{g1, g2} GammaPrime \\union Gamma;'
        translation = self.translate(ra)
        expected = ['SELECT GammaPrime.g1, GammaPrime.g2 FROM GammaPrime '
                    'UNION ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma;']
        self.assertEqual(expected, translation.sql)

    def test_rename_simple(self):
        ra = '\\rename_{G} (Gamma \\union GammaTwin);'
        expected = ['SELECT G.g1, G.g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'UNION ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS G(g1, g2);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{G(a, b)} (Gamma \\union GammaTwin);'
        expected = ['SELECT G.a, G.b FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'UNION ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS G(a, b);']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)


class TestDifference(TestSQL):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'GammaTwin': ['g1', 'g2'],
            'GammaPrime': ['g1', 'g2', 'g3'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(CoreGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)

    def test_simple(self):
        ra = 'Gamma \\difference GammaTwin;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'EXCEPT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_simple_multiple(self):
        ra = 'Gamma \\difference GammaTwin \\difference Gamma;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'EXCEPT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin '
                    'EXCEPT ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_different(self):
        ra = 'Gamma \\difference GammaTwin \\union Gamma;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'EXCEPT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin '
                    'UNION ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_simple(self):
        ra = '\\select_{g1 = g2} (Gamma \\difference GammaTwin);'
        translation = self.translate(ra)
        exp_name = translation.parse_tree[0].child.name
        expected = ['SELECT g1, g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'EXCEPT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS {name} WHERE (g1 = g2);'.format(name=exp_name)]
        self.assertEqual(expected, translation.sql)


class TestIntersection(TestSQL):
    def setUp(self):
        self.schema = {
            'Alpha': ['a1', 'a2', 'a3'],
            'Beta': ['b1', 'b2', 'b3'],
            'Gamma': ['g1', 'g2'],
            'GammaTwin': ['g1', 'g2'],
            'GammaPrime': ['g1', 'g2', 'g3'],
            'Delta': ['d1', 'd2'],
            'Ambiguous': ['a', 'a', 'b']
        }
        self.translator = Translator(ExtendedGrammar)
        self.translate = functools.partial(self.translator.translate,
                                           self.schema, BAG_SEMANTICS)

    def test_simple(self):
        ra = 'Gamma \\intersect GammaTwin;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'INTERSECT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_simple_multiple(self):
        ra = 'Gamma \\intersect GammaTwin \\intersect Gamma;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'INTERSECT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin '
                    'INTERSECT ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_multiple_different(self):
        ra = 'Gamma \\intersect GammaTwin \\union Gamma;'
        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'INTERSECT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin '
                    'UNION ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma;']
        actual = self.translate(ra).sql
        self.assertEqual(expected, actual)

    def test_select_simple(self):
        ra = '\\select_{g1 = g2} (Gamma \\intersect GammaTwin);'
        translation = self.translate(ra)
        exp_name = translation.parse_tree[0].child.name
        expected = ['SELECT g1, g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'INTERSECT ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS {name} WHERE (g1 = g2);'.format(name=exp_name)]
        self.assertEqual(expected, translation.sql)