import unittest
from replaceit.sequence import (SequenceNode, SequenceState,
                                Offset, OffsetMode)


# SequenceNode
class SequenceBasicTests(unittest.TestCase):
    def setUp(self):
        self.s = SequenceNode(1)

    def test__initial_values(self):
        self.assertEqual(Offset, self.s.offset.__class__)
        self.assertEqual(None, self.s.prev_sequence)
        self.assertEqual(None, self.s.next_sequence)
        self.assertEqual(0, self.s.condition_id)
        self.assertEqual(1, self.s.id)
        self.assertEqual(SequenceState.idle, self.s.state)
        self.assertEqual(0, self.s.proxy_counter)

    def test__passing_id_to_constructor(self):
        s = SequenceNode(1)
        self.assertEqual(1, s.id)

    def test__is_trigger_case_1(self):
        self.assertTrue(self.s.is_trigger())

    def test__is_trigger_case_2(self):
        self.s.prev_sequence = 1
        self.assertFalse(self.s.is_trigger())

    def test__is_termination_case_1(self):
        self.assertTrue(self.s.is_termination())

    def test__is_termination_case_2(self):
        self.s.next_sequence = 1
        self.assertFalse(self.s.is_termination())

    def test__adding_parent_sets_reference_in_children_too(self):
        s1 = SequenceNode(1)
        s2 = SequenceNode(2)
        s2.add_prev_sequence(s1)
        self.assertEqual(s1, s2.prev_sequence)
        self.assertEqual(s2, s1.next_sequence)


class SequenceProcessProtocolTests(unittest.TestCase):
    def test__no_condition_specified__raise_error(self):
        s = SequenceNode(1)
        with self.assertRaises(ValueError):
            s.process(None)

    def test__trigger_and_termination_matches(self):
        s = SequenceNode(1)
        s.condition_id = 2
        data = {2: True}
        expected = {'result': 1, 'termination': True}
        result = s.process(data)
        self.assertEqual(expected, result)

    def test__trigger_and_termination_not_matches(self):
        s = SequenceNode(1)
        s.condition_id = 3
        data = {2: True}
        expected = {'result': 0, 'termination': True}
        result = s.process(data)
        self.assertEqual(expected, result)

    def test__two_sequences__first_sequence_changes_state_on_match(self):
        s1 = SequenceNode(1)
        s2 = SequenceNode(2)
        s2.add_prev_sequence(s1)
        s1.condition_id = 1

        data = {1: True}
        expected = {'result': 1, 'termination': False}
        result = s1.process(data)

        self.assertEqual(SequenceState.proxy, s1.state)
        self.assertEqual(expected, result)

    def test__two_sequences__first_node_emits_offset_information_in_proxy_mode(self):
        s1 = SequenceNode(1)
        s1.state = SequenceState.proxy
        s1.condition_id = 1
        dummy = SequenceNode(2)
        dummy.add_prev_sequence(s1)
        self.assertEqual(0, s1.proxy_counter)
        s1.process(None)
        self.assertEqual(1, s1.proxy_counter)
        s1.process(None)
        self.assertEqual(2, s1.proxy_counter)


