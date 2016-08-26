import unittest
from rak.pattern import Pattern


class PatternBasicBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.p = Pattern()

    def test__pattern_default_properties(self):
        self.assertEqual(None, self.p.pattern)
        self.assertEqual(('',), self.p.groups)

    def test__invalid_pattern__raises_exception(self):
        pattern = '(foo'
        with self.assertRaises(SyntaxError):
            self.p.add_expression(pattern)

    def test__pattern_with_no_groups_contains_only_the_main_pattern(self):
        pattern = 'foo'
        self.p.add_expression(pattern)
        self.assertEqual((pattern,), self.p.groups)

    def test__pattern_with_one_group(self):
        pattern = '(foo)'
        self.p.add_expression(pattern)
        self.assertEqual((pattern, '(foo)'), self.p.groups)

    def test__pattern_with_two_groups(self):
        pattern = '(foo)kjh(hello)kjkjkjkjkj'
        self.p.add_expression(pattern)
        self.assertEqual((pattern, '(foo)', '(hello)'), self.p.groups)

    def test__pattern_can_be_printed_when_empty(self):
        result = str(self.p)
        expected = 'An empty pattern'
        self.assertEqual(result, expected)

    def test__pattern_can_be_printed_when_not_empty1(self):
        self.p.add_expression('(foo)')
        result = str(self.p)
        expected = "Pattern object\n\tregexp pattern: '(foo)'\n\tregexp groups:  ('(foo)',)"
        self.assertEqual(result, expected)

    def test__pattern_can_be_printed_when_not_empty2(self):
        self.p.add_expression('(foo)vmi(hello)')
        result = str(self.p)
        expected = "Pattern object\n\tregexp pattern: '(foo)vmi(hello)'\n\tregexp groups:  ('(foo)', '(hello)')"
        self.assertEqual(result, expected)


class PatternRegexpExecutionTests(unittest.TestCase):
    def setUp(self):
        self.p = Pattern()

    def test__empty_pattern__should_raise_exception_on_execution(self):
        with self.assertRaises(ValueError):
            self.p.execute('foo')

    def test__search_fully_qualified_pattern_with_no_group(self):
        raw_text = 'Hello'
        pattern = '^\w+$'
        self.p.add_expression(pattern)

        expected = {
            'results': ('Hello',),
            'spans': ((0, 5),)
        }
        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)

    def test__search_fully_qualified_pattern_with_one_group(self):
        raw_text = 'Hello'
        pattern = '^(\w+)$'
        self.p.add_expression(pattern)

        expected = {
            'results': ('Hello', 'Hello'),
            'spans': ((0, 5), (0, 5))
        }
        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)

    def test__search_partly_qualified_pattern_with_one_group(self):
        raw_text = '  Hello  '
        pattern = '(\w+)'
        self.p.add_expression(pattern)

        expected = {
            'results': ('Hello', 'Hello'),
            'spans': ((2, 7), (2, 7))
        }
        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)

    def test__search_partly_qualified_pattern_with_two_groups(self):
        raw_text = 'Foo:12'
        pattern = '(\w{3}):(\d+)'
        self.p.add_expression(pattern)

        expected = {
            'results': ('Foo:12', 'Foo', '12'),
            'spans': ((0, 6), (0, 3), (4, 6))
        }

        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)

    def test__search_partly_qualified_pattern_with_three_groups(self):
        raw_text = 'Foo:12,fofo'
        pattern = '(Foo):(\d+),(fofo)'
        self.p.add_expression(pattern)

        expected = {
            'results': ('Foo:12,fofo', 'Foo', '12', 'fofo'),
            'spans': ((0, 11), (0, 3), (4, 6), (7, 11))
        }

        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)

    def test__match_longer_text_than_the_pattern(self):
        raw_text = '  Foo:12   kjkjkjkj'
        pattern = '(Foo):(\d+)'
        self.p.add_expression(pattern)

        expected = {
            'results': ('Foo:12', 'Foo', '12'),
            'spans': ((2, 8), (2, 5), (6, 8))
        }

        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)

    def test__no_match__returns_none(self):
        raw_text = 'kjkjkjkjkj'
        pattern = '(Foo)'
        self.p.add_expression(pattern)
        expected = None
        result = self.p.execute(raw_text)
        self.assertEqual(result, expected)
