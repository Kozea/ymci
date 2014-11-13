from ymci.ext.db import Table
from sqlalchemy import Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref


class Sloccount(Table):
    __tablename__ = 'ymci_ext_sloccount__result'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'build_id'],
            ['build.project_id', 'build.build_id']),
    )
    project_id = Column(Integer, primary_key=True)
    build_id = Column(Integer, primary_key=True)
    language = Column(String, primary_key=True)
    filename = Column(String, primary_key=True, server_default='sloccount.sc')
    count = Column(Integer, nullable=False)

    build = relationship('Build', backref='sloccounts')

    @property
    def percent(self):
        total = sum([s.count for s in self.build.sloccounts])
        return round(self.count * 100 / total, 2)


class SloccountConfig(Table):
    __tablename__ = 'ymci_ext_sloccount__sloccount_config'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
    )
    project_id = Column(Integer, primary_key=True, nullable=False)
    sloccount_path = Column('sloccount_path', String)

    columns_list = ['sloccount_path']

    project = relationship('Project', backref=backref(
        'sloccount', uselist=False, cascade='all'))
