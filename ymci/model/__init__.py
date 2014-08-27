from tornado.web import HTTPError
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, create_engine)
from sqlalchemy.orm import relationship, Query as SAQuery
from sqlalchemy.ext.declarative import declarative_base
from .. import conf
import os


engine = create_engine(conf['db_url'], echo=False)
Table = declarative_base()


class Query(SAQuery):
    def get(self, *args, **kwargs):
        obj = super(Query, self).get(*args, **kwargs)
        if obj is None:
            raise HTTPError(404)
        return obj


class Project(Table):
    __tablename__ = 'project'
    project_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    repository = Column(String)
    script = Column(Text)

    builds = relationship('Build', backref='project', lazy='dynamic')

    @property
    def dir_name(self):
        return (
            self.name
            .replace(' ', '_')
            .replace('.', '_')
            .replace('\\', '_')
            .replace('/', '_'))

    @property
    def project_dir(self):
        path = os.path.join(conf['projects_path'], self.dir_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    def src_dir(self):
        path = os.path.join(self.project_dir, 'src')
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    def last_build(self):
        return self.builds.order_by(Build.build_id.desc()).first()


class Build(Table):
    __tablename__ = 'build'
    build_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Project.project_id),
                        primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    duration = Column(DateTime)
    status = Column(String)

    @property
    def dir(self):
        return os.path.join(
            self.project.project_dir, 'build_%d' % self.build_id)

    @property
    def log_file(self):
        return os.path.join(
            self.project.project_dir,
            'build_%d.log' % self.build_id)
