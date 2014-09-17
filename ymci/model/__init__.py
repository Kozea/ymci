from tornado.web import HTTPError
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, create_engine,
    func)
from sqlalchemy.orm import relationship, Query as SAQuery
from sqlalchemy.ext.declarative import declarative_base
from logging import getLogger
from .. import server
import os
import pkg_resources


log = getLogger('ymci')
engine = create_engine(server.conf['db_url'], echo=False)
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

    builds = relationship('Build', cascade='all, delete-orphan',
                          backref='project', lazy='dynamic',
                          order_by='Build.build_id.desc()')

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
        path = os.path.join(server.conf['projects_path'], self.dir_name)
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

    @property
    def last_non_running_build(self):
        return (
            self.builds
                .filter(~Build.status.in_(('RUNNING', 'PENDING')))
                .order_by(Build.build_id.desc())
                .first())

    @property
    def last_successful_build(self):
        return (
            self.builds
                .filter(Build.status == 'SUCCESS')
                .order_by(Build.build_id.desc())
                .first())

    @property
    def average_build_duration(self):
        return (self.builds
                .filter(Build.status == 'SUCCESS')
                .order_by(Build.build_id.desc())
                .limit(5)
                .from_self(
                    func.avg(Build.duration)).scalar() or 60 * 10)

    def health(self, over=10):
        count = self.builds.count()
        if not count:
            return 0

        if count > over:
            count = over

        ok = len(list(filter(
            lambda b: b.status == 'SUCCESS', self.builds[:count])))
        return int((ok / count) * over)


class Build(Table):
    __tablename__ = 'build'
    build_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Project.project_id),
                        primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    duration = Column(Float)
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

    @property
    def bootstrap_status(self):
        return {
            'SUCCESS': 'success',
            'RUNNING': 'primary',
            'FAILED': 'danger',
            'STOPPED': 'default',
            'PENDING': 'info',
            'WARNING': 'warning',
            None: 'default'
        }[self.status]


class User(Table):
    __tablename__ = 'ymci_user'

    login = Column(String, primary_key=True)
    password = Column(String)
    last_login = Column(DateTime)
    login_count = Column(Integer)
