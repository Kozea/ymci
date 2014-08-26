from tornado.process import Subprocess
from subprocess import STDOUT
from logging import getLogger
import shutil
import os
import pkg_resources

log = getLogger('ymci')


class Builder(object):
    def __init__(self, db):
        self.queue = []
        self.current_task = None
        self.db = db

    def add(self, task):
        if not len(self.queue):
            self.build(task)
        else:
            self.queue.append(task)

    def build(self, task):
        self.current_task = task
        task.db = self.db
        task.run(self.next)

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

    def read(self, data):
        if data:
            data = data.decode('utf-8')
            self.log.write(data)
            self.log.flush()

            for sock in self.socks:
                try:
                    sock.write_message(data)
                except Exception:
                    sock.on_close()
                    sock.close()

        else:
            self.log.close()

    def run(self, callback):
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
                self.log.write('%s> %s\n' % (Hook.__name__, message))

            hook = Hook(self.project, self.build, out)
            if hook.active:
                self.build_hooks.append(hook)

        src = self.project.src_dir

        for hook in self.build_hooks:
            hook.pre_copy()

        assert not os.path.exists(self.build.dir)

        shutil.copytree(src, self.build.dir)

        for hook in self.build_hooks:
            hook.pre_build()

        self.subprocess = Subprocess(
            ['/bin/bash', '-x', '-c', self.script],
            stdout=Subprocess.STREAM,
            stderr=STDOUT,
            cwd=self.build.dir)

        self.subprocess.set_exit_callback(self.done)
        self.subprocess.stdout.read_until_close(self.read, self.read)
        self.log.flush()

    def done(self, rv):
        if rv == 0:
            self.build.status = 'SUCCESS'
        else:
            self.build.status = 'FAIL'

        for hook in self.build_hooks:
            hook.post_build(self.build.status)

        self.db.commit()
