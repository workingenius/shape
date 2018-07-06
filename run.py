# -*- coding:utf8 -*-
from __future__ import print_function, unicode_literals

from shape import *


if __name__ == '__main__':

    assert TypedChecker(int).verify(3)

    assert SequenceChecker(TypedChecker(int)).verify([1, 2, 4])

    assert MappingChecker(TypedChecker(str), TypedChecker(int)).verify({'2': 2, '3': 3})

    assert (
        LengthChecker(2) & SequenceChecker(TypedChecker(int))
    ).verify([1, 4])

    assert (
        SequenceChecker(
            DictChecker({
                'number': TypedChecker(int) | TypedChecker(float),
                'int': TypedChecker(int),
                'float': TypedChecker(float)
            })
        )
    ).verify([
        {
            'number': 5,
            'int': 10,
            'float': 10.0
        }, {
            'number': 33.1,
            'int': 2,
            'float': 2.2
        }
    ])

    # 收集错误信息

    right = TermChecker(lambda x: x == 0).verify(0)

    assert right

    wrong = TermChecker(lambda x: x == 0).verify(6)

    assert not wrong

    # assert wrong.path
    assert wrong.error
    print(wrong)
