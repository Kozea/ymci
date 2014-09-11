from sqlalchemy import Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref
from ymci.ext.db import Table
from ymci.ext.config import ConfigHook
from wtforms_alchemy import ModelForm


class Config(Table):
    __tablename__ = 'ymci_ext_coverage__coverage_config'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
        ForeignKeyConstraint(['build_id'], ['build.build_id']),
    )
    project_id = Column(Integer, primary_key=True, nullable=False)
    build_id = Column(Integer)
    coverage_path = Column('coverage_path', String, default='coverage.xml')

    columns_list = ['coverage_path']

    project = relationship('Project', backref=backref(
        'coverage', uselist=False, cascade='all'))

    build = relationship(
        'Build', backref=backref('coverage_config', uselist=False))


class CoverageForm(ModelForm):
    class Meta(object):
        model = Config
        only = Config.columns_list


class CoverageConfigHook(ConfigHook):
    def pre_populate(self, form):
        form.coverage.coverage_path.data = (
            form.coverage.coverage_path.data.lstrip('./'))
        return True

    def pre_add(self, build):
        build.coverage_config = build.project.coverage
        return True
