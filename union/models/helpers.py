# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from datetime import datetime
import humanize

from flask import escape, Markup
from flask_appbuilder.models.decorators import renders
import sqlalchemy as sa
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy.ext.declarative import declared_attr


class AuditMixinNullable(AuditMixin):
    """Altering the AuditMixin to use nullable fields

    Allows creating objects programmatically outside of CRUD
    """

    created_on = sa.Column(sa.DateTime, default=datetime.now, nullable=True)
    changed_on = sa.Column(
        sa.DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)

    @declared_attr
    def created_by_fk(self):
        return sa.Column(
            sa.Integer, sa.ForeignKey('ab_user.id'),
            default=self.get_user_id, nullable=True)

    @declared_attr
    def changed_by_fk(self):
        return sa.Column(
            sa.Integer, sa.ForeignKey('ab_user.id'),
            default=self.get_user_id, onupdate=self.get_user_id, nullable=True)

    def _user_link(self, user):
        if not user:
            return ''
        url = '/union_master/profile/{}/'.format(user.username)
        return Markup('<a href="{}">{}</a>'.format(url, escape(user) or ''))

    def changed_by_name(self):
        if self.created_by:
            return escape('{}'.format(self.created_by))
        return ''

    @renders('created_by')
    def creator(self):
        return self._user_link(self.created_by)

    @property
    def changed_by_(self):
        return self._user_link(self.created_by)

    @renders('changed_on')
    def chang_on_(self):
        return Markup(
            '<span class="no-wrap">{}</span>'.format(self.created_on))

    @renders('changed_on')
    def modified(self):
        s = humanize.naturaltime(datetime.now() - self.created_on)
        return Markup('<span class="no-wrap">{}</span>'.format(s))

    @property
    def icons(self):
        return """
        <a href="{self.datasource_edit_url}"
            data-toggle='tooltip'
            title="{self.datasource}">
            <i class="fa fa-database"></i>
        </a>
        """.format(**locals())



