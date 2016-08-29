#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def add():
    pass

def delete():
    pass

def change():
    pass

def info():
    pass

def run():
    pass

def serialize():
    pass

def deserialize():
    pass


class InvalidPatternIdError(SyntaxError):
    pass


class NoPatternError(Exception):
    pass


class Pattern(object):
    """Regular expression pattern object

    Dependency:
        re

    It's main purpose is to contain and validate the regular expression patterns
    and it's corresponding compiled pattern object.  It collects the raw groups
    as well for displaying purpose.

    :type pattern: _sre.SRE_Pattern  # compiled re pattern object
    :type groups: tuple              # regexp groups including the pattern itself at the first place
    """

    def __init__(self):
        self.pattern = None
        self.groups = ('',)

    def __str__(self):
        if self.pattern:
            ret = 'Pattern object\n'
            ret += '\tregexp pattern: {}\n'.format(repr(self.groups[0]))
            ret += '\tregexp groups:  {}'.format(repr(self.groups[1:]))
            return ret
        else:
            return 'An empty pattern'

    def add_expression(self, pattern):
        """Interface method for adding and validating regular expressions.  The given
        pattern string will be validated and will be saved if passed the validation.
        Regexp groups will be separated and will be accessible via the groups property.

        :type pattern: str

        :raises: SyntaxError
        """
        try:
            self.pattern = re.compile(pattern)
            temp_groups = list(re.findall('(\([^\(]+\))', pattern))
            if temp_groups:
                temp_groups.insert(0, pattern)
            else:
                temp_groups = [pattern]
            self.groups = tuple(temp_groups)
        except re.error:
            raise SyntaxError('Invalid regular expression: "' + pattern + '"')

    def execute(self, raw_text):
        """Method for producing pattern results.  If the pattern matches, this method
        return a dictionary having two keys: results and indexes.

        returned_dictionary_on_match = {
            'results': ('whole pattern matched content', 'first group matched content', ...),
            'spans': ((starting index for results[0],  index after results[0] last character), (..., ...))
        }

        Example:
            String:  'Foo:12'
            Pattern: '(\w{3}):(\d+)'

            Result:
            {
                'results': ('Foo:12', 'Foo', '12'),
                'spans': ((0, 6), (0, 3), (4, 6))
            }

        If the pattern couldn't match None will be returned.
        """
        if not self.pattern:
            raise ValueError('Pattern has to be initialized with some value')

        # construct group matches from index
        m = self.pattern.search(raw_text)
        if m:
            ret = {
                'results': [],
                'spans': []
            }
            for i in range(1, len(m.groups()) + 1):
                group = m.group(i)
                start = m.start(i)
                group_len = len(group)
                ret['results'].append(group)
                ret['spans'].append((start, start + group_len))

            # construct whole pattern match
            m = self.pattern.search(raw_text)
            ret['results'].insert(0, m.group())
            ret['spans'].insert(0, m.span())

            # convert lists to tuples
            ret['results'] = tuple(ret['results'])
            ret['spans'] = tuple(ret['spans'])
        else:
            ret = None
        return ret


