from ymci.ext.db import Table
from sqlalchemy import Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship


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
    count = Column(Integer, nullable=False)

    build = relationship('Build', backref='sloccounts')

    @property
    def percent(self):
        total = sum([s.count for s in self.build.sloccounts])
        return round(self.count * 100 / total, 2)
