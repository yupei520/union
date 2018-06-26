# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import logging
import json
import shutil

from flask import (flash, g, Markup, request, Response)
from flask_appbuilder import expose

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _

from union import app, appbuilder, db, utils
import union.models.core as models
from .base import (api, UnionModelView, BaseUnionView, json_error_response)


config = app.config


def json_success(json_msg, status=200):
    return Response(json_msg, status=status, mimetype='application/json')


def join_file(dir_name, file_name, suffix):
    return os.path.join(dir_name, file_name+suffix)


def create_fetch_file(obj):
    file_name = obj.hive_table
    dir_path = os.path.join(config.get('CREATE_JOB_DIR'), obj.file_dir.dir_name, obj.hive_database, file_name)
    if os.path.exists(dir_path) is False:
        os.makedirs(dir_path)
    with open(join_file(dir_path, file_name, '.py'), 'w') as py_file:
        py_content = """if __name__ == '__main__':
    pass"""
        py_file.write(py_content)


def delete_fetch_file(obj):
    dir_path = os.path.join(config.CREATE_JOB_DIR, obj.file_dir.dir_name, obj.hive_database, obj.hive_table)
    shutil.rmtree(dir_path)


class DatabaseView(UnionModelView):
    datamodel = SQLAInterface(models.Database)

    list_title = _('List Databases')
    show_title = _('Show Database')
    add_title = _('Add Database')
    edit_title = _('Edit Database')

    list_columns = ['database_name', 'backend', 'creator', 'modified']
    order_columns = ['database_name', 'modified']
    add_columns = ['database_name', 'sqlalchemy_uri']
    edit_columns = add_columns
    show_columns = [
        'tables',
        'database_name',
        'sqlalchemy_uri',
        'backend',
        'creator'
        'created_by',
        'created_on',
        'changed_by',
        'changed_on',
    ]
    search_columns = ['database_name']
    base_order = ('changed_on', 'desc')

    add_template = 'union/models/database/add.html'
    edit_template = 'union/models/database/edit.html'
    description_columns = {
        'sqlalchemy_uri': utils.markdown(
            'Refer to the '
            '[SqlAlchemy docs]'
            '(http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#'
            'database-urls) '
            'for more information on how to structure your URI.', True)
    }
    label_columns = {
        'database_name': _('Database'),
        'backend': _('Backend'),
        'creator': _('Creator'),
        'modified': _('Modified'),
        'changed_on_': _('Last Changed'),
        'sqlalchemy_uri': _('SQLAlchemy URI'),
        'tables': _('Tables'),
        'created_by': _('Created By'),
        'created_on': _('Created On'),
        'changed_by': _('Changed By'),
        'changed_on': _('Changed On')
    }

    def pre_add(self, db):
        db.set_sqlalchemy_uri(db.sqlalchemy_uri)

    def pre_update(self, db):
        self.pre_add(db)


appbuilder.add_view(DatabaseView, 'Databases', label=__('Databases'),
                    icon='fa-database', category='Extract', category_label=__('Extract'),
                    category_icon='fa-tachometer')


class FetchView(UnionModelView):
    datamodel = SQLAInterface(models.Fetch)

    list_title = _('List Fetches')
    show_title = _('Show Fetch')
    add_title = _('Add Fetch')
    edit_title = _('Edit Fetch')

    list_columns = ['fetch_name', 'database', 'table_name', 'creator', 'modified']
    add_columns = ['database', 'table_name', 'hive_database', 'hive_table', 'query', 'split_by', 'm', 'target_dir',
                   'file_dir', 'partition_key', 'default_fetch_config', 'hive_overwrite', 'direct',
                   'delete_targer_dir', 'outdir', 'extra_config']
    edit_columns = add_columns
    show_columns = ['fetch_name', 'database', 'table_name', 'generate_script']
    search_columns = ['database', 'table_name']
    description_columns = {
        'query': _('Sqoop Execute SQL'),
        'split_by': _('Split of the column'),
        'm': _('Hive Map Number'),
        'target_dir': _('Target path'),
        'file_dir': _('Job directory'),
        'partition_key': _('Hive Partition Key'),
        'hive_overwrite': _('Overwrite the data'),
        'direct': _('Use the direct import fast path'),
        'delete_targer_dir': _('Delete target path'),
        'outdir': _('Hive output directory'),
        'extra_config': _('Extra hive configuration')
    }
    label_columns = {
        'fetch_name': _('Fetch'),
        'database': _('DataBase'),
        'table_name': _('Table Name'),
        'creator': _('Creator'),
        'modified': _('Modified'),
        'hive_database': _('Hive Database'),
        'hive_table': _('Hive Table'),
        'query': _('Query'),
        'split_by': _('Split By'),
        'm': _('M'),
        'target_dir': _('Target Dir'),
        'file_dir': _('File Dir'),
        'partition_key': _('Partition Key'),
        'default_fetch_config': _('Default Fetch Config'),
        'hive_overwrite': _('Hive Overwrite'),
        'direct': _('Direct'),
        'delete_targer_dir': _('Delete Targer Dir'),
        'outdir': _('Outdir'),
        'extra_config': _('Extra Config'),
        'generate_script': _('Generate Script')
    }

    def pre_add(self, obj):
        create_fetch_file(obj)

    def pre_delete(self, obj):
        # delete_fetch_file(obj)
        pass


