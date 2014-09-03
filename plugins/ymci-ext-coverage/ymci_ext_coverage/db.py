from ymci.ext.db import Table
from sqlalchemy import Column, Integer, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref


class Coverage(Table):
    __tablename__ = 'ymci_ext_coverage__coverage'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'build_id'],
            ['build.project_id', 'build.build_id']),
    )
    project_id = Column(Integer, primary_key=True)
    build_id = Column(Integer, primary_key=True)

    cls = Column(Integer)
    missed_cls = Column(Integer)

    branches = Column(Integer)
    missed_branches = Column(Integer)

    files = Column(Integer)
    missed_files = Column(Integer)

    lines = Column(Integer)
    missed_lines = Column(Integer)

    @property
    def cls_rate(self):
        if self.cls:
            return 100 * (1 - self.missed_cls / self.cls)
        else:
            return 100

    @property
    def branch_rate(self):
        if self.branches:
            return 100 * (1 - self.missed_branches / self.branches)
        else:
            return 100

    @property
    def file_rate(self):
        if self.files:
            return 100 * (1 - self.missed_files / self.files)
        else:
            return 100

    @property
    def line_rate(self):
        if self.lines:
            return 100 * (1 - self.missed_lines / self.lines)
        else:
            return 100

    build = relationship('Build', backref=backref('coverage', uselist=False))