# Offset
class OffsetValidationTests(unittest.TestCase):
    def setUp(self):
        self.o = Offset()

    def test__equal_mode_case_1(self):
        # target_number is 0
        # mode is equal
        self.assertEqual(False, self.o.validate_before_match(0))
        self.assertEqual(True, self.o.validate_on_match(0))

    def test__equal_mode_case_2(self):
        self.o.target_number = 2
        self.assertEqual(True, self.o.validate_before_match(0))
        self.assertEqual(True, self.o.validate_before_match(1))
        self.assertEqual(False,  self.o.validate_before_match(2))
        self.assertEqual(False, self.o.validate_before_match(3))

        self.assertEqual(False, self.o.validate_on_match(1))
        self.assertEqual(True,  self.o.validate_on_match(2))
        self.assertEqual(False, self.o.validate_on_match(3))

    def test__equal_mode_case_3(self):
        self.o.target_number = -7
        self.assertEqual(False, self.o.validate_before_match(-7))

    def test__less_than_mode(self):
        self.o.mode = OffsetMode.less_than
        self.o.target_number = 2
        self.assertEqual(True,  self.o.validate_before_match(1))
        self.assertEqual(False, self.o.validate_before_match(2))
        self.assertEqual(False, self.o.validate_before_match(3))

        self.assertEqual(True,  self.o.validate_on_match(1))
        self.assertEqual(False, self.o.validate_on_match(2))
        self.assertEqual(False, self.o.validate_on_match(3))

    def test__less_than_or_equal_mode(self):
        self.o.mode = OffsetMode.less_than_or_equal
        self.o.target_number = 2
        self.assertEqual(True,  self.o.validate_before_match(1))
        self.assertEqual(True,  self.o.validate_before_match(2))
        self.assertEqual(False, self.o.validate_before_match(3))

        self.assertEqual(True,  self.o.validate_on_match(1))
        self.assertEqual(True, self.o.validate_on_match(2))
        self.assertEqual(False, self.o.validate_on_match(3))

    def test__greater_than_mode(self):
        self.o.mode = OffsetMode.greater_then
        self.o.target_number = 2
        self.assertEqual(True, self.o.validate_before_match(1))
        self.assertEqual(True, self.o.validate_before_match(2))
        self.assertEqual(True,  self.o.validate_before_match(3))

        self.assertEqual(False, self.o.validate_on_match(1))
        self.assertEqual(False, self.o.validate_on_match(2))
        self.assertEqual(True,  self.o.validate_on_match(3))

    def test__greater_than_or_equal_mode(self):
        self.o.mode = OffsetMode.greater_then_or_equal
        self.o.target_number = 2
        self.assertEqual(True, self.o.validate_before_match(1))
        self.assertEqual(True,  self.o.validate_before_match(2))
        self.assertEqual(True,  self.o.validate_before_match(3))

        self.assertEqual(False, self.o.validate_on_match(1))
        self.assertEqual(True,  self.o.validate_on_match(2))
        self.assertEqual(True,  self.o.validate_on_match(3))

    def test__interval_mode_case_1(self):
        self.o.target_number = 1
        self.o.upper_target_number = 3
        self.o.mode = OffsetMode.interval
        self.assertEqual(True, self.o.validate_before_match(1))
        self.assertEqual(False,  self.o.validate_before_match(2))
        self.assertEqual(False, self.o.validate_before_match(3))

        self.assertEqual(False, self.o.validate_on_match(1))
        self.assertEqual(True,  self.o.validate_on_match(2))
        self.assertEqual(False, self.o.validate_on_match(3))

    def test__interval_mode_case_2(self):
        self.o.target_number = 1
        self.o.upper_target_number = 3
        self.o.mode = OffsetMode.interval_lower_may_equal
        self.assertEqual(True, self.o.validate_before_match(0))
        self.assertEqual(True,  self.o.validate_before_match(1))
        self.assertEqual(False,  self.o.validate_before_match(2))
        self.assertEqual(False, self.o.validate_before_match(3))

        self.assertEqual(False, self.o.validate_on_match(0))
        self.assertEqual(True,  self.o.validate_on_match(1))
        self.assertEqual(True,  self.o.validate_on_match(2))
        self.assertEqual(False, self.o.validate_on_match(3))

    def test__interval_mode_case_3(self):
        self.o.target_number = 1
        self.o.upper_target_number = 3
        self.o.mode = OffsetMode.interval_upper_may_equal
        self.assertEqual(True, self.o.validate_before_match(0))
        self.assertEqual(True, self.o.validate_before_match(1))
        self.assertEqual(True,  self.o.validate_before_match(2))
        self.assertEqual(False,  self.o.validate_before_match(3))
        self.assertEqual(False, self.o.validate_before_match(4))

        self.assertEqual(False, self.o.validate_on_match(0))
        self.assertEqual(False, self.o.validate_on_match(1))
        self.assertEqual(True,  self.o.validate_on_match(2))
        self.assertEqual(True,  self.o.validate_on_match(3))
        self.assertEqual(False, self.o.validate_on_match(4))

    def test__interval_mode_case_4(self):
        self.o.target_number = 1
        self.o.upper_target_number = 3
        self.o.mode = OffsetMode.interval_both_may_equal
        self.assertEqual(True, self.o.validate_before_match(0))
        self.assertEqual(True,  self.o.validate_before_match(1))
        self.assertEqual(True,  self.o.validate_before_match(2))
        self.assertEqual(False,  self.o.validate_before_match(3))
        self.assertEqual(False, self.o.validate_before_match(4))

        self.assertEqual(False, self.o.validate_on_match(0))
        self.assertEqual(True,  self.o.validate_on_match(1))
        self.assertEqual(True,  self.o.validate_on_match(2))
        self.assertEqual(True,  self.o.validate_on_match(3))
        self.assertEqual(False, self.o.validate_on_match(4))


