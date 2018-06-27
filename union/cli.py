# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
"""Utility functions used across Superset"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask_migrate import MigrateCommand
from flask_script import Manager

import argparse
import subprocess
from union.models.core import Fetch
from union import app, db

manager = Manager(app)
manager.add_command('db', MigrateCommand)



@manager.option('-f', '--fetch')
def run_fetch(fetch):
    fetch_one = db.session.query(Fetch).filter_by(fetch_name=fetch).first()
    subprocess.Popen(fetch_one.generate_script.split('\\\n'), shell=False, stdout=subprocess.PIPE)

