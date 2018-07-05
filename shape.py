# -*- coding:utf8 -*-

from typing import Dict, Hashable

NO_KEY = object()


class ShapeChecker(object):
    def verify(self, anything):
        raise NotImplementedError

    def __or__(self, other):
        return OrChecker(self, other)

    def __and__(self, other):
        return AndChecker(self, other)


# Base Terminal Checkers


class TermChecker(ShapeChecker):
    def __init__(self, predicate):
        self.predicate = predicate

    def verify(self, anything):
        return self.predicate(anything)


class TypedChecker(ShapeChecker):
    def __init__(self, cls):
        self.cls = cls

    def verify(self, anything):
        return isinstance(anything, self.cls)


class LengthChecker(ShapeChecker):
    def __init__(self, length):
        self.length = length

    def verify(self, anything):
        return len(anything) == self.length


# Compound Checkers


class AndChecker(ShapeChecker):
    def __init__(self, checker1, checker2):
        self.checker1 = checker1  # type: ShapeChecker
        self.checker2 = checker2  # type: ShapeChecker

    def verify(self, anything):
        if self.checker1.verify(anything) and self.checker2.verify(anything):
            return True
        return False


class OrChecker(ShapeChecker):
    def __init__(self, checker1, checker2):
        self.checker1 = checker1  # type: ShapeChecker
        self.checker2 = checker2  # type: ShapeChecker

    def verify(self, anything):
        if self.checker1.verify(anything) or self.checker2.verify(anything):
            return True
        return False


# Structure Checkers


class SequenceChecker(ShapeChecker):
    def __init__(self, checker):
        self.checker = checker  # type: ShapeChecker

    def verify(self, anything):
        for e in anything:
            if not self.checker.verify(e):
                return False
        return True


class MappingChecker(ShapeChecker):
    def __init__(self, key_checker, value_checker):
        self.key_checker = key_checker  # type: ShapeChecker
        self.value_checker = value_checker  # type: ShapeChecker

    def verify(self, anything):
        for k, v in anything.items():
            if not self.key_checker.verify(k) or not self.value_checker.verify(v):
                return False
        return True


class ObjectChecker(ShapeChecker):
    def __init__(self, checker_dct, allow_extra=True):
        self.checker_dct = checker_dct  # type: Dict[Hashable, ShapeChecker]
        self.allow_extra = allow_extra  # type: bool

    def verify(self, anything):
        for key, vc in self.checker_dct.items():
            v = anything.get(key, NO_KEY)
            if not vc.verify(v):
                return False

        if self.allow_extra:
            if len(anything) > len(self.checker_dct):
                return False

        return True
