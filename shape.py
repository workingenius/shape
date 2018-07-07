# -*- coding:utf8 -*-

from __future__ import print_function, unicode_literals

from typing import Dict, Hashable

from summary import Summary

NO_KEY = object()


class ShapeChecker(object):
    def verify(self, anything, path):
        raise NotImplementedError

    def __or__(self, other):
        return OrChecker(self, other)

    def __and__(self, other):
        return AndChecker(self, other)


# Base Terminal Checkers


class TermChecker(ShapeChecker):
    def __init__(self, predicate):
        self.predicate = predicate

    def verify(self, anything, path=None):
        if not path:
            path = []

        if self.predicate(anything):
            return Summary(success=True)
        else:
            return Summary(success=False, path=path, error='predicate fail')


class TypedChecker(ShapeChecker):
    def __init__(self, cls):
        self.cls = cls

    def verify(self, anything, path=None):
        if not path:
            path = []

        if isinstance(anything, self.cls):
            return Summary(success=True)
        else:
            return Summary(success=False, path=path, error='not an instance of {0}'.format(self.cls))


class LengthChecker(ShapeChecker):
    def __init__(self, length):
        self.length = length  # type: int

    def verify(self, anything, path=None):
        if not path:
            path = []

        if not getattr(anything, '__len__', None):
            return Summary(success=False, path=path, error='has no __len__')

        if len(anything) == self.length:
            return Summary(success=True)
        else:
            return Summary(success=False, path=path, error='not length of {0}'.format(self.length))


class EnumChecker(ShapeChecker):
    def __init__(self, options):
        self.options = list(options)  # type: list

    def verify(self, anything, path=None):
        if not path:
            path = []

        if anything in self.options:
            return Summary(success=True)
        else:
            return Summary(success=False, path=path,
                           error='{0} not in options'.format(repr(anything)))


# Compound Checkers


class AndChecker(ShapeChecker):
    def __init__(self, checker1, checker2):
        self.checker1 = checker1  # type: ShapeChecker
        self.checker2 = checker2  # type: ShapeChecker

    def verify(self, anything, path=None):
        if not path:
            path = []

        s1 = self.checker1.verify(anything, path=path)
        if s1:
            # 若 checker1 没错，再检查 checker2
            # 不论对错，最终结果都是 checker2 的
            return self.checker2.verify(anything, path=path)

        # 若 checker1 出错，checker2 就不用检查了，总结就用 checker1 的
        else:
            return s1


class OrChecker(ShapeChecker):
    def __init__(self, checker1, checker2):
        self.checker1 = checker1  # type: ShapeChecker
        self.checker2 = checker2  # type: ShapeChecker

    def verify(self, anything, path=None):
        if not path:
            path = []

        s1 = self.checker1.verify(anything, path=path)
        if s1:
            # 如果 checker1 通过了，就不用检查 checker2 了，总结就用 checker1 的
            return s1

        # 如果 checker1 没通过，继续检查 checker2
        else:
            # 不论对错，总结都以 checker2 为准
            return self.checker2.verify(anything, path=path)


# Structure Checkers


class SequenceChecker(ShapeChecker):
    def __init__(self, checker):
        self.checker = checker  # type: ShapeChecker

    def verify(self, anything, path=None):
        if not path:
            path = []

        if not getattr(anything, '__iter__', None):
            return Summary(success=False, path=path, error='not iterable')

        for i, e in enumerate(anything):
            s = self.checker.verify(e, path=path + [i   ])
            if not s:
                return s
        return Summary(success=True)


class MappingChecker(ShapeChecker):
    def __init__(self, key_checker, value_checker):
        self.key_checker = key_checker  # type: ShapeChecker
        self.value_checker = value_checker  # type: ShapeChecker

    def verify(self, anything, path=None):
        if not path:
            path = []

        if not getattr(anything, 'items', None):
            return Summary(success=False, path=path, error='not a dict')

        for k, v in anything.items():
            next_path = path + [k]

            ks, vs = None, None

            ks = self.key_checker.verify(k, path=next_path)
            if ks:
                vs = self.value_checker.verify(v, path=next_path)

                # 如果 key checker 和 value checker 都通过了，就继续做下一组 kv pair
                if vs:
                    pass

                # 如果 value checker 没通过，总结就是 value checker 的报错
                else:
                    return vs

            # 如果 key checker 没通过，总结就是 key checker 的报错，value checker 也不用做了
            else:
                return ks

        # 当所有 kv pair 都通过时，给出正向总结
        return Summary(success=True)


class DictChecker(ShapeChecker):
    def __init__(self, checker_dct, allow_extra=True):
        self.checker_dct = checker_dct  # type: Dict[Hashable, ShapeChecker]
        self.allow_extra = allow_extra  # type: bool

    def verify(self, anything, path=None):
        if not path:
            path = []

        if not getattr(anything, 'items', None) or (not getattr(anything, '__len__', None)):
            return Summary(success=False, path=path, error='not a dict')

        for key, vc in self.checker_dct.items():
            v = anything.get(key, NO_KEY)

            s = vc.verify(v, path=path + [key])
            if not s:
                return s

        if not self.allow_extra:
            if len(anything) > len(self.checker_dct):
                return Summary(success=False, path=path, error='has extra keys')

        return Summary(success=True)


# None Checkers


class NoneChecker(ShapeChecker):
    def verify(self, anything, path=None):
        if not path:
            path = []

        if anything is None:
            return Summary(success=True)
        else:
            return Summary(success=False, path=path, error='is not none')


class OptionalChecker(ShapeChecker):
    def __init__(self, checker):
        self.checker = checker

    def verify(self, anything, path=None):
        if not path:
            path = []

        if anything is None:
            return Summary(success=True)
        else:
            return self.checker(anything, path=path)


class OptionalKeyChecker(ShapeChecker):
    def __init__(self, checker):
        self.checker = checker

    def verify(self, anything, path=None):
        if not path:
            path = []

        if anything is NO_KEY:
            return Summary(success=True)
        else:
            return self.checker(anything, path=path)


# abbreviations

C = TermChecker
T = TypedChecker
L = LengthChecker
N = NoneChecker
E = EnumChecker

Seq = SequenceChecker
Mpp = MappingChecker
Dct = DictChecker

Opt = OptionalChecker
OpK = OptionalKeyChecker
