#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
try:
    import mock
except ImportError:
    from unittest import mock

from rak.interface import cmd

class Parameterpreprocessing(TestCase):
    def test__empty_parameter_list_returns_empty_list(self):
        param_list = []
        expected = []
        result = cmd.prepare_args(param_list)
        self.assertEquals(expected, result)

    def test__single_dashed_parameter_returns_itself(self):
        param_list = ['-p']
        expected = ['-p']
        result = cmd.prepare_args(param_list)
        self.assertEquals(expected, result)

    def test__non_dashed_arguments_gets_concatenated(self):
        param_list = ['-p', 'hello', 'imre']
        expected = ['-p', 'hello imre']
        result = cmd.prepare_args(param_list)
        self.assertEquals(expected, result)

    def test__multiple_concatenation(self):
        param_list = ['-p', 'hello', 'imre', '-a', 'kakao']
        expected = ['-p', 'hello imre', '-a', 'kakao']
        result = cmd.prepare_args(param_list)
        self.assertEquals(expected, result)

    def test__non_dashed_argument_only(self):
        param_list = ['imre']
        expected = ['imre']
        result = cmd.prepare_args(param_list)
        self.assertEquals(expected, result)

    def test__non_dashed_argument_is_the_first(self):
        param_list = ['imre', '-a', 'kakao']
        expected = ['imre', '-a', 'kakao']
        result = cmd.prepare_args(param_list)
        self.assertEquals(expected, result)
