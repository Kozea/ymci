from tornado.ioloop import IOLoop
from tornado import gen
from logging import getLogger
from ymci.builder.util import execute
import shutil
import os
import pkg_resources


log = getLogger('ymci')


class Builder(object):
    def __init__(self, db, ioloop=None):
        self.queue = []
        self.current_task = None
        self.db = db
        self.ioloop = ioloop or IOLoop.instance()

    def add(self, task):
        if not len(self.queue):
            self.build(task)
        else:
            self.queue.append(task)

    def build(self, task):
        self.current_task = task
        task.db = self.db
        self.ioloop.add_callback(task.run, self.next)

    def next(self):
        self.db.remove()
        self.current_task = None
        if len(self.queue):
            self.build(self.queue.pop(0))


class Task(object):
    def __init__(self, project, build, socks):
        self.project = project
        self.build = build
        self.socks = socks
        self.script = project.script

    def out(self, data):
        self.log.write(data)
        self.log.flush()

        for sock in self.socks:
            try:
                sock.write_message(data)
            except Exception:
                sock.on_close()
                sock.close()

    def read(self, data):
        if data:
            self.out(data)
        else:
            self.log.close()

    @gen.coroutine
    def run(self, callback):
        log.info('Starting run for task')
        self.log = open(self.build.log_file, 'w')
        self.log.write('Starting build %d...\n' % self.build.build_id)
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

            hook = Hook(self.project, self.build, self.out)
            if hook.active:
                self.build_hooks.append(hook)

        src = self.project.src_dir

        for hook in self.build_hooks:
            yield hook.pre_copy()

        assert not os.path.exists(self.build.dir)

        shutil.copytree(src, self.build.dir)

        for hook in self.build_hooks:
            yield hook.pre_build()

        rv = yield execute(
            ['/bin/bash', '-x', '-c', self.script],
            self.build.dir, self.read)

        # self.db.remove()
        # build = self.db.query(Build).get(self.build.build_id)
        if rv == 0:
            self.build.status = 'SUCCESS'
        else:
            self.build.status = 'FAIL'

        for hook in self.build_hooks:
            yield hook.post_build()

        self.db.commit()
