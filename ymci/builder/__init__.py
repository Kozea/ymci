from tornado.ioloop import IOLoop
from logging import getLogger
from collections import defaultdict
from threading import Thread
from time import time
from datetime import datetime
from .util import execute, ExecutionException
from .. import server
import shutil
import os
import pkg_resources


log = getLogger('ymci')


class Pool(object):

    def __init__(self, db, ioloop=None):
        self.log_streams = defaultdict(list)
        self.queue = []
        self.db = db()
        self.current_task = None
        self.ioloop = ioloop or IOLoop.instance()

    def add(self, build):
        task = Task(build)
        if not len(self.queue) and not self.current_task:
            self.build(task)
        else:
            self.queue.append(task)
        server.blocks.build.refresh()
        server.blocks.project.refresh()
        server.blocks.history.refresh(build.project_id)

    def stop(self, build):
        if (self.current_task and
                self.current_task.build.project_id == build.project_id and
                self.current_task.build.build_id == build.build_id):
            self.current_task.stop = True
            return
        for task in self.queue:
            if (self.current_task.build.project_id == build.project_id and
                    self.current_task.build.build_id == build.build_id):
                self.queue.remove(task)
        server.blocks.build.refresh()
        server.blocks.project.refresh()
        server.blocks.history.refresh(build.project_id)

    def build(self, task):
        self.current_task = task
        task.callback = lambda: self.ioloop.add_callback(self.next)
        task.db = self.db
        task.streams = self.log_streams['%s-%s' % (
            task.build.project_id,
            task.build.build_id
        )]
        self.ioloop.add_callback(task.start)

    def next(self):
        project_id = self.current_task.build.project_id
        self.current_task = None
        if len(self.queue):
            self.build(self.queue.pop(0))
        server.blocks.build.refresh()
        server.blocks.project.refresh()
        server.blocks.history.refresh(project_id)


class Task(Thread):
    def __init__(self, build, *args, **kwargs):
        self.build = build
        self.stop = False
        self.start_time = None
        self.script = build.project.script
        super(Task, self).__init__(*args, **kwargs)

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
        log.info('Starting run for task %r on %s' % (self, datetime.now()))
        self.start_time = time()
        self.log = open(self.build.log_file, 'w')
        self.build.status = 'RUNNING'

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
                status = 'FAILED'
            return status

        try:
            self.run_task()
        except ExecutionException as e:
            log.warn('Error during task execution %r' % self)
            self.build.status = treat(e)

        try:
            for hook in self.build_hooks:
                hook.post_build()
        except ExecutionException as e:
            log.warn('Error during task execution %r' % self)
            self.build.status = treat(e)

        if self.build.status == 'RUNNING':
            self.out('Success !')
            self.build.status = 'SUCCESS'

        self.build.duration = time() - self.start_time
        self.out('\n(Duration %fs)' % self.build.duration)
        self.log.close()
        self.db.commit()
        self.callback()

    def run_task(self):
        self.out('Starting build %d...\n' % self.build.build_id)
        self.build_hooks = []
        for hook in pkg_resources.iter_entry_points(
                'ymci.ext.hooks.BuildHook'):
            try:
                Hook = hook.load()
            except Exception:
                log.exception('Failed to load plugin %r' % hook)
                continue

            def out(message):
                self.out('%s> %s\n' % (Hook.__name__, message))

            hook = Hook(self.build, self.out)
            if hook.active:
                self.build_hooks.append(hook)

        src = self.build.project.src_dir

        for hook in self.build_hooks:
            hook.pre_copy()

        assert not os.path.exists(self.build.dir)

        shutil.copytree(src, self.build.dir)

        for hook in self.build_hooks:
            hook.pre_build()

        execute(
            ['/bin/bash', '-x', '-c', self.script],
            self.build.dir, self.read)
