from unittest import TestCase
from rapt.treebrd.grammars.syntax import Syntax


class TestSyntax(TestCase):
    def test___init__when_operator_is_changed(self):
        new_op = 'test_op'
        self.assertEqual(new_op, Syntax(and_op=new_op).and_op)

    def test___init__cannot_set_unknown_attributes(self):
        self.assertFalse(hasattr(Syntax(foo='bar'), 'foo'))