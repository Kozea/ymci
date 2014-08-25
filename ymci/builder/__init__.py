from tornado.process import Subprocess
from subprocess import STDOUT
import os


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
        self.build_dir = os.path.join(
            project.project_dir, 'build_%d' % build.build_id)
        os.mkdir(self.build_dir)

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

        self.subprocess = Subprocess(
            ['/bin/bash', '-x', '-c', self.script],
            stdout=Subprocess.STREAM,
            stderr=STDOUT,
            cwd=self.build_dir)

        self.subprocess.set_exit_callback(self.done)
        self.subprocess.stdout.read_until_close(self.read, self.read)

    def done(self, rv):
        if rv == 0:
            self.build.status = 'SUCCESS'
        else:
            self.build.status = 'FAIL'
        self.db.commit()
