import re


class SequenceNode(object):
    def __init__(self, id):
        self.proxy_counter = 0
        self.state = SequenceState.idle
        self.id = id
        self.condition_id = 0
        self.next_sequence = None
        self.prev_sequence = None
        self.offset = Offset()

    def is_trigger(self):
        return self.prev_sequence is None

    def is_termination(self):
        return self.next_sequence is None

    def add_prev_sequence(self, prev):
        self.prev_sequence = prev
        prev.next_sequence = self

    def process(self, data):
        return self._process(data, 0)

    def _process(self, data, proxy_number):
        if self.condition_id == 0:
            raise ValueError('No condition id was specified for sequence: ' + str(self))
        if self.state is SequenceState.idle:
            if self.condition_id in data.keys() and data[self.condition_id]:
                self.state = SequenceState.proxy
                return {'result': self.id, 'termination': self.is_termination()}
            else:
                return {'result': 0, 'termination': self.is_termination()}
        else:
            self.proxy_counter += 1


class SequenceState(object):
    """Enumeration object for the internal sequence states"""
    idle = 1
    proxy = 2


class Offset(object):
    """Offset is the responsible about validating the distance/offset between
    sequence nodes.  It can verify that a match occurs in the right offset.
    It works efficiently and saves as many unnecessary steps as possible.

    Offset features a string parser which you can set easily the required offset
    configuration.  The parser expects string configuration commands.

    The returned boolean value depends on the offset, the actual configuration, and
    the additional information if the request was made before an actual match, or
    on a match. This way Offset can optimise the processing, by eliminating the
    unnecessary steps and failing earlier, if the next step will be unnecessary anyway

    Dependency:
        re, enum

    Available modes:
        equal
            A mach is allowed only in a fixed offset from the previous sequence node match.
            [$==]{value}
            regexp: '^\s*\$?\s*(==)?\s*(\d+)\s*$'

        less_than
            A match has to occur before the specified offset.
            [$]<{value}
            regexp: '^\s*\$?\s*<\s*(\d+)\s*$'

        less_than_or_equal
            A match has to occur before or at the specified offset.
            [$]<={value}
            regexp: '^\s*\$?\s*<=\s*(\d+)\s*$'

        greater_than
            A match has to occur after the specified offset.
            [$]>{value}
            regexp: '^\s*\$?\s*>\s*(\d+)\s*$'

        greater_than_or_equal
            A match has to occur after or at the the specified offset.
            [$]>={value}
            regexp: '^\s*\$?\s*>=\s*(\d+)\s*$'

        interval
            A match has to occur inside an interval.
            {value}<$<{value}
            regexp: '^\s*(\d+)\s*<\s*\$\s*<\s*(\d+)\s*$'

        interval_lower_may_equal
             A match has to occur inside an interval or at the lower boundary.
             {value}<=$<{value}
             regexp: '^\s*(\d+)\s*<=\s*\$\s*<\s*(\d+)\s*$'

        interval_upper_may_equal
             A match has to occur inside an interval or at the upper boundary.
             {value}<$<={value}
             regexp: '^\s*(\d+)\s*<\s*\$\s*<=\s*(\d+)\s*$'

        interval_both_may_equal
             A match has to occur inside an interval or at the boundaries.
             {value}<=$<={value}
             regexp: '^\s*(\d+)\s*<=\s*\$\s*<=\s*(\d+)\s*$'

    Raises:
        ValueError at parsing if impossible interval configuration was added.
        SyntaxError at parsing error
    """
    def __init__(self):
        self.target_number = 0
        self.upper_target_number = 0
        self.mode = OffsetMode.equal

    def validate_before_match(self, offset):
        return self._validate(offset, False)

    def validate_on_match(self, offset):
        return self._validate(offset, True)

    def _validate(self, offset, match):
        if offset < 0:
            return False

        if self.mode is OffsetMode.equal:
            offset_smaller_before__match = not match and offset < self.target_number
            match_on_target = offset == self.target_number and match
            return match_on_target or offset_smaller_before__match

        if self.mode is OffsetMode.less_than:
            return offset < self.target_number

        if self.mode is OffsetMode.less_than_or_equal:
            return offset <= self.target_number

        if self.mode is OffsetMode.greater_then:
            return offset > self.target_number or not match

        if self.mode is OffsetMode.greater_then_or_equal:
            return offset >= self.target_number or not match

        if self.mode >= OffsetMode.interval:
            if not self._validate_interval_limits():
                raise ValueError('Offset lower limit should be lower!')

            if self.mode is OffsetMode.interval:
                is_over = offset+1 >= self.upper_target_number
                is_inside = self.target_number < offset < self.upper_target_number
                return (is_inside and match) or (not match and not is_over)

            if self.mode is OffsetMode.interval_lower_may_equal:
                is_over = offset+1 >= self.upper_target_number
                is_inside = self.target_number <= offset < self.upper_target_number
                return (is_inside and match) or (not match and not is_over)

            if self.mode is OffsetMode.interval_upper_may_equal:
                is_over = offset >= self.upper_target_number
                is_inside = self.target_number < offset <= self.upper_target_number
                return (is_inside and match) or (not match and not is_over)

            if self.mode is OffsetMode.interval_both_may_equal:
                is_over = offset >= self.upper_target_number
                is_inside = self.target_number <= offset <= self.upper_target_number
                return (is_inside and match) or (not match and not is_over)

    def _validate_interval_limits(self):
        if self.mode >= OffsetMode.interval:
            if self.target_number > self.upper_target_number:
                return False
            if self.mode is OffsetMode.interval:
                if self.target_number == self.upper_target_number:
                    return False
                elif self.target_number+1 == self.upper_target_number:
                    return False
                else:
                    return True

            if self.mode is OffsetMode.interval_lower_may_equal:
                if self.target_number == self.upper_target_number:
                    return False
                else:
                    return True

            if self.mode is OffsetMode.interval_upper_may_equal:
                if self.target_number == self.upper_target_number:
                    return False
                else:
                    return True

            if self.mode is OffsetMode.interval_both_may_equal:
                return True
        else:
            return True

    def parse(self, raw_offset):
        equal_match = re.compile('^\s*\$?\s*(==)?\s*(\d+)\s*$').match(raw_offset)
        less_than_match = re.compile('^\s*\$?\s*<\s*(\d+)\s*$').match(raw_offset)
        less_than_or_e_m = re.compile('^\s*\$?\s*<=\s*(\d+)\s*$').match(raw_offset)
        greater_than_match = re.compile('^\s*\$?\s*>\s*(\d+)\s*$').match(raw_offset)
        greater_than_o_e_m = re.compile('^\s*\$?\s*>=\s*(\d+)\s*$').match(raw_offset)
        interval_m = re.compile('^\s*(\d+)\s*<\s*\$\s*<\s*(\d+)\s*$').match(raw_offset)
        interval_l_m = re.compile('^\s*(\d+)\s*<=\s*\$\s*<\s*(\d+)\s*$').match(raw_offset)
        interval_u_m = re.compile('^\s*(\d+)\s*<\s*\$\s*<=\s*(\d+)\s*$').match(raw_offset)
        interval_b_m = re.compile('^\s*(\d+)\s*<=\s*\$\s*<=\s*(\d+)\s*$').match(raw_offset)

        something_matched = False

        if equal_match:
            self.target_number = int(equal_match.group(2))
            self.mode = OffsetMode.equal
            something_matched |= True

        if less_than_match:
            self.target_number = int(less_than_match.group(1))
            self.mode = OffsetMode.less_than
            something_matched |= True

        if less_than_or_e_m:
            self.target_number = int(less_than_or_e_m.group(1))
            self.mode = OffsetMode.less_than_or_equal
            something_matched |= True

        if greater_than_match:
            self.target_number = int(greater_than_match.group(1))
            self.mode = OffsetMode.greater_then
            something_matched |= True

        if greater_than_o_e_m:
            self.target_number = int(greater_than_o_e_m.group(1))
            self.mode = OffsetMode.greater_then_or_equal
            something_matched |= True

        if interval_m:
            self.target_number = int(interval_m.group(1))
            self.upper_target_number = int(interval_m.group(2))
            self.mode = OffsetMode.interval
            something_matched |= True

        if interval_u_m:
            self.target_number = int(interval_u_m.group(1))
            self.upper_target_number = int(interval_u_m.group(2))
            self.mode = OffsetMode.interval_upper_may_equal
            something_matched |= True

        if interval_l_m:
            self.target_number = int(interval_l_m.group(1))
            self.upper_target_number = int(interval_l_m.group(2))
            self.mode = OffsetMode.interval_lower_may_equal
            something_matched |= True

        if interval_b_m:
            self.target_number = int(interval_b_m.group(1))
            self.upper_target_number = int(interval_b_m.group(2))
            self.mode = OffsetMode.interval_both_may_equal
            something_matched |= True

        if not self._validate_interval_limits():
            raise ValueError('Invalid offset interval: ' + raw_offset)

        if not something_matched:
            raise SyntaxError('Invalid offset specifier: ' + raw_offset)


class OffsetMode(object):
    """Enumeration object for the Offset states"""
    equal = 1
    less_than = 2
    less_than_or_equal = 3
    greater_then = 4
    greater_then_or_equal = 5
    interval = 6
    interval_lower_may_equal = 7
    interval_upper_may_equal = 8
    interval_both_may_equal = 9

