import unittest
from rak.pattern import (Pattern, PatternHandler, InvalidPatternIdError,
                               NoPatternError)


class PatternHandlerAddingPatternsTests(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__pattern_handler_initialization(self):
        self.assertEqual([], self.ph.patterns)
        self.assertEqual(0, self.ph.last_id)

    def test__adding_a_pattern(self):
        self.ph.add_pattern()
        self.assertEqual(1, len(self.ph.patterns))
        self.assertEqual(dict, self.ph.patterns[0].__class__)
        self.assertEqual(str, self.ph.patterns[0]['id'].__class__)
        self.assertEqual(Pattern, self.ph.patterns[0]['pattern'].__class__)

    def test__adding_pattern_returns_the_main_id(self):
        expected = 'P1'
        result = self.ph.add_pattern()
        self.assertEqual(result, expected)
        self.assertEqual(1, len(self.ph.patterns))

    def test__adding_pattern_returns_the_main_id_for_the_second_time_as_well(self):
        expected = 'P2'
        self.ph.add_pattern()
        result = self.ph.add_pattern()
        self.assertEqual(result, expected)
        self.assertEqual(2, len(self.ph.patterns))


class PatternHandlerPrint(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__pattern_handler_can_be_printed_when_empty(self):
        result = str(self.ph)
        expected = 'An empty PatternHandler'
        self.assertEqual(result, expected)

    def test__pattern_handler_can_be_printed_when_contains_patterns1(self):
        self.ph.add_pattern()
        result = str(self.ph)
        expected = 'PatternHandler\n\tA: Empty pattern\n'
        self.assertEqual(result, expected)

    def test__pattern_handler_can_be_printed_when_contains_patterns2(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')
        result = str(self.ph)
        expected = 'PatternHandler\n\tA: \'(foo)\'\n'
        self.assertEqual(result, expected)

    def test__pattern_handler_can_be_printed_when_contains_patterns3(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(hello)')
        result = str(self.ph)
        expected = 'PatternHandler\n\tA: \'(foo)\'\n\tB: \'(hello)\'\n'
        self.assertEqual(result, expected)


class PatterIdParsing(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__single_id_produces_valid_main_and_group_index1(self):
        raw_id = 'P1'
        expected = {'main': 0, 'group': -1}
        result = PatternHandler._parse_id(raw_id)
        self.assertEqual(result, expected)

    def test__single_id_produces_valid_main_and_group_index2(self):
        raw_id = 'P2'
        expected = {'main': 1, 'group': -1}
        result = PatternHandler._parse_id(raw_id)
        self.assertEqual(result, expected)

    def test__id_with_group_index(self):
        raw_id = 'P2.2'
        expected = {'main': 1, 'group': 1}
        result = PatternHandler._parse_id(raw_id)
        self.assertEqual(result, expected)

    def test__lowercase_id__raises_exception(self):
        raw_id = 'a2'
        with self.assertRaises(InvalidPatternIdError):
            PatternHandler._parse_id(raw_id)

    def test__numeric_id__raises_exception(self):
        raw_id = '42'
        with self.assertRaises(InvalidPatternIdError):
            PatternHandler._parse_id(raw_id)


class PatternIdValidation(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__no_patterns_added_yet__validation_raises_error(self):
        parsed_id = {'main': 0, 'group': 0}
        with self.assertRaises(InvalidPatternIdError):
            self.ph._validate_id(parsed_id)

    def test__valid_pattern__no_error_raised__main_ok(self):
        self.ph.add_pattern()
        parsed_id = {'main': 0, 'group': 0}
        self.ph._validate_id(parsed_id)

    def test__valid_pattern__no_error_raised__group_ok(self):
        self.ph.add_pattern()
        self.ph.patterns[0]['pattern'].add_expression('(foo)')
        parsed_id = {'main': 0, 'group': 0}
        self.ph._validate_id(parsed_id)

    def test__invalid_pattern__main_index_overrun__should_raise_error(self):
        self.ph.add_pattern()
        parsed_id = {'main': 1, 'group': 0}
        with self.assertRaises(InvalidPatternIdError):
            self.ph._validate_id(parsed_id)

    def test__invalid_pattern__group_index_overrun__should_raise_error(self):
        main_id = self.ph.add_pattern()
        parsed_id = {'main': main_id, 'group': 1}
        with self.assertRaises(InvalidPatternIdError):
            self.ph._validate_id(parsed_id)


class PatternHandlerRemovePattersTests(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__pattern_can_be_removed_with_id(self):
        main_id = self.ph.add_pattern()
        self.ph.remove_pattern(main_id)
        self.assertEqual(0, len(self.ph.patterns))

    def test__remove__removes_the_appropriate_pattern_case_1(self):
        self.ph.add_pattern()
        main_id = self.ph.add_pattern()
        self.ph.remove_pattern(main_id)
        self.assertEqual(1, len(self.ph.patterns))
        self.assertEqual('A', self.ph.patterns[0]['id'])

    def test__remove__removes_the_appropriate_pattern_case_2(self):
        main_id = self.ph.add_pattern()
        self.ph.add_pattern()
        self.ph.remove_pattern(main_id)
        self.assertEqual(1, len(self.ph.patterns))
        self.assertEqual('B', self.ph.patterns[0]['id'])

    def test__invalid_id_raises_error(self):
        self.ph.add_pattern()
        with self.assertRaises(InvalidPatternIdError):
            self.ph.remove_pattern('B')


class PatternModificationTests(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__modify_pattern(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')
        expected = ('(foo)', '(foo)')
        result = self.ph.patterns[0]['pattern'].groups
        self.assertEqual(result, expected)


class PatternHandlerReportTests(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__no_patterns__returns_empty_tuple(self):
        expected = ()
        result = self.ph.get_main_id_list()
        self.assertEqual(result, expected)

    def test__patterns_exist__returns_tuple_with_ids(self):
        self.ph.add_pattern()
        self.ph.add_pattern()
        self.ph.add_pattern()
        expected = ('A', 'B', 'C')
        result = self.ph.get_main_id_list()
        self.assertEqual(result, expected)

    def test__groups_can_be_interrogated(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')

        expected = (('A', 'A1'),)
        result = self.ph.get_full_id_list()

        self.assertEqual(result, expected)

    def test__groups_can_be_interrogated_for_multiple_patterns(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)(hello)')

        expected = (('A', 'A1'), ('B', 'B1', 'B2'))
        result = self.ph.get_full_id_list()

        self.assertEqual(result, expected)

    def test__groups_can_be_interrogated_for_id(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)(hello)')

        expected = ('A', 'A1')
        result = self.ph.get_full_id_list('A')
        self.assertEqual(result, expected)

        expected = ('B', 'B1', 'B2')
        result = self.ph.get_full_id_list('B')
        self.assertEqual(result, expected)


class PatternHandlerExecute(unittest.TestCase):
    def setUp(self):
        self.ph = PatternHandler()

    def test__empty_pattern_list_raises_error_on_execution(self):
        with self.assertRaises(NoPatternError):
            self.ph.execute(None)

    def test__execute_with_one_pattern_no_match(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, 'foo')

        content = 'nope'

        expected = {}

        result = self.ph.execute(content)
        self.assertEqual(result, expected)

    def test__execute_with_no_group(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, 'foo')

        content = 'This is foo..'

        expected = {
            'P1': {'match': 'foo', 'span': (8, 11)}
        }

        result = self.ph.execute(content)
        self.assertEqual(result, expected)

    def test__execute_with_one_pattern_case_1(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '(foo)')

        content = 'This is foo..'

        expected = {
            'P1':   {'match': 'foo', 'span': (8, 11)},
            'P1.1': {'match': 'foo', 'span': (8, 11)}
        }

        result = self.ph.execute(content)
        self.assertEqual(result, expected)

    def test__execute_with_one_pattern_case_2(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '.*(foo).*')

        content = 'This is foo..'

        expected = {
            'P1':   {'match': 'This is foo..', 'span': (0, 13)},
            'P1.1': {'match': 'foo', 'span': (8, 11)}
        }

        result = self.ph.execute(content)
        self.assertEqual(result, expected)

    def test__execute_with_two_patterns_case_1(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '.*(foo).*')

        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '\s(is)\s(.*)')

        content = 'This is foo..'

        expected = {
            'P1':   {'match': 'This is foo..', 'span': (0, 13)},
            'P1.1': {'match': 'foo', 'span': (8, 11)},
            'P2':   {'match': ' is foo..', 'span': (4, 13)},
            'P2.1': {'match': 'is', 'span': (5, 7)},
            'P2.2': {'match': 'foo..', 'span': (8, 13)}
        }

        result = self.ph.execute(content)
        self.assertEqual(result, expected)

    def test__execute_with_two_patterns_second_did_not_match(self):
        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '.*(foo).*')

        main_id = self.ph.add_pattern()
        self.ph.modify_pattern(main_id, '\s(is)\s(.*)')

        content = '..foo..'

        expected = {
            'P1':   {'match': '..foo..', 'span': (0, 7)},
            'P1.1': {'match': 'foo', 'span': (2, 5)}
        }

        result = self.ph.execute(content)
        self.assertEqual(result, expected)