class OffsetIntervalCheckingTests(unittest.TestCase):
    def setUp(self):
        self.o = Offset()

    def test__interval_check_equal_targets_should_fail_other_than_both_may_equal_mode(self):
        # target number and upper target number are the same at init
        self.o.target_number = 1
        self.o.upper_target_number = 1

        # no interval cases should pass
        self.o.mode = OffsetMode.equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.less_than
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.less_than_or_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.greater_then
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.greater_then_or_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        # interval modes other than both may equal should fail
        self.o.mode = OffsetMode.interval
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_lower_may_equal
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_upper_may_equal
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_both_may_equal
        self.assertEqual(True, self.o._validate_interval_limits())

    def test__interval_check_two_long_interval_cases(self):
        # target number and upper target number are the same at init
        self.o.target_number = 1
        self.o.upper_target_number = 2

        # no interval cases should pass
        self.o.mode = OffsetMode.equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.less_than
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.less_than_or_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.greater_then
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.greater_then_or_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        # pure interval with no equality should fail only
        self.o.mode = OffsetMode.interval
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_lower_may_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_upper_may_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_both_may_equal
        self.assertEqual(True, self.o._validate_interval_limits())

    def test__smaller_upper_target_should_fail_only_in_interval_mode(self):
        self.o.target_number = 1
        self.o.upper_target_number = 0
        # no interval cases should pass
        self.o.mode = OffsetMode.equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.less_than
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.less_than_or_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.greater_then
        self.assertEqual(True, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.greater_then_or_equal
        self.assertEqual(True, self.o._validate_interval_limits())

        # pure interval with no equality should fail only
        self.o.mode = OffsetMode.interval
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_lower_may_equal
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_upper_may_equal
        self.assertEqual(False, self.o._validate_interval_limits())

        self.o.mode = OffsetMode.interval_both_may_equal
        self.assertEqual(False, self.o._validate_interval_limits())


class OffsetParsingTests(unittest.TestCase):
    def setUp(self):
        self.o = Offset()

    # Equal
    def test__equal_mode_can_be_parsed(self):
        raw_offset = '3'
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(OffsetMode.equal, self.o.mode)

    def test__equal_mode_with_explicit_equal_sign_case_1(self):
        raw_offset = '==4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.equal, self.o.mode)

    def test__equal_mode_with_explicit_equal_sign_case_2(self):
        raw_offset = '  ==   74'
        self.o.parse(raw_offset)
        self.assertEqual(74, self.o.target_number)
        self.assertEqual(OffsetMode.equal, self.o.mode)

    def test__equal_mode_with_explicit_equal_sign_and_sequence_mark_case_1(self):
        raw_offset = '$==2'
        self.o.parse(raw_offset)
        self.assertEqual(2, self.o.target_number)
        self.assertEqual(OffsetMode.equal, self.o.mode)

    def test__equal_mode_with_explicit_equal_sign_and_sequence_mark_case_2(self):
        raw_offset = '  $ ==  2       '
        self.o.parse(raw_offset)
        self.assertEqual(2, self.o.target_number)
        self.assertEqual(OffsetMode.equal, self.o.mode)

    # Less than
    def test__less_than_mode_parsing_case_1(self):
        raw_offset = '<4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than, self.o.mode)

    def test__less_than_mode_parsing_case_2(self):
        raw_offset = '  <   4 '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than, self.o.mode)

    def test__less_than_mode_parsing_with_explicit_sequence_mark_case_1(self):
        raw_offset = '$<4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than, self.o.mode)

    def test__less_than_mode_parsing_with_explicit_sequence_mark_case_2(self):
        raw_offset = ' $ <  45'
        self.o.parse(raw_offset)
        self.assertEqual(45, self.o.target_number)
        self.assertEqual(OffsetMode.less_than, self.o.mode)

    # Less than or equal
    def test__less_than_or_equal_mode_parsing_case_1(self):
        raw_offset = '<=4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than_or_equal, self.o.mode)

    def test__less_than_or_equal_mode_parsing_case_2(self):
        raw_offset = '  <=  4  '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than_or_equal, self.o.mode)

    def test__less_than_or_equal_mode_parsing_with_explicit_sequence_mark_case_1(self):
        raw_offset = '$<=4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than_or_equal, self.o.mode)

    def test__less_than_or_equal_mode_parsing_with_explicit_sequence_mark_case_2(self):
        raw_offset = ' $ <= 4    '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.less_than_or_equal, self.o.mode)

    # Greate than
    def test__greater_than_mode_parsing_case_1(self):
        raw_offset = '>4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then, self.o.mode)

    def test__greater_than_mode_parsing_case_2(self):
        raw_offset = ' >    4 '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then, self.o.mode)

    def test__greater_than_mode_with_explicit_sequence_mark_case_1(self):
        raw_offset = '$>4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then, self.o.mode)

    def test__greater_than_mode_with_explicit_sequence_mark_case_2(self):
        raw_offset = '   $   >  4 '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then, self.o.mode)

    # Greater than or equal
    def test__greater_than_or_equal_mode_parsing_case_1(self):
        raw_offset = '>=4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then_or_equal, self.o.mode)

    def test__greater_than_or_equal_mode_parsing_case_2(self):
        raw_offset = ' >=    4 '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then_or_equal, self.o.mode)

    def test__greater_than_or_equal_mode_with_explicit_sequence_mark_case_1(self):
        raw_offset = '$>=4'
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then_or_equal, self.o.mode)

    def test__greater_than_or_equal_mode_with_explicit_sequence_mark_case_2(self):
        raw_offset = '   $   >=  4 '
        self.o.parse(raw_offset)
        self.assertEqual(4, self.o.target_number)
        self.assertEqual(OffsetMode.greater_then_or_equal, self.o.mode)

    # Interval
    def test__interval_mode_parsing_case_1(self):
        raw_offset = '3<$<5'
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval, self.o.mode)

    def test__interval_mode_parsing_case_2(self):
        raw_offset = '  3 <    $  < 5     '
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval, self.o.mode)

    # Interval upper may equal
    def test__interval_upper_may_equal_mode_parsing_case_1(self):
        raw_offset = '3<$<=5'
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval_upper_may_equal, self.o.mode)

    def test__interval_upper_may_equal_mode_parsing_case_2(self):
        raw_offset = '  3 <    $  <= 5     '
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval_upper_may_equal, self.o.mode)

    # Interval lower may equal
    def test__interval_lower_may_equal_mode_parsing_case_1(self):
        raw_offset = '3<=$<5'
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval_lower_may_equal, self.o.mode)

    def test__interval_lower_may_equal_mode_parsing_case_2(self):
        raw_offset = '  3 <=    $  < 5     '
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval_lower_may_equal, self.o.mode)

    # Interval both may equal
    def test__interval_both_may_equal_mode_parsing_case_1(self):
        raw_offset = '3<=$<=5'
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval_both_may_equal, self.o.mode)

    def test__interval_both_may_equal_mode_parsing_case_2(self):
        raw_offset = '  3 <=    $  <= 5     '
        self.o.parse(raw_offset)
        self.assertEqual(3, self.o.target_number)
        self.assertEqual(5, self.o.upper_target_number)
        self.assertEqual(OffsetMode.interval_both_may_equal, self.o.mode)

    # Invalid cases
    def test__mode_parsing_raise_error__on_invalid_syntax(self):
        raw_offset = 'some invalid stuff'
        with self.assertRaises(SyntaxError):
            self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_1(self):
        raw_offset = '6<$<6'
        with self.assertRaises(ValueError):
            self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_2(self):
        # this should pass
        raw_offset = '6<=$<=6'
        self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_3(self):
        raw_offset = '6<=$<6'
        with self.assertRaises(ValueError):
            self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_4(self):
        raw_offset = '6<$<=6'
        with self.assertRaises(ValueError):
            self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_5(self):
        raw_offset = '6<$<6'
        with self.assertRaises(ValueError):
            self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_6(self):
        raw_offset = '6<$<7'
        with self.assertRaises(ValueError):
            self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_7(self):
        raw_offset = '6<=$<7'
        self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_8(self):
        raw_offset = '6<$<=7'
        self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_9(self):
        raw_offset = '6<=$<=7'
        self.o.parse(raw_offset)

    def test__error_raised_on_invalid_interval_case_10(self):
        raw_offset = '6<=$<=5'
        with self.assertRaises(ValueError):
            self.o.parse(raw_offset)