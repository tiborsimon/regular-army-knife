#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tibor Simon'

import rak

def prepare_args(args):
    ret = []
    buff = None
    for a in args:
        if a.startswith('-'):
            if buff:
                ret.append(buff)
                buff = None
            ret.append(a)
        else:
            if buff:
                buff += ' ' + a
            else:
                buff = a
    if buff:
        ret.append(buff)
    return ret
