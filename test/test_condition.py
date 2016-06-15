import unittest
from replaceit.condition import (Comparer, Matcher, Sequence, Condition, Relation)

# ============================================================================
#    C O N D I T I O N   T E S T S
# ============================================================================

class ConditionTests(unittest.TestCase):
    def test__initial_values(self):
        c = Condition(1)
        self.assertEqual(c.id, 1)
        self.assertEqual(c.children, [None, None])
        self.assertEqual(c.arbitration_value, 0)
        self.assertEqual(c.related_conditions, [])
        self.assertEqual(c.condition_processor, None)
        self.assertEqual(c.is_termination, True)

    def test__adding_child_condition(self):
        c1 = Condition(1)
        c2 = Condition(2)
        c1.add_child(0, c2)
        self.assertEqual(c1.children[0], c2)
        self.assertEqual(c2.related_conditions, [c1])

    def test__adding_new_child_removes_itself_from_old_one(self):
        c1 = Condition(1)
        c2 = Condition(2)
        c3 = Condition(3)
        c1.add_child(1, c2)
        self.assertEqual(c2.related_conditions, [c1])
        c1.add_child(1, c3)
        self.assertEqual(c3.related_conditions, [c1])
        self.assertEqual(c2.related_conditions, [])

    def test__arbitration_protocol_for_five_nodes(self):
        term_c1 = Condition(1)
        term_c2 = Condition(2)
        pure_t_c = Condition(3)
        mix_c = Condition(4)
        pure_c_c = Condition(5)

        pure_t_c.add_child(0, term_c1)
        pure_t_c.add_child(1, term_c2)

        mix_c.add_child(0, pure_t_c)
        mix_c.add_child(1, term_c1)

        pure_c_c.add_child(0, pure_t_c)
        pure_c_c.add_child(1, mix_c)

        term_c1.execute_arbitration()
        term_c2.execute_arbitration()

        self.assertEqual(term_c1.arbitration_value, 0)
        self.assertEqual(term_c2.arbitration_value, 0)
        self.assertEqual(pure_t_c.arbitration_value, 2)
        self.assertEqual(mix_c.arbitration_value, 3)
        self.assertEqual(pure_c_c.arbitration_value, 5)


# ============================================================================
#    M A T C H E R   T E S T S
# ============================================================================

class MatchConditionTests(unittest.TestCase):
    def setUp(self):
        self.c = Matcher()

    def test__initialization_values(self):
        self.assertEqual(self.c.pattern_id, None)
        self.assertEqual(self.c.is_inverted, False)

    def test__pattern_is_not_set__raises_error_on_process(self):
        with self.assertRaises(AttributeError):
            self.c.process(1, 2, None)

    def test__can_process_data_case_1(self):
        data = {}
        self.c.pattern_id = 'A'
        expected = False
        result = self.c.process(1, 2, data)
        self.assertEqual(result, expected)

    def test__can_process_data_case_2(self):
        data = {'B': None}
        self.c.pattern_id = 'A'
        self.c.is_inverted = True
        expected = True
        result = self.c.process(1, 2, data)
        self.assertEqual(result, expected)

    def test__can_process_data_case_3(self):
        data = {'A': None}
        self.c.pattern_id = 'A'
        expected = True
        result = self.c.process(1, 2, data)
        self.assertEqual(result, expected)

    def test__can_process_data_case_4(self):
        data = {'A': None}
        self.c.pattern_id = 'A'
        self.c.is_inverted = True
        expected = False
        result = self.c.process(1, 2, data)
        self.assertEqual(result, expected)


# ============================================================================
#    C O M P A R E R   T E S T S
# ============================================================================

