# -*- coding:utf8 -*-

from __future__ import print_function, unicode_literals

from sys import version_info
from unittest import TestCase

from shape import *

PY2 = (version_info.major == 2)
PY3 = (version_info.major == 3)

if PY2:
    byte = str
    str = unicode


class TestTermChecker(TestCase):
    def test_error_path(self):
        """检查报错产生的位置"""
        summ = TermChecker(lambda x: x == 6).verify(4)
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])


class TestTypedChecker(TestCase):
    def test_positive_case(self):
        self.assertTrue(TypedChecker(int).verify(3))

    def test_negative_case(self):
        summ = TypedChecker(int).verify(8.9)
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])


class TestLengthChecker(TestCase):
    def test_error_path(self):
        summ = LengthChecker(1).verify([])
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])

    def test_bad_thing_error(self):
        summ = LengthChecker(1).verify(object())
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])


class TestAndChecker(TestCase):
    def setUp(self):
        self.checker1 = TypedChecker(int)
        self.checker2 = TermChecker(lambda x: x > 0)

    def test_true_true(self):
        summ = (self.checker1 & self.checker2).verify(1)
        self.assertTrue(summ)

    def test_true_false(self):
        summ = (self.checker1 & self.checker2).verify(-1)
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])

    def test_false_true(self):
        summ = (self.checker2 & self.checker1).verify(-1)
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])

    def test_false_false(self):
        summ = (self.checker2 & self.checker1).verify(-1.5)
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])


class TestOrChecker(TestCase):
    def setUp(self):
        self.checker1 = TypedChecker(int)
        self.checker2 = TermChecker(lambda x: x > 0)

    def test_true_true(self):
        summ = (self.checker1 | self.checker2).verify(1)
        self.assertTrue(summ)

    def test_true_false(self):
        summ = (self.checker1 | self.checker2).verify(-1)
        self.assertTrue(summ)

    def test_false_true(self):
        summ = (self.checker2 | self.checker1).verify(-1)
        self.assertTrue(summ)

    def test_false_false(self):
        summ = (self.checker2 | self.checker1).verify(-1.5)
        self.assertFalse(summ)
        self.assertEqual(summ.path, [])


class TestSequenceChecker(TestCase):
    def setUp(self):
        self.checker = SequenceChecker(TypedChecker(int))

    def test_happy_case(self):
        summ = self.checker.verify([1, 2, 3])
        self.assertTrue(summ)

    def test_bad_case(self):
        """并非每个元素都满足子 checker 时，验证不通过"""
        summ = self.checker.verify([1, 2, 3.4])
        self.assertFalse(summ)

    def test_bad_case_with_path(self):
        """并非每个元素都满足子 checker 时，错误路径上要反映 sequence index"""
        summ = self.checker.verify([1, 2, 3.4])
        self.assertEqual(summ.path, [2])

    def test_bad_interface(self):
        """验证的对象不是序列时，验证不通过"""
        summ = self.checker.verify(object())
        self.assertFalse(summ)

    def test_bad_interface_with_path(self):
        """验证的对象不是序列时，出错路径不带 sequence index"""
        summ = self.checker.verify(object())
        self.assertEqual(summ.path, [])


class TestMappingChecker(TestCase):
    def setUp(self):
        self.checker = MappingChecker(
            TermChecker(lambda x: x.startswith('valid_')),
            TypedChecker(int)
        )

    def test_happy_case(self):
        summ = self.checker.verify({
            'valid_k1': 1,
            'valid_k2': 2,
            'valid_k3': 3
        })
        self.assertTrue(summ)

    def test_bad_interface(self):
        """验证的对象不是字典时，验证不通过"""
        summ = self.checker.verify(object())
        self.assertFalse(summ)

    def test_bad_interface_with_path(self):
        """验证的对象不是字典时，出错路径不带 dict key"""
        summ = self.checker.verify(object())
        self.assertEqual(summ.path, [])

    def test_bad_key(self):
        """字典中有不正确的 key 时，验证不通过"""
        summ = self.checker.verify({
            'valid_k1': 1,
            'valid_k2': 2,
            'invalid_k3': 3
        })
        self.assertFalse(summ)

    def test_bad_key_with_path(self):
        """字典中有不正确的 key 时，错误路径中带有 dict key"""
        summ = self.checker.verify({
            'valid_k1': 1,
            'valid_k2': 2,
            'invalid_k3': 3
        })
        self.assertEqual(summ.path, ['invalid_k3'])


