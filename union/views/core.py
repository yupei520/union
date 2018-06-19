# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from flask_appbuilder.models.sqla.interface import SQLAInterface

from union import app, appbuilder

import union.models.core as models
from union.views.base import UnionModelView, BaseUnionView


config = app.config


class DatabaseView(UnionModelView):
    datamodel = SQLAInterface(models.Database)
    list_title = ('List Databases')
    show_title = ('Show Database')
    add_title = ('Add Database')
    edit_title = ('Edit Database')

    list_columns = ['database_name', 'creator', 'modified']
    order_columns = ['database_name', 'modified']
    add_columns = ['database_name', 'sqlalchemy_uri']
    edit_columns = add_columns
    show_columns = [
        'tables',
        'database_name',
        'sqlalchemy_uri',
        'created_by',
        'created_on',
        'changed_by',
        'changed_on',
    ]
    base_order = ('changed_on', 'desc')
    label_columns = {
        'database_name': ('Database'),
        'creator': ('Creator'),
        'changed_on_': ('Last Changed'),
        'sqlalchemy_uri': ('SQLAlchemy URI'),
    }
    add_template = 'union/models/database/add.html'
    edit_template = 'union/models/database/edit.html'


appbuilder.add_view(DatabaseView, 'Databases', label=('Databases'),
                    icon='fa-database', category='Sources', category_label=('Sources'),
                    category_icon='fa-database')