class CompareConditionValuePreparationsTests(unittest.TestCase):
    def test__preparation_int_should_be_int(self):
        v = '1'
        result = Comparer._prepare_value(v)
        expected = 1
        self.assertEqual(result, expected)

    def test__preparation_float_should_be_float(self):
        v = '1.99'
        result = Comparer._prepare_value(v)
        expected = 1.99
        self.assertEqual(result, expected)

    def test__preparation_hex_should_be_hex(self):
        v = '0x10'
        result = Comparer._prepare_value(v)
        expected = 16
        self.assertEqual(result, expected)

    def test__preparation_true_should_be_true_case1(self):
        v = 'true'
        result = Comparer._prepare_value(v)
        expected = True
        self.assertEqual(result, expected)

    def test__preparation_true_should_be_true_case2(self):
        v = 'True'
        result = Comparer._prepare_value(v)
        expected = True
        self.assertEqual(result, expected)

    def test__preparation_false_should_be_false_case1(self):
        v = 'false'
        result = Comparer._prepare_value(v)
        expected = False
        self.assertEqual(result, expected)

    def test__preparation_false_should_be_false_case2(self):
        v = 'False'
        result = Comparer._prepare_value(v)
        expected = False
        self.assertEqual(result, expected)

    def test__preparation_string_should_remain_string(self):
        v = 'true but hello and false'
        result = Comparer._prepare_value(v)
        expected = 'true but hello and false'
        self.assertEqual(result, expected)


class CompareConditionExecutionsTests(unittest.TestCase):
    def test__equal_conditional_execution_case_1(self):
        p1 = '1'
        p2 = '2'
        c = '=='
        result = Comparer._execute_condition(p1, p2, c)
        expected = False
        self.assertEqual(result, expected)

    def test__equal_conditional_execution_case_2(self):
        p1 = '1'
        p2 = '1'
        c = '=='
        result = Comparer._execute_condition(p1, p2, c)
        expected = True
        self.assertEqual(result, expected)

    def test__not_equal_conditional_execution_case_1(self):
        p1 = '1'
        p2 = '2'
        c = '!='
        result = Comparer._execute_condition(p1, p2, c)
        expected = True
        self.assertEqual(result, expected)

    def test__not_equal_conditional_execution_case_2(self):
        p1 = '1'
        p2 = '1'
        c = '!='
        result = Comparer._execute_condition(p1, p2, c)
        expected = False
        self.assertEqual(result, expected)

    def test__less_than_conditional_execution_case_1(self):
        p1 = '1'
        p2 = '1.1'
        c = '<'
        result = Comparer._execute_condition(p1, p2, c)
        expected = True
        self.assertEqual(result, expected)

    def test__less_than_conditional_execution_case_2(self):
        p1 = '1'
        p2 = '1'
        c = '<'
        result = Comparer._execute_condition(p1, p2, c)
        expected = False
        self.assertEqual(result, expected)

    def test__less_than_or_equal_conditional_execution_case_1(self):
        p1 = '1'
        p2 = '1'
        c = '<='
        result = Comparer._execute_condition(p1, p2, c)
        expected = True
        self.assertEqual(result, expected)

    def test__less_than_or_equal_conditional_execution_case_2(self):
        p1 = '1.1'
        p2 = '1'
        c = '<='
        result = Comparer._execute_condition(p1, p2, c)
        expected = False
        self.assertEqual(result, expected)

    def test__greater_than_conditional_execution_case_1(self):
        p1 = '4'
        p2 = '1'
        c = '>'
        result = Comparer._execute_condition(p1, p2, c)
        expected = True
        self.assertEqual(result, expected)

    def test__greater_than_conditional_execution_case_2(self):
        p1 = '0'
        p2 = '1'
        c = '>'
        result = Comparer._execute_condition(p1, p2, c)
        expected = False
        self.assertEqual(result, expected)

    def test__greater_than_or_equal_conditional_execution_case_1(self):
        p1 = '1'
        p2 = '1'
        c = '>='
        result = Comparer._execute_condition(p1, p2, c)
        expected = True
        self.assertEqual(result, expected)

    def test__greater_than_or_equal_conditional_execution_case_2(self):
        p1 = '1'
        p2 = '4'
        c = '>='
        result = Comparer._execute_condition(p1, p2, c)
        expected = False
        self.assertEqual(result, expected)

    def test__invalid_condition_raises_error(self):
        p1 = '1'
        p2 = '4'
        c = 'fg='
        with self.assertRaises(AttributeError):
            result = Comparer._execute_condition(p1, p2, c)


