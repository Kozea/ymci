from ymci.ext.db import Table
from sqlalchemy import Column, Integer, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case


class Coverage(Table):
    __tablename__ = 'ymci_ext_coverage__coverage'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'build_id'],
            ['build.project_id', 'build.build_id']),
    )
    project_id = Column(Integer, primary_key=True)
    build_id = Column(Integer, primary_key=True)
    filename = Column(String, primary_key=True, server_default='coverage.xml')

    cls = Column(Integer)
    missed_cls = Column(Integer)

    branches = Column(Integer)
    missed_branches = Column(Integer)

    files = Column(Integer)
    missed_files = Column(Integer)

    lines = Column(Integer)
    missed_lines = Column(Integer)

    @hybrid_property
    def cls_rate(self):
        return self.cls and 100 * (1 - self.missed_cls / self.cls)

    @cls_rate.expression
    def cls_rate(cls):
        return case([(cls.cls != 0,
                      100 * (1 - cls.missed_cls / cls.cls))],
                    else_=0)

    @hybrid_property
    def branch_rate(self):
        return self.branches and 100 * (
            1 - self.missed_branches / self.branches)

    @branch_rate.expression
    def branch_rate(cls):
        return case([(cls.branches != 0,
                      100 * (1 - cls.missed_branches / cls.branches))],
                    else_=0)

    @hybrid_property
    def file_rate(self):
        return self.files and 100 * (1 - self.missed_files / self.files)

    @file_rate.expression
    def file_rate(cls):
        return case([(cls.files != 0,
                      100 * (1 - cls.missed_files / cls.files))],
                    else_=0)

    @hybrid_property
    def line_rate(self):
        return self.lines and 100 * (1 - self.missed_lines / self.lines)

    @line_rate.expression
    def line_rate(cls):
        return case([(cls.lines != 0,
                      100 * (1 - cls.missed_lines / cls.lines))],
                    else_=0)

    build = relationship('Build', backref='coverages')


class CoverageConfig(Table):
    __tablename__ = 'ymci_ext_coverage__coverage_config'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
    )
    project_id = Column(Integer, primary_key=True, nullable=False)
    coverage_path = Column('coverage_path', String)

    columns_list = ['coverage_path']

    project = relationship('Project', backref=backref(
        'coverage', uselist=False, cascade='all'))
