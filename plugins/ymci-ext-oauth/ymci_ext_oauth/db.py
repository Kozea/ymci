from ymci.ext.db import Table
from sqlalchemy import Column, Integer, ForeignKeyConstraint, Boolean
from sqlalchemy.orm import relationship, backref


class OAuthProjectConfig(Table):
    __tablename__ = 'ymci_ext_oauth_config'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.project_id']),
    )
    project_id = Column(Integer, primary_key=True, nullable=False)
    public_read = Column(Boolean)
    public_build = Column(Boolean)

    columns_list = ['public_read', 'public_build']

    project = relationship('Project', backref=backref(
        'oauth_config', uselist=False, cascade='all'))
