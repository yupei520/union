# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import logging
import json

from flask import (flash, g, Markup, request, Response)
from flask_appbuilder import expose

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access
from union import app, appbuilder, db
import union.models.core as models
from .base import (api, UnionModelView, BaseUnionView, json_error_response)


config = app.config


def json_success(json_msg, status=200):
    return Response(json_msg, status=status, mimetype='application/json')

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


class Union(BaseUnionView):
    """The base views for Union!"""

    @api
    @expose('/testconn', methods=['POST', 'GET'])
    def testconn(self):
        """Tests a sqla connection"""
        try:
            username = g.user.username if g.user is not None else None
            uri = request.json.get('uri')
            db_name = request.json.get('name')
            impersonate_user = request.json.get('impersonate_user')
            database = None
            if db_name:
                database = (
                    db.session
                    .query(models.Database)
                    .filter_by(database_name=db_name)
                    .first()
                )
                if database and uri == database.safe_sqlalchemy_uri():
                    uri = database.sqlalchemy_uri_decrypted

            configuration = {}

            if database and uri:
                url = make_url(uri)
                db_engine = models.Database.get_db_engine_spec_for_backend(
                    url.get_backend_name())
                db_engine.patch()

                masked_url = database.get_password_masked_url_from_uri(uri)
                logging.info('Union.testconn(). Masked URL:{0}'.format(masked_url))

                configuration.update(db_engine.get_configuration_for_impersonation(
                    uri, impersonate_user, username
                ),)

            connect_args = (request.json
                            .get('engine_params', {})
                            .get('connect_args',{}))

            if configuration:
                connect_args['configuration'] = configuration

            engine = create_engine(uri, connect_args=connect_args)
            engine.connect()
            return json_success(json.dumps(engine.table_names(), indent=4))
        except Exception as e:
            logging.exception(e)
            return json_error_response((
                'Connection failed!\n\n'
                'The error message returned was:\n{}').format(e)
            )

appbuilder.add_view_no_menu(Union)