# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
"""A set of constants and methods to manage permissions and security"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from flask_appbuilder.security.sqla.manager import SecurityManager

class UnionSecurityManager(SecurityManager):
    pass