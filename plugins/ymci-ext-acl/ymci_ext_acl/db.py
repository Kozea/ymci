from ymci.ext.db import Table
from sqlalchemy import (
    Column, Integer, ForeignKeyConstraint, String, UniqueConstraint)
from sqlalchemy.orm import relationship, backref


class Set(Table):
    __tablename__ = 'ymci_ext_acl_set'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['ymci_ext_acl_group.group_id']),
        ForeignKeyConstraint(['login'], ['user.login']))

    group_id = Column(Integer, primary_key=True)
    login = Column(String, primary_key=True)

    group = relationship('Group', backref='sets')
    user = relationship('User', backref='sets')


class Group(Table):
    __tablename__ = 'ymci_ext_acl_group'
    __table_args__ = (UniqueConstraint('name'),)

    group_id = Column(Integer, primary_key=True)
    name = Column(String)

    user = relationship(
        "User", secondary='ymci_ext_acl_set',
        backref=backref('groups', cascade='all'))


class AclLevel(Table):
    __tablename__ = 'ymci_ext_acl_level'
    __table_args__ = (UniqueConstraint('level_id', 'name'),)

    level_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class UserLevel(Table):
    __tablename__ = 'ymci_ext_acl_user_level'
    __table_args__ = (
        ForeignKeyConstraint(['login'], ['user.login']),
        ForeignKeyConstraint(['level_id'], ['ymci_ext_acl_level.level_id']))

    login = Column(String, primary_key=True)
    level_id = Column(Integer, primary_key=True)

    user = relationship('User', backref=backref('level', uselist=False))
    acl_level = relationship('AclLevel', backref='user_level')


class Acl(Table):
    __tablename__ = "ymci_ext_acl"
    __table_args__ = (
        ForeignKeyConstraint(['login'], ['user.login']),
        ForeignKeyConstraint(['group_id'], ['ymci_ext_acl_group.group_id']),
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
        ForeignKeyConstraint(['level_id'], ['ymci_ext_acl_level.level_id']),
        UniqueConstraint('login', 'level_id', 'route'),
        UniqueConstraint('group_id', 'route'))

    acl_id = Column(Integer, primary_key=True)
    login = Column(String)
    group_id = Column(Integer)
    level_id = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=True)
    route = Column(String, nullable=True)

    project = relationship(
        'Project', backref=backref('acls', cascade='all, delete-orphan'))
    level = relationship('AclLevel', backref='acls', uselist=False)
    user = relationship('User', backref='acls')
    group = relationship('Group', backref='acls')
