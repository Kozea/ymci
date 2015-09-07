from tornado.ioloop import IOLoop
from logging import getLogger
from collections import defaultdict
from threading import Thread
from time import time
from datetime import datetime
from .util import execute, ExecutionException
from ..utils import short_transaction, secure_rmtree
from ..model import Build
from .. import server
import traceback
import shutil
import os


log = getLogger('ymci')
blocks = server.components.blocks


def refresh(id):
    log.debug('Refreshing build/project/home/history')
    blocks.build.refresh()
    blocks.project.refresh()
    blocks.home.refresh()
    blocks.history.refresh(id)


class Pool(object):

    def __init__(self, ioloop=None):
        self.log_streams = defaultdict(list)
        self.queue = []
        self.tasks = []
        self.limit = server.conf.get('slot_size', 5)
        self.stop_flags = []
        self.ioloop = ioloop or IOLoop.instance()

    def add(self, build):
        task = Task(
            build.build_id, build.project_id,
            self.log_streams['%s-%s' % (build.project_id, build.build_id)],
            build.project.name, self.ioloop)
        if len(self.tasks) < self.limit and (
                task.project_id not in [t.project_id for t in self.tasks]):
            self.build(task)
        else:
            self.queue.append(task)
        refresh(build.project_id)

    def stop(self, build):
        for task in self.tasks:
            if (task.project_id == build.project_id and
                    task.build_id == build.build_id):
                self.stop_flags.append((build.project_id, build.build_id))
                # Set stop flag to keep the fact that it's manual stopping
                task.stop = True

        for task in self.queue:
            if (task.project_id == build.project_id and
                    task.build_id == build.build_id):
                self.queue.remove(task)

        refresh(build.project_id)

    def build(self, task):
        self.tasks.append(task)
        task.callback = self.next
        self.ioloop.add_callback(task.start)

    def next(self, task):
        project_id = task.project_id
        self.tasks.remove(task)

        for queued_task in self.queue[:]:
            if queued_task.project_id not in [
                    running_task.project_id
                    for running_task in self.tasks]:
                self.queue.remove(queued_task)
                self.build(queued_task)
                break
        refresh(project_id)


