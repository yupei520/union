# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
"""Package's main module!"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import json
import os

from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

from union import config, utils
from union.security import UnionSecurityManager


"""
 Logging configuration
"""

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

APP_DIR = os.path.dirname(__file__)
CONFIG_MODULE = os.environ.get('UNION_CONFIG', 'union.config')

if not os.path.exists(config.DATA_DIR):
    os.makedirs(config.DATA_DIR)


app = Flask(__name__)
app.config.from_object(CONFIG_MODULE)
conf = app.config


"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

db = SQLA(app)

tables_cache = utils.setup_cache(app, conf.get('TABLE_NAMES_CACHE_CONFIG'))

custom_sm = app.config.get('CUSTOM_SECURITY_MANAGER') or UnionSecurityManager

appbuilder = AppBuilder(
    app,
    db.session,
    security_manager_class=custom_sm,
)

security_manager = appbuilder.sm

from union import views

