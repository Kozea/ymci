from sqlalchemy import Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref
from ymci.ext.db import Table
from ymci.ext.config import ConfigHook
from wtforms_alchemy import ModelForm


class Config(Table):
    __tablename__ = 'ymci_ext_coverage__coverage_config'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
    )
    project_id = Column(Integer, primary_key=True)
    coverage_path = Column('coverage_path', String)

    columns_list = ['coverage_path']

    project = relationship('Project', backref=backref(
        'coverage', uselist=False,
        cascade='all, delete-orphan', single_parent=True))


class CoverageForm(ModelForm):
    class Meta(object):
        model = Config
        only = Config.columns_list


class CoverageConfigHook(ConfigHook):
    def pre_populate(self, form):
        form.coverage.coverage_path.data = (
            form.coverage.coverage_path.data.lstrip('./'))
        return True