appbuilder.add_view(FetchView, 'Fetches', label=__('Fetches'), icon='fa-flag',
                    category='Extract', category_label=__('Extract'),
                    category_icon='fa-tachometer'
                    )


class PartitionValueView(UnionModelView):
    datamodel = SQLAInterface(models.PartitionValue)

    list_title = _('List PartitionValues')
    show_title = _('Show PartitionValue')
    add_title = _('Add PartitionValue')
    edit_title = _('Edit PartitionValue')

    edit_columns = ['par_val_name', 'format_date', 'forward_days', 'slice_format']
    list_columns = edit_columns + ['creator', 'modified']
    show_columns = edit_columns + ['real_value']
    add_columns = edit_columns
    description_columns ={
        'format_date': _('Time format Such as %Y-%m-%d'),
        'forward_days': _('Days before the date'),
        'slice_format': _('Slice format Such as 2:4')
    }
    label_columns = {
        'par_val_name': _('Partition Value Name'),
        'format_date': _('Format Date'),
        'forward_days': _('Forward Days'),
        'slice_format': _('Slice Format'),
        'creator': _('Creator'),
        'modified': _('Modified'),
        'real_value': _('Real Value')
    }


appbuilder.add_view(PartitionValueView, 'PartitionValues', label=__('PartitionValues'), icon='fa-paper-plane',
                    category='Extract', category_label=__('Extract'),
                    category_icon='fa-tachometer'
                    )


class PartitionKeyView(UnionModelView):
    datamodel = SQLAInterface(models.PartitionKey)

    list_title = _('List PartitionKeys')
    show_title = _('Show PartitionKey')
    add_title = _('Add PartitionKey')
    edit_title = _('Edit PartitionKey')

    show_columns = ['partition_field', 'partition_value']
    list_columns = show_columns + ['creator', 'modified']
    edit_columns = show_columns
    add_columns = show_columns
    search_columns = ['partition_field']
    label_columns = {
        'partition_field': _('Partition Field'),
        'partition_value': _('Partition Value'),
        'creator': _('Creator'),
        'modified': _('Modified')
    }


appbuilder.add_view(PartitionKeyView, 'PartitionKeys', label=__('PartitionKeys'), icon='fa-podcast',
                    category='Extract', category_label=__('Extract'),
                    category_icon='fa-tachometer'
                    )


class FileDirView(UnionModelView):
    datamodel = SQLAInterface(models.FileDir)

    list_title = _('List FileDirs')
    show_title = _('Show FileDir')
    add_title = _('Add FileDir')
    edit_title = _('Edit FileDir')

    list_columns = ['dir_name', 'creator', 'modified']
    show_columns = ['dir_name']
    edit_columns = show_columns
    add_columns = show_columns
    search_columns = ['dir_name']
    label_columns = {
        'dir_name': _('Dir Name'),
        'creator': _('Creator'),
        'modified': _('Modified')
    }


appbuilder.add_view(FileDirView, 'FileDirs', label=__('FileDirs'), icon='fa-file',
                    category='Extract', category_label=__('Extract'),
                    category_icon='fa-tachometer'
                    )


class DefaultFetchConfigView(UnionModelView):
    datamodel = SQLAInterface(models.DefaultFetchConfig)

    list_title = _('List DefaultFetchConfigs')
    show_title = _('Show DefaultFetchConfig')
    add_title = _('Add DefaultFetchConfig')
    edit_columns = _('Edit DefaultFetchConfig')

    list_columns = ['def_fet_name', 'fields_terminated_by', 'null_string', 'hive_delims_replacement', 'null_non_string']
    show_columns = list_columns + ['creator', 'modified']
    edit_columns = list_columns
    add_columns = list_columns
    search_columns = ['def_fet_name']
    description_columns = {
        'fields_terminated_by': _('The separator between fields'),
        'null_string': _('Null value of character column'),
        'null_non_string': _('Null values for non-character columns')
    }
    label_columns = {
        'def_fet_name': _('Default Fetch Name'),
        'fields_terminated_by': _('Fields Terminated By'),
        'null_string': _('Null String'),
        'hive_delims_replacement': _('Hive Delims Replacement'),
        'null_non_string': _('Null Non String'),
        'creator': _('Creator'),
        'modified': _('Modified')
    }


appbuilder.add_view(DefaultFetchConfigView, 'DefaultFetchConfigs', label=__('DefaultFetchConfigs'),
                    icon='fa-mortar-board ', category='Extract', category_label=__('Extract'),
                    category_icon='fa-tachometer'
                    )


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
                            .get('connect_args', {}))

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