class Task(Thread):
    def __init__(self, build_id, project_id, streams, name, ioloop,
                 *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.build_id = build_id
        self.project_id = project_id
        self.name = name
        self.streams = streams
        self.ioloop = ioloop
        self.stop = False
        self.start_time = None

    def out(self, data):
        self.log.write(data)
        self.log.flush()

        for stream in self.streams:
            try:
                for line in data.splitlines(True):
                    stream.write_message(line)
            except Exception:
                stream.on_close()
                stream.close()

    def read(self, data):
        if data:
            self.out(data)

    def run(self):
        try:
            self.safe_run()
        except Exception as e:
            try:
                log.exception('Error during task run')
                self.out('YMCI Internal error %s' % (
                    ', '.join(traceback.format_exception_only(type(e), e))))
                self.db.rollback()
            except Exception:
                pass
            with short_transaction() as db:
                build = db.query(Build).get((self.build_id, self.project_id))
                build.status = 'BROKEN'
            self.ioloop.add_callback(self.callback, self)

    def safe_run(self):
        log.info('Starting run for task %r on %s' % (self, datetime.now()))

        self.start_time = time()

        with short_transaction() as db:
            build = db.query(Build).get((self.build_id, self.project_id))
            build.status = 'RUNNING'

        self.db = server.scoped_session()
        self.build = self.db.query(Build).get((self.build_id, self.project_id))
        self.ioloop.add_callback(refresh, self.project_id)

        self.log = open(self.build.log_file, 'w')
        self.script = self.build.project.script
        self.latest_dir = self.build.project.latest_dir
        self.latest_success_dir = self.build.project.latest_success_dir

        def treat(e):
            if e.errno < 0:
                if self.stop:
                    self.out('\nStoped by user')
                    status = 'STOPPED'
                else:
                    self.out('\nCommand %s was killed by signal %d' % (
                        e.command, -e.errno))
                    status = 'KILLED'
            else:
                self.out('\nCommand %s returned %d' % (
                    e.command, -e.errno))
                status = 'BROKEN'
            return status

        log.debug('Running task %r' % self)
        try:
            self.run_task()
        except ExecutionException as e:
            log.warn('Error during task execution %r' % self, exc_info=True)
            self.build.status = treat(e)

        self.out('\n')
        log.debug('Task %r ran. Validating build' % self)
        try:
            for hook in self.build_hooks:
                hook.validate_build()
        except ExecutionException as e:
            log.warn('Error during task execution %r' % self, exc_info=True)
            self.build.status = treat(e)

        log.debug('Checking status after validation for %r ' % self)
        if self.build.status == 'RUNNING':
            self.out('Success !')
            self.build.status = 'SUCCESS'

        self.build.duration = time() - self.start_time
        self.out('\n(Duration %fs)' % self.build.duration)
        log.debug('Persisting state for %r ' % self)
        self.db.commit()

        log.debug('Running post build for %r ' % self)
        for hook in self.build_hooks:
            hook.post_build()

        if self.build.status == 'SUCCESS':
            log.debug('Symlinking to latest_success_dir for %r ' % self)
            if os.path.exists(self.latest_success_dir):
                assert os.path.islink(self.latest_success_dir)
                os.remove(self.latest_success_dir)

            os.symlink(self.build.dir, self.latest_success_dir)

        log.debug('Closing log file and calling callback %r ' % self)
        self.log.close()
        self.ioloop.add_callback(self.callback, self)
        server.scoped_session.remove()

    def run_task(self):
        self.out('Starting build %d...\n' % self.build.build_id)
        self.build_hooks = []

        for Hook in server.plugins['ymci.ext.hooks.BuildHook']:
            def get_out(hook_name):
                def out(message):
                    self.out('%s> %s\n' % (hook_name, message))
                return out

            hook = Hook(self.build, get_out(Hook.__name__))
            if hook.active:
                self.build_hooks.append(hook)

        src = self.build.project.src_dir
        log.debug('Running pre copy hooks for %r' % self)
        for hook in self.build_hooks:
            hook.pre_copy()

        assert not os.path.exists(self.build.dir), (
            '%s already exists' % self.build.dir)

        log.debug('Copying tree for %r' % self)
        shutil.copytree(src, self.build.dir, symlinks=True)

        log.debug('Linking to latest %r' % self)
        if os.path.exists(self.latest_dir):
            assert os.path.islink(self.latest_dir)
            os.remove(self.latest_dir)

        os.symlink(self.build.dir, self.latest_dir)
        log.debug('Running pre build hooks for %r' % self)
        for hook in self.build_hooks:
            hook.pre_build()

        script_fn = os.path.abspath(os.path.join(self.latest_dir, '.ymci.sh'))
        script = self.script
        if not script.startswith('#!'):
            # This is not sexy
            script = (
                '#!/bin/sh\n' +
                script
            )

        with open(script_fn, 'w') as build_script:
            build_script.write(script)
        os.chmod(script_fn, 0o700)

        log.debug('Executing %s for %r' % (script_fn, self))
        execute(
            script_fn,
            self.latest_dir, self.read,
            self.build.project_id, self.build.build_id)
        log.debug('Execution complete for %r' % self)

        kept = self.build.project.kept_builds
        if kept is not None and kept > 0:
            self.out('Cleaning... (Keeping %d project builds)\n' % kept)
            if self.build.build_id - kept > 0:
                for build_id in range(1, self.build.build_id - kept + 1):
                    build_dir = os.path.join(
                        self.build.project.project_dir, 'build_%d' % build_id)
                    if os.path.exists(build_dir):
                        self.out('Removing %s\n' % build_dir)
                        secure_rmtree(build_dir)
