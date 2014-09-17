from ymci.ext.db import Table
from sqlalchemy import (
    Column, Integer, ForeignKeyConstraint, String, UniqueConstraint)
from sqlalchemy.orm import relationship, backref


class AclLevel(Table):
    __tablename__ = 'ymci_ext_acl_level'

    level_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Acl(Table):
    __tablename__ = "ymci_ext_acl"
    __table_args__ = (
        ForeignKeyConstraint(['login'], ['ymci_user.login']),
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
        ForeignKeyConstraint(['level_id'], ['ymci_ext_acl_level.level_id']),
        UniqueConstraint('login', 'level_id', 'route'))

    acl_id = Column(Integer, primary_key=True)
    login = Column(String)
    level_id = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=True)
    route = Column(String, nullable=True)

    project = relationship(
        'Project', backref=backref('acls', cascade='all, delete-orphan'))
    level = relationship('AclLevel', backref='acls', uselist=False)
    user = relationship('User', backref='acls')
