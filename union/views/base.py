# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import traceback
import logging
import functools

from flask import get_flashed_messages, Response
from flask_appbuilder import ModelView, BaseView
from flask_appbuilder.widgets import ListWidget
from flask_babel import get_locale

from union import conf, utils
from union.translations.utils import get_language_pack


FRONTEND_CONF_KEYS = (
    'UNION_WEBSERVER_TIMEOUT',
    'ENABLE_JAVASCRIPT_CONTROLS',
)

def json_error_response(msg=None, status=500, stacktrace=None, payload=None, link=None):
    if not payload:
        payload = {'error': str(msg)}
        if stacktrace:
            payload['stacktrace'] = stacktrace
        if link:
            payload['link'] = link
    return Response(json.dumps(payload, default=utils.json_iso_dttm_ser),
                    status=status, mimetype='application/json')

class BaseUnionView(BaseView):
    def common_bootsrap_payload(self):
        """Common data always sent to the client"""
        messages = get_flashed_messages(with_categories=True)
        locale = str(get_locale())
        return {
            'flash_messages': messages,
            'conf': {k: conf.get(k) for k in FRONTEND_CONF_KEYS},
            'locale': locale,
            'language_pack': get_language_pack(locale),
        }


class UnionListWidget(ListWidget):
    template = 'union/fab_overrides/list.html'


class UnionModelView(ModelView):
    page_size = 100
    list_widget = UnionListWidget

class ListWidgetWithCheckboxes(ListWidget):
    """An alternative to list view that renders Boolean

    Works in conjunction with the `checkbox` view."""
    template = 'union.py/fab_overrides/list_with_checkboxes.html'

def get_error_msg():
    if conf.get('SHOW_STACKTRACE'):
        error_msg = traceback.format_exc()
    else:
        error_msg = 'FATAL ERROR \n'
        error_msg += (
            'Stacktrace is hidden. Change the SHOW_STACKTRACE '
            'configuration setting to enable it')
    return error_msg

def api(f):
    """
    A decorator to label an endpoint as an API. Catches uncaught exceptions and
    return the response in the JSON format
    """
    def wraps(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            logging.exception(e)
            return json_error_response(get_error_msg())

    return functools.update_wrapper(wraps, f)