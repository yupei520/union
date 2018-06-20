# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
"""Utility functions used across Superset"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from datetime import date, datetime, time, timedelta
import decimal
import uuid
import functools
import numpy
import pandas as pd


from flask_caching import Cache

def base_json_conv(obj):

    if isinstance(obj, numpy.int64):
        return int(obj)
    elif isinstance(obj, numpy.bool_):
        return bool(obj)
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, timedelta):
        return str(obj)

def json_iso_dttm_ser(obj, pessimistic=False):
    """
    json serializer that deals with dates
    >>> dttm = datetime(1970, 1, 1)
    >>> json.dumps({'dttm': dttm}, default=json_iso_dttm_ser)
    '{"dttm": "1970-01-01T00:00:00"}'
    """
    val = base_json_conv(obj)
    if val is not None:
        return val
    if isinstance(obj, (datetime, date, time, pd.Timestamp)):
        obj = obj.isoformat()
    else:
        if pessimistic:
            return 'Unserializable [{}]'.format(type(obj))
        else:
            raise TypeError(
                'Unserializable object {} of type {}'.format(obj, type(obj))
            )
    return obj


class _memoized(object):  # noqa
    """Decorator that caches a function's return value each time it is called
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    Define ``watch`` as a tuple of attribute names if this Decorator
    should account for instance variable changes.
    """

    def __init__(self, func, watch=()):
        self.func = func
        self.cache = {}
        self.is_method = False
        self.watch = watch

    def __call__(self, *args, **kwargs):
        key = [args, frozenset(kwargs.items())]
        if self.is_method:
            key.append(tuple([getattr(args[0], v, None) for v in self.watch]))
        key = tuple(key)
        if key in self.cache:
            return self.cache[key]
        try:
            value = self.func(*args, **kwargs)
            self.cache[key] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        if not self.is_method:
            self.is_method = True
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def memoized(func=None, watch=None):
    if func:
        return _memoized(func)
    else:
        def wrapper(f):
            return _memoized(f, watch)
        return wrapper


def setup_cache(app, cache_config):
    """Setup the flask-cache on a flask app"""
    if cache_config and cache_config.get('CACHE_TYPE') != 'null':
        return Cache(app, config=cache_config)

class QueryStatus(object):
    """Enum-type class for query statuses"""

    STOPPED = 'stopped'
    FAILED = 'failed'
    PENDING = 'pending'
    RUNNING = 'running'
    SCHEDULED = 'scheduled'
    SUCCESS = 'success'
    TIMED_OUT = 'timed_out'