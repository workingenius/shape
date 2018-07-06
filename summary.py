# -*- coding:utf8 -*-

from __future__ import unicode_literals


try:
    # noinspection PyUnresolvedReferences
    from typing import List
except ImportError:
    pass


class Summary(object):
    def __init__(self, success, path=None, error=''):
        if not path:
            path = []

        self.success = success  # type: bool
        self.path = path  # type: List[str]
        self.error = error  # type: str

    def __str__(self):
        if self.success:
            return '<shape good>'
        else:
            return '<shape bad: path: {0}, error: {1}>'.format('/' + '/'.join(self.path), self.error)

    def __bool__(self):
        return self.success
