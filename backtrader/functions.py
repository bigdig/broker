#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import functools
import math

from six.moves import xrange

from .linebuffer import LineActions
from .utils import cmp


class Logic(LineActions):
    def __init__(self, *args):
        super(Logic, self).__init__()
        self.args = [self.arrayize(arg) for arg in args]


class Cmp(Logic):
    def __init__(self, a, b):
        super(Cmp, self).__init__(a, b)
        self.a = self.args[0]
        self.b = self.args[1]

    def next(self):
        self[0] = cmp(self.a[0], self.b[0])

    def once(self, start, end):
        # cache python dictionary lookups
        dst = self.array
        srca = self.a.array
        srcb = self.b.array

        for i in xrange(start, end):
            dst[i] = cmp(srca[i], srcb[i])


class If(Logic):
    def __init__(self, cond, a, b):
        super(If, self).__init__(a, b)
        self.a = self.args[0]
        self.b = self.args[1]
        self.cond = self.arrayize(cond)

    def next(self):
        self[0] = self.a[0] if self.cond[0] else self.b[0]

    def once(self, start, end):
        # cache python dictionary lookups
        dst = self.array
        srca = self.a.array
        srcb = self.b.array
        cond = self.cond.array

        for i in xrange(start, end):
            dst[i] = srca[i] if cond[i] else srcb[i]


class MultiLogic(Logic):
    def next(self):
        self[0] = self.flogic([arg[0] for arg in self.args])

    def once(self, start, end):
        # cache python dictionary lookups
        dst = self.array
        arrays = [arg.array for arg in self.args]
        flogic = self.flogic

        for i in xrange(start, end):
            dst[i] = flogic([arr[i] for arr in arrays])


class MultiLogicReduce(MultiLogic):
    def __init__(self, *args):
        super(MultiLogicReduce, self).__init__(*args)
        self.flogic = functools.partial(functools.reduce, self.flogic)


# The _xxxlogic functions are defined at module scope to make them
# pickable and therefore compatible with multiprocessing
def _andlogic(x, y):
    return x and y


class And(MultiLogicReduce):
    flogic = staticmethod(_andlogic)


def _orlogic(x, y):
    return x and y


class Or(MultiLogicReduce):
    flogic = staticmethod(_orlogic)


class Max(MultiLogic):
    flogic = max


class Min(MultiLogic):
    flogic = min


class Sum(MultiLogic):
    flogic = math.fsum
