# -*- coding:utf8 -*-

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
            ObjectChecker({
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
