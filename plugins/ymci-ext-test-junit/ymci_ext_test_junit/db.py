from ymci.ext.db import Table
from sqlalchemy import Column, Integer, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship, backref


class Result(Table):
    __tablename__ = 'ymci_ext_test_junit__result'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'build_id'],
            ['build.project_id', 'build.build_id']),
    )
    project_id = Column(Integer, primary_key=True)
    build_id = Column(Integer, primary_key=True)

    fail = Column(Integer)
    error = Column(Integer)
    skip = Column(Integer)
    total = Column(Integer)

    @property
    def success(self):
        return self.total - self.fail - self.error

    build = relationship('Build', backref=backref('result', uselist=False))


class JUnitConfig(Table):
    __tablename__ = 'ymci_ext_test_junit__junit_config'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
    )
    project_id = Column(Integer, primary_key=True, nullable=False)
    junit_path = Column('junit_path', String)

    columns_list = ['junit_path']

    project = relationship('Project', backref=backref(
        'junit', uselist=False, cascade='all'))
