# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import get_flashed_messages
from flask_appbuilder import BaseView, ModelView
from flask_appbuilder.widgets import ListWidget
from flask_babel import get_locale

from union import conf
# from union_master.translation.utils import get_language_pack


FRONTEND_CONF_KEYS = (
    'UNION_WEBSERVER_TIMEOUT',
    'ENABLE_JAVASCRIPT_CONTROLS',
)

class BaseUnionView(BaseView):
    def common_bootsrap_payload(self):
        """Common data always sent to the client"""
        messages = get_flashed_messages(with_categories=True)
        locale = str(get_locale())
        return {
            'flash_messages': messages,
            'conf': {k: conf.get(k) for k in FRONTEND_CONF_KEYS},
            'locale': locale,
            'language_pack': 'en',#get_language_pack(locale)
        }


class UnionListWidget(ListWidget):
    template = 'union_master/fab_overrides/list.html'


class UnionModelView(ModelView):
    page_size = 100
    list_widget = UnionListWidget

class ListWidgetWithCheckboxes(ListWidget):
    """An alternative to list view that renders Boolean

    Works in conjunction with the `checkbox` view."""
    template = 'union_master/fab_overrides/list_with_checkboxes.html'