class CompareConditionTests(unittest.TestCase):
    def setUp(self):
        self.c = Comparer()

    def test__initialization_values(self):
        self.assertEqual(self.c.pattern_id, None)
        self.assertEqual(self.c.condition, '==')
        self.assertEqual(self.c.value, '')

    def test__pattern_is_not_set__raises_error_on_process(self):
        with self.assertRaises(AttributeError):
            self.c.process(None, None, 'something')

    def test__condition_in_main_group_with_default_values(self):
        data = {
            'A': {'match': 'hello'}
        }
        expected = True

        self.c.pattern_id = 'A'
        self.c.value = 'hello'

        result = self.c.process(None, None, data)
        self.assertEqual(result, expected)

    def test__condition_in_other_main_group(self):
        data = {
            'A': {'match': 'hello'},
            'B': {'match': '3'}
        }
        expected = True

        self.c.pattern_id = 'B'
        self.c.value = '5'
        self.c.condition = '<'

        result = self.c.process(None, None, data)
        self.assertEqual(result, expected)

    def test__condition_in_group(self):
        data = {
            'A': {'match': 'hello'},
            'A1': {'match': 'hello'},
            'A2': {'match': '44.678'}
        }
        expected = True

        self.c.pattern_id = 'A2'
        self.c.value = '44.678'

        result = self.c.process(None, None, data)
        self.assertEqual(result, expected)


class ConditionUpdateParsing(unittest.TestCase):
    def setUp(self):
        self.c = Comparer()

    # OffsetMode
    def test__update_relation_case_1(self):
        self.c.update('relation ==')
        self.assertEqual('==', self.c.condition)

    def test__update_relation_case_2(self):
        self.c.update('relation !=')
        self.assertEqual('!=', self.c.condition)

    def test__update_relation_case_3(self):
        self.c.update('relation <')
        self.assertEqual('<', self.c.condition)

    def test__update_relation_case_4(self):
        self.c.update('relation >')
        self.assertEqual('>', self.c.condition)

    def test__update_relation_case_5(self):
        self.c.update('relation <=')
        self.assertEqual('<=', self.c.condition)

    def test__update_relation_case_6(self):
        self.c.update('relation >=')
        self.assertEqual('>=', self.c.condition)

    def test__update_relation_case_7(self):
        self.c.update('relation ">="')
        self.assertEqual('>=', self.c.condition)

    # Value
    def test__update_value_case_1(self):
        self.c.update('value \'foo\'')
        self.assertEqual('foo', self.c.value)

    def test__update_value_case_2(self):
        self.c.update('value "foo"')
        self.assertEqual('foo', self.c.value)

    def test__update_value_case_3(self):
        self.c.update('value "56"')
        self.assertEqual('56', self.c.value)

    def test__update_value_case_4(self):
        self.c.update('value "56.99"')
        self.assertEqual('56.99', self.c.value)

    def test__update_value_case_5(self):
        self.c.update('value "0x42"')
        self.assertEqual('0x42', self.c.value)


# ============================================================================
#    R E L A T I O N   T E S T S
# ============================================================================

class RelationConditionTests(unittest.TestCase):
    def setUp(self):
        self.r = Relation()

    def test__initial_values(self):
        self.assertEqual(self.r.relation, 'AND')

    def test__parse_and(self):
        data = {1: True, 2: False}
        self.r.relation = 'AND'
        expected = False
        result = self.r.process(1, 2, data)
        self.assertEqual(expected, result)

    def test__parse_or(self):
        data = {1: True, 2: False}
        self.r.relation = 'OR'
        expected = True
        result = self.r.process(1, 2, data)
        self.assertEqual(expected, result)

    def test__parse_xor_case_1(self):
        data = {1: True, 2: False}
        self.r.relation = 'XOR'
        expected = True
        result = self.r.process(1, 2, data)
        self.assertEqual(expected, result)

    def test__parse_xor_case_2(self):
        data = {1: True, 2: True}
        self.r.relation = 'XOR'
        expected = False
        result = self.r.process(1, 2, data)
        self.assertEqual(expected, result)

    def test__invalid_relation_raises_error(self):
        data = {1: True, 2: True}
        self.r.relation = 'dfg'
        with self.assertRaises(AttributeError):
            result = self.r.process(1, 2, data)


# ============================================================================
#   S E Q U E N C E   T E S T S
# ============================================================================

class SequenceConditionTests(unittest.TestCase):
    def setUp(self):
        self.c = Sequence()

    def test__initial_values(self):
        self.assertEqual(self.c.parent_sequence, None)
        self.assertEqual(self.c.offset, 0)
        self.assertEqual(self.c.condition_id, None)

