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


MANIFEST_FILE = APP_DIR + '/static/assets/dist/manifest.json'
manifest = {}


def parse_manifest_json():
    global manifest
    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except Exception:
        pass


def get_manifest_file(filename):
    if app.debug:
        parse_manifest_json()
    return '/static/assets/dist/' + manifest.get(filename, '')


parse_manifest_json()


@app.context_processor
def get_js_manifest():
    return dict(js_manifest=get_manifest_file)


db = SQLA(app)

tables_cache = utils.setup_cache(app, conf.get('TABLE_NAMES_CACHE_CONFIG'))

custom_sm = app.config.get('CUSTOM_SECURITY_MANAGER') or UnionSecurityManager

appbuilder = AppBuilder(
    app,
    db.session,
    base_template='union/base.html',
    security_manager_class=custom_sm,
)

security_manager = appbuilder.sm

from union import views

