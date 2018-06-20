# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class UnionException(Exception):
    status = 500

class UnionTimeoutException(UnionException):
    pass


class UnionSecurityException(UnionException):
    pass


class MetricPermException(UnionException):
    pass


class NoDataException(UnionException):
    status = 400


class UnionTemplateException(UnionException):
    pass