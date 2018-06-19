# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from past.builtins import basestring
from sqlalchemy import (
    and_, Boolean, Column, Integer, String, Text,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import foreign, relationship

from union.models.helpers import AuditMixinNullable

class BaseDatasource(AuditMixinNullable):
    """A common interface to objects that are queryable
    (tables and datasources)"""

    __tablename__ = None
    

