import re


class NoConditionError(Exception):
    pass


class ConditionLoopError(Exception):
    pass


class NoActionError(Exception):
    pass



class Condition(object):
    """Object to represent a condition. Conditions can be interconnected and can
    have unique processor object that can produce output.  It provides a base for
    the arbitration protocol.

    Arbitration protocol
        A process which provides a way to sort the condition entries in an upper
        level to be able to process the pattern input in one sequential step.

    Loop protocol
        A protocol that finds loops in the newly created relation. If a loop is
        detected an exception will be raised.
    """
    def __init__(self, new_id):
        self.is_termination = True
        self.id = new_id
        self.condition_processor = None
        self.related_conditions = []
        self.arbitration_value = 0
        self.children = [None, None]

    def add_child(self, index, new_child):
        child = self.children[index]
        if child:
            child.remove_related(self)
        self.children[index] = new_child
        new_child.add_related(self)

    def add_related(self, reference):
        self.related_conditions.append(reference)

    def remove_related(self, reference):
        self.related_conditions.remove(reference)

    def execute_arbitration(self):
        for related in self.related_conditions:
            related._arbitration_protocol()

    def _arbitration_protocol(self):
        self.arbitration_value += 1
        for related in self.related_conditions:
            related._arbitration_protocol()

    def _loop_protocol(self, starting_condition):
        if self.is_termination or 0 == len(self.related_conditions):
            return False
        else:
            for rel in self.related_conditions:
                if starting_condition == rel:
                    return True
                else:
                    return rel._loop_protocol(starting_condition)

    def process(self, data):
        c1 = None
        if self.children[0]:
            c1 = self.children[0].id
        c2 = None
        if self.children[1]:
            c2 = self.children[1].id
        result = self.condition_processor.process(c1, c1, data)
        return {self.id: result}


class Matcher(object):
    """Condition object that chacks if the given pattern id matches or not through the content.
    It has two parameters you can set up the desired behavior:

        pattern_id: valid pattern id you want to check
        has_to_match [True/False]: pattern should match or not to pass this condition
    """
    def __init__(self):
        self.is_inverted = False
        self.pattern_id = None

    def process(self, c1, c2, data):
        if not self.pattern_id:
            raise AttributeError('No pattern id was set..')
        else:
            if self.pattern_id in data.keys():
                return not self.is_inverted
            else:
                return self.is_inverted


class Comparer(object):
    """This condition is be able to compare patterns and pattern groups to predefined
    values, by applying the predefined condition on them.  Automatic type parsing is
    happening too.

        pattern_id: a valid pattern id you want to compare
        condition: the condition you want to use during the comparison
                   [==, !=, <, <=, >, >=]
        value: value you want to compare the matched pattern content

    Every parameter is a string.

    Precondition:
        A matching pattern is a pre-requirement to produce positive output!

    Conditions:
        Conditions can be assigned with a string, and will be parsed internally.

        [result] = <matched content> [condition] <given value>

        Available conditions:
            [==, !=, <, <=, >, >=]
    """
    def __init__(self):
        self.value = ''
        self.condition = '=='
        self.pattern_id = None

    def process(self, c1, c2, data):
        if not self.pattern_id:
            raise AttributeError
        else:
            ret = False
            value = data[self.pattern_id]['match']
            ret = Comparer._execute_condition(value, self.value, self.condition)
            return ret

    @staticmethod
    def _prepare_value(v):
        try:
            v = int(v)
        except ValueError:
            try:
                v = int(v, 16)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    p = re.compile('^(true|True)$')
                    m = p.match(v)
                    if m:
                        v = True
                    else:
                        p = re.compile('^(false|False)$')
                        m = p.match(v)
                        if m:
                            v = False
        return v

    @staticmethod
    def _execute_condition(p1, p2, c):
        p1 = Comparer._prepare_value(p1)
        p2 = Comparer._prepare_value(p2)
        if c == '==':
            return p1 == p2
        if c == '!=':
            return p1 != p2
        if c == '<':
            return p1 < p2
        if c == '<=':
            return p1 <= p2
        if c == '>':
            return p1 > p2
        if c == '>=':
            return p1 >= p2
        raise AttributeError('Invalid condition: ' + c)

    def update(self, string):
        relation_pattern = re.compile('\s*relation\s+"?([=<>!]+)"?\s*')
        relation_match = relation_pattern.search(string)
        if relation_match:
            self.condition = relation_match.group(1)

        value_pattern = re.compile('\s*value\s+("([^"]+)"|\'([^\']+)\')\s*')
        value_match = value_pattern.search(string)
        if value_match:
            if value_match.group(3):
                self.value = value_match.group(3)
            if value_match.group(2):
                self.value = value_match.group(2)


class Relation(object):
    def __init__(self):
        self.relation = 'AND'

    def process(self, c1, c2, data):
        if self.relation == 'AND':
            return data[c1] and data[c2]
        if self.relation == 'OR':
            return data[c1] or data[c2]
        if self.relation == 'XOR':
            return (data[c1] or data[c2]) and not (data[c1] and data[c2])
        raise AttributeError('Invalid relation: ' + self.relation)


class Sequence(object):
    def __init__(self):
        self.condition_id = None
        self.offset = 0
        self.parent_sequence = None


class ConditionHandler(object):
    """ConditionHandler is the holder object for the conditions.  It's main purpose is to
    provide an interface for condition creation linkage and processing.
    """
    def __init__(self):
        self.prev_id = 0
        self.conditions = []

    def _get_new_id(self):
        self.prev_id += 1
        return self.prev_id

    def add_match_condition(self):
        return self._add_condition(Matcher(), True)

    def add_compare_condition(self):
        return self._add_condition(Comparer(), True)

    def add_relation_condition(self):
        return self._add_condition(Relation(), False)

    def _add_condition(self, processor, is_termination):
        new_id = self._get_new_id()
        new_condition = Condition(new_id)
        new_condition.is_termination = is_termination
        new_condition.condition_processor = processor
        self.conditions.append(new_condition)
        return new_id

    def _execute_arbitration(self):
        terminators = [t for t in self.conditions if t.is_termination]
        for t in terminators:
            t.execute_arbitration()
        self.conditions.sort(key=lambda c: c.arbitration_value)

    def get_condition(self, wanted_id):
        return [x for x in self.conditions if x.id == wanted_id][0]

    def add_child_for(self, parent_id, child_index, child_id):
        parent = self.get_condition(parent_id)
        child = self.get_condition(child_id)
        parent.add_child(child_index, child)
        self.loop_test(child)

    def loop_test(self, child):
        for rel in child.related_conditions:
            if rel._loop_protocol(child):
                raise ConditionLoopError()

    def process(self, data):
        self._execute_arbitration()
        ret = {}
        for c in self.conditions:
            ret.update(c.process(data))
        return ret

    def update(self, param):
        pass