class PatternHandler(object):
    """Pattern handler object that keeps track of the actual pattern list and
    provides an interface for interrogating and modifying the patterns with ids.

    Dependency: re
    """
    def __init__(self):
        self.patterns = []
        # ASCII code of the letter before 'A'. The pattern generation method
        # will increment first this number and assigns the converted one to
        # the newly created condition.
        self.last_id = 0

    def __str__(self):
        if self.patterns:
            ret = 'PatternHandler\n'
            for element in self.patterns:
                ret += '\t{}: '.format(element['id'])
                if element['pattern'].pattern:
                    ret += '\'{}\'\n'.format(element['pattern'].groups[0])
                else:
                    ret += 'Empty pattern\n'
            return ret
        else:
            return 'An empty PatternHandler'

    def add_pattern(self):
        """Adds a new empty pattern to the pattern list and returns it's id you can
        refer to it in the future. If the pattern list reaches the limit (26 patterns)
        an OverflowError will be raised.

        Raises: OverflowError
        """
        self.last_id += 1
        new_entry = {'id': chr(self.last_id), 'pattern': Pattern()}
        self.patterns.append(new_entry)
        return 'P{}'.format(self.last_id)

    def remove_pattern(self, raw_id):
        """Removes a pattern specified with the given id. Id validation is happening
        here as well.

        Raises: InvalidPatternIdError
        """
        i = self._get_index_for_id(raw_id)
        self.patterns.pop(i)

    def modify_pattern(self, raw_id, new_pattern):
        """Removes a pattern specified with the given id. Id validation is happening
        here as well.

        Raises: InvalidPatternIdError
        """
        pattern = self._get_pattern_for_id(raw_id)
        pattern.add_expression(new_pattern)

    def get_parsed_id(self, raw_id):
        """This method uses the two hidden method to provide parsed main id and
        group index after validation. In case of invalid id an InvalidPatternIdError
        will raised.

        Raises: InvalidPatternIdError
        """
        parsed_id = PatternHandler._parse_id(raw_id)
        try:
            self._validate_id(parsed_id)
        except InvalidPatternIdError:
            raise InvalidPatternIdError('Invalid ID: ' + raw_id)
        return parsed_id

    def get_main_id_list(self):
        ret = []
        for element in self.patterns:
            ret.append(element['id'])
        return tuple(ret)

    def get_full_id_list(self, specific_id=None):
        ret = []
        for element in self.patterns:
            g = [element['id']]
            for i in range(1, len(element['pattern'].groups)):
                g.append(g[0]+str(i))
            ret.append(tuple(g))
        if specific_id:
            i = self._get_index_for_id(specific_id)
            return ret[i]
        else:
            return tuple(ret)

    def execute(self, content):
        """Executes the search for the given content which has to be an iterable object.
        As a result it returns a dictionary with the keyed with the patters ids.

        returned_dictionary = {
            '<first_pattern_id_whole_pattern>': {'match': '...', 'span': (x, y)},
            '<first_pattern_id_first_group>': {'match': '...', 'span': (x, y)},
            '<first_pattern_id_second_group>': {'match': '...', 'span': (x, y)},
            ...
            '<second_pattern_id_whole_pattern>': {'match': '...', 'span': (x, y)},
            '<second_pattern_id_first_group>': {'match': '...', 'span': (x, y)},
            '<second_pattern_id_second_group>': {'match': '...', 'span': (x, y)},
            ...
        }

        returned_dictionary_example = {
            'A': {'match': 'foo', 'span': (8, 11)},
            'A1': {'match': 'foo', 'span': (8, 11)}
        }
        """
        if not self.patterns:
            raise NoPatternError
        ret = {}
        for pattern in self.patterns:
            current_key = pattern['id']
            result = pattern['pattern'].execute(content)
            if result:
                for i in range(len(result['results'])):
                    ret[current_key] = {
                        'match': result['results'][i],
                        'span': result['spans'][i]
                    }
                    current_key = pattern['id'] + str(i+1)
        return ret

    def _get_pattern_for_id(self, raw_id):
        parsed_id = self.get_parsed_id(raw_id)
        for element in self.patterns:
            if element['id'] == parsed_id['main']:
                return element['pattern']

    def _get_index_for_id(self, raw_id):
        parsed_id = self.get_parsed_id(raw_id)
        for i in range(len(self.patterns)):
            if self.patterns[i]['id'] == parsed_id['main']:
                return i

    @classmethod
    def _parse_id(cls, raw_id):
        """Translates pattern ids to indexes.  The first pattern can be identified as A,
        the second is B and so on.  Pattern groups can be indexed with numbers.  For
        example, you can index the second pattern's second group with B2.  The method
        returns a tuple with two element.

        returned_dictionary = {
            'main': <pattern indexes from 0>,
            'group': <group indexes from 1. 0 indexes the whole pattern>
        }
        """
        m = re.match('P(\d+)(.(\d+))?', raw_id)
        if m:
            main_index = int(m.group(1)) - 1
            try:
                group_index = int(m.group(3)) - 1
            except TypeError:
                group_index = -1
            parsed_id = {'main': main_index, 'group': group_index}
            return parsed_id
        else:
            raise InvalidPatternIdError('Invalid ID: ' + raw_id)

    def _validate_id(self, parsed_id):
        """Validates the provided indexes.  If the validation fails, an IndexError
        exception will raised.
        """
        for pattern in self.patterns:
            if pattern['id'] == parsed_id['main']:
                if parsed_id['group'] < len(pattern['pattern'].groups):
                    break
                else:
                    raise InvalidPatternIdError()
        else:
            raise InvalidPatternIdError()