class TestDictChecker(TestCase):
    def setUp(self):
        self.checker = DictChecker({
            'key': TypedChecker(int)
        }, allow_extra=False)

        self.checker_extra = DictChecker({
            'key': TypedChecker(int)
        }, allow_extra=True)

    def test_bad_interface(self):
        """验证的对象不是字典时，验证不通过"""
        summ = self.checker.verify(object())
        self.assertFalse(summ)

    def test_bad_interface_with_path(self):
        """验证的对象不是字典时，错误路径中带有 dict key"""
        summ = self.checker.verify(object())
        self.assertEqual(summ.path, [])

    def test_negative_case(self):
        summ = self.checker.verify({'key': 1.1})
        self.assertFalse(summ)

    def test_negative_case_with_path(self):
        summ = self.checker.verify({'key': 1.1})
        self.assertEqual(summ.path, ['key'])

    def test_miss_key(self):
        summ = self.checker.verify({})
        self.assertFalse(summ)

    def test_extra_key_allowed(self):
        summ = self.checker.verify({
            'key': 1,
            'extra_key': None
        })
        self.assertFalse(summ)

    def test_extra_key_disallowed(self):
        summ = self.checker_extra.verify({
            'key': 1,
            'extra_key': None
        })
        self.assertTrue(summ)


class TestNoneChecker(TestCase):
    def test_positive_case(self):
        summ = NoneChecker().verify(None)
        self.assertTrue(summ)

    def test_negative_case(self):
        summ = NoneChecker().verify('None')
        self.assertFalse(summ)


class TestOptionalChecker(TestCase):
    def test_positive_case(self):
        summ = OptionalChecker(TypedChecker(int)).verify(None)
        self.assertTrue(summ)


class TestOptionalKeyChecker(TestCase):
    def test_positive_case(self):
        summ = DictChecker({
            'key': OptionalKeyChecker(TypedChecker(int))
        }).verify({
            # 'key': nothing
        })
        self.assertTrue(summ)


class OverallTest(TestCase):

    Subject = T(str) & E(['sport', 'maths', 'literary'])

    Question = Mpp(
        T(str) & C(lambda x: x.startswith('q')),  # q for "question"
        Dct({
            'question': T(str),
            'options': Seq(T(str)),
            'answer': OpK(T(str))
        })
    )

    quiz_data_checker = Dct({
        'success': T(bool),
        'error': T(str)
    }) | Dct({
        'success': T(bool),
        'data': Mpp(Subject, Question)
    })

    def test_case_1(self):
        summ = self.quiz_data_checker.verify({
            'success': True,
            'error': 'should not be here',
            'data': {}
        })
        print(summ)
        self.assertFalse(summ)

    def test_case_2(self):
        summ = self.quiz_data_checker.verify({
            'success': True,
            'data': {
                "sport": {
                    "q1": {
                        "question": "Which one is correct team name in NBA?",
                        "options": [
                            "New York Bulls",
                            "Los Angeles Kings",
                            "Golden State Warriros",
                            "Huston Rocket"
                        ],
                        "answer": "Huston Rocket"
                    }
                },
                "maths": {
                    "q1": {
                        "question": "5 + 7 = ?",
                        "options": [
                            "10",
                            "11",
                            "12",
                            "13"
                        ],
                        "answer": "12"
                    },
                    "q2": {
                        "question": "12 - 8 = ?",
                        "options": [
                            "1",
                            "2",
                            "3",
                            "4"
                        ],
                        "answer": "4"
                    }
                }
            }
        })

        print(summ)
        self.assertTrue(summ)
