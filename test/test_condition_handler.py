import unittest
from replaceit.condition import (ConditionHandler, NoConditionError,
                                 ConditionLoopError)


class ConditionHandlerBasicTests(unittest.TestCase):
    def setUp(self):
        self.ch = ConditionHandler()

    def test__initial_values(self):
        self.assertEqual(self.ch.conditions, [])
        self.assertEqual(self.ch.prev_id, 0)

    def test__adding_conditions(self):
        result = self.ch.add_match_condition()
        expected = 1
        self.assertEqual(expected, result)

        result = self.ch.add_compare_condition()
        expected = 2
        self.assertEqual(expected, result)

        result = self.ch.add_relation_condition()
        expected = 3
        self.assertEqual(expected, result)
        self.assertEqual(3, len(self.ch.conditions))

    def test_get_condition_for_id(self):
        self.ch.add_match_condition()
        test_id = self.ch.add_compare_condition()

        condition = self.ch.get_condition(test_id)
        self.assertEqual(test_id, condition.id)

    def test__connecting_conditions(self):
        t1_id = self.ch.add_match_condition()
        t2_id = self.ch.add_match_condition()
        rel_id = self.ch.add_relation_condition()

        self.ch.add_child_for(rel_id, 0, t1_id)
        self.ch.add_child_for(rel_id, 1, t2_id)

        eval_c = self.ch.get_condition(rel_id)
        self.assertEqual(t1_id, eval_c.children[0].id)
        self.assertEqual(t2_id, eval_c.children[1].id)


class ArbitrationTests(unittest.TestCase):
    def setUp(self):
        self.ch = ConditionHandler()

    def test__arbitration_protocol(self):
        rel_id = self.ch.add_relation_condition()
        t1_id = self.ch.add_match_condition()
        t2_id = self.ch.add_match_condition()

        self.ch.add_child_for(rel_id, 0, t1_id)
        self.ch.add_child_for(rel_id, 1, t2_id)

        self.ch._execute_arbitration()

        self.assertEqual(rel_id, self.ch.conditions[2].id)


class LoopDetectionTests(unittest.TestCase):
    def setUp(self):
        self.ch = ConditionHandler()

    def test__loop_protocol_for_terminations__returns_false(self):
        t1_id = self.ch.add_compare_condition()
        t2_id = self.ch.add_match_condition()
        t1 = self.ch.get_condition(t1_id)
        t2 = self.ch.get_condition(t2_id)
        self.assertEqual(False, t1._loop_protocol(None))
        self.assertEqual(False, t2._loop_protocol(None))

    def test__loop_protocol_for_empty_related_list__resturns_false(self):
        r_id = self.ch.add_relation_condition()
        r = self.ch.get_condition(r_id)
        self.assertEqual(False, r._loop_protocol(None))

    def test__starting_node_in_the_related_list__returns_true(self):
        r1_id = self.ch.add_relation_condition()
        r2_id = self.ch.add_relation_condition()
        r1 = self.ch.get_condition(r1_id)
        r2 = self.ch.get_condition(r2_id)

        try:
            self.ch.add_child_for(r2_id, 1, r1_id)
            self.ch.add_child_for(r1_id, 0, r2_id)
        except ConditionLoopError:
            pass

        self.assertEqual(True, r2._loop_protocol(r1))

    def test__get_possible_children__two_relation_with_loop(self):
        r1_id = self.ch.add_relation_condition()
        r2_id = self.ch.add_relation_condition()

        self.ch.add_child_for(r2_id, 0, r1_id)

        with self.assertRaises(ConditionLoopError):
            self.ch.add_child_for(r1_id, 0, r2_id)

    def test__get_possible_children__three_relation_with_loop(self):
        r1_id = self.ch.add_relation_condition()
        r2_id = self.ch.add_relation_condition()
        r3_id = self.ch.add_relation_condition()

        self.ch.add_child_for(r2_id, 0, r1_id)
        self.ch.add_child_for(r3_id, 0, r2_id)

        with self.assertRaises(ConditionLoopError):
            self.ch.add_child_for(r1_id, 0, r3_id)

    def test__get_possible_children__four_relation_with_loop(self):
        r1_id = self.ch.add_relation_condition()
        r2_id = self.ch.add_relation_condition()
        r3_id = self.ch.add_relation_condition()
        r4_id = self.ch.add_relation_condition()

        self.ch.add_child_for(r2_id, 0, r1_id)
        self.ch.add_child_for(r3_id, 0, r2_id)
        self.ch.add_child_for(r4_id, 0, r3_id)

        with self.assertRaises(ConditionLoopError):
            self.ch.add_child_for(r1_id, 0, r4_id)

class ConditionUpdateTests(unittest.TestCase):
    def setUp(self):
        self.ch = ConditionHandler()

    def test__can_call_update(self):
        self.ch.update('')

    def test__update_first_child(self):
        self.ch.update('')


class ProcessConditions(unittest.TestCase):
    def setUp(self):
        self.ch = ConditionHandler()

    def test__process_one_matcher(self):
        c_id = self.ch.add_match_condition()
        c = self.ch.get_condition(c_id)
        c.condition_processor.pattern_id = 'A'

        data = {'A': {'match': 'foo'}}

        expected = {1: True}
        result = self.ch.process(data)

        self.assertEqual(expected, result)

    def test__process_two_matchers(self):
        c1_id = self.ch.add_match_condition()
        c1 = self.ch.get_condition(c1_id)
        c1.condition_processor.pattern_id = 'A'

        c2_id = self.ch.add_match_condition()
        c2 = self.ch.get_condition(c2_id)
        c2.condition_processor.pattern_id = 'A3'

        data = {'A': {'match': 'foo'}, 'A3': {'match': 'foo'}}

        expected = {1: True, 2: True}
        result = self.ch.process(data)

        self.assertEqual(expected, result)

    def test__process_matcher_and_comparer(self):
        c1_id = self.ch.add_match_condition()
        c1 = self.ch.get_condition(c1_id)
        c1.condition_processor.pattern_id = 'A'

        c2_id = self.ch.add_compare_condition()
        c2 = self.ch.get_condition(c2_id)
        c2.condition_processor.pattern_id = 'A3'
        c2.condition_processor.value = 'hello'

        data = {'A': {'match': 'foo'}, 'A3': {'match': 'hello'}}

        expected = {1: True, 2: True}
        result = self.ch.process(data)

        self.assertEqual(expected, result)
