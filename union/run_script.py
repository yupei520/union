# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
"""Utility functions used across Superset"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import argparse
import subprocess
from union.models.core import Fetch
from union import app, db


parse = argparse.ArgumentParser()
parse.add_argument('-f', '--fetch')
args = parse.parse_args()

fetch_one = db.session.query(Fetch).filter_by(fetch_name=args.fetch).first()
subprocess.Popen(fetch_one.generate_script, shell=False, stdout=subprocess.PIPE)
