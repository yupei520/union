# -*- coding: utf-8 -*-
"""A collection of ORM sqlalchemy models for Union"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from copy import copy, deepcopy
import sqlalchemy as sqla
from flask_appbuilder import Model
from union.models.helpers import AuditMixinNullable


from sqlalchemy import (
    Boolean, Column, create_engine, DateTime, ForeignKey, Integer,
    MetaData, String, Table, Text,
)

from sqlalchemy.engine import url
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import relationship, subqueryload
from sqlalchemy.orm.session import make_transient
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_utils import EncryptedType

from union import app, db_engine_specs, security_manager, utils

config = app.config
custom_password_store = config.get('SQLALCHEMY_CUSTOM_PASSWORD_STORE')
metadata = Model.metadata  # pylint: disable=no-member

PASSWORD_MASK = 'X' * 10

class Database(Model, AuditMixinNullable):

    """An ORM object that stores Database related information"""
    __tablename__ = 'dbs'
    type = 'table'
    __table_args__ = (UniqueConstraint('database_name'),)

    id = Column(Integer, primary_key=True)
    verbose_name = Column(String(250), unique=True)
    database_name = Column(String(250), unique=True)
    sqlalchemy_uri = Column(String(1024))
    password = Column(EncryptedType(String(1024), config.get('SECRET_KEY')))

    export_fields = ('database_name', 'sqlalchemy_uri')
    export_children = ['tables']

    def __repr__(self):
        return self.verbose_name if self.verbose_name else self.database_name

    @property
    def name(self):
        return self.verbose_name if self.verbose_name else self.database_name

    @property
    def backend(self):
        url = make_url(self.sqlalchemy_uri_decrypted)
        return url.get_backend_name()

    @classmethod
    def get_password_masked_url_from_uri(cls, uri):
        url = make_url(uri)
        return cls.get_password_masked_url(url)

    @classmethod
    def get_password_masked_url(cls, url):
        url_copy = deepcopy(url)
        if url_copy.password is not None and url_copy.password != PASSWORD_MASK:
            url_copy.password = PASSWORD_MASK
        return url_copy

    def set_sqlalchemy_uri(self, uri):
        conn = sqla.engine.url.make_url(uri.strip())
        if conn.password != PASSWORD_MASK and not custom_password_store:
            # do not over-write the password with the password mask
            self.password = conn.password
        conn.password = PASSWORD_MASK if conn.password else None
        self.sqlalchemy_uri = str(conn)  # hides the password

    def safe_sqlalchemy_uri(self):
        return self.sqlalchemy_uri

    @property
    def sqlalchemy_uri_decrypted(self):
        conn = sqla.engine.url.make_url(self.sqlalchemy_uri)
        if custom_password_store:
            conn.password = custom_password_store(conn)
        else:
            conn.password = self.password
        return str(conn)

    @utils.memoized(
        watch=('impersonate_user', 'sqlalchemy_uri_decrypted', 'extra'))
    def get_sqla_engine(self, schema=None, nullpool=True, user_name=None):
        extra = self.get_extra()
        url = make_url(self.sqlalchemy_uri_decrypted)
        url = self.db_engine_spec.adjust_database_uri(url, schema)
        effective_username = self.get_effective_user(url, user_name)
        # If using MySQL or Presto for example, will set url.username
        # If using Hive, will not do anything yet since that relies on a
        # configuration parameter instead.
        self.db_engine_spec.modify_url_for_impersonation(
            url,
            self.impersonate_user,
            effective_username)

        masked_url = self.get_password_masked_url(url)
        logging.info('Database.get_sqla_engine(). Masked URL: {0}'.format(masked_url))

        params = extra.get('engine_params', {})
        if nullpool:
            params['poolclass'] = NullPool

        # If using Hive, this will set hive.server2.proxy.user=$effective_username
        configuration = {}
        configuration.update(
            self.db_engine_spec.get_configuration_for_impersonation(
                str(url),
                self.impersonate_user,
                effective_username))
        if configuration:
            params['connect_args'] = {'configuration': configuration}

        DB_CONNECTION_MUTATOR = config.get('DB_CONNECTION_MUTATOR')
        if DB_CONNECTION_MUTATOR:
            url, params = DB_CONNECTION_MUTATOR(
                url, params, effective_username, security_manager)
        return create_engine(url, **params)

    @property
    def db_engine_spec(self):
        return db_engine_specs.engines.get(
            self.backend, db_engine_specs.BaseEngineSpec)

    @classmethod
    def get_db_engine_spec_for_backend(cls, backend):
        return db_engine_specs.engines.get(backend, db_engine_specs.BaseEngineSpec)