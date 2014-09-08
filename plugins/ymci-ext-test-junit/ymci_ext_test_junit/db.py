from ymci.ext.db import Table
from sqlalchemy import Column, Integer, ForeignKeyConstraint
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
