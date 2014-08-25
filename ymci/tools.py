from tornado.process import Subprocess
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
    def __init__(self, project, build):
        self.project = project
        self.build = build
        self.script = project.script
        self.build_dir = os.path.join(
            project.project_dir, 'build_%d' % build.build_id)
        os.mkdir(self.build_dir)

    def run(self, callback):
        log = open(self.build.log_file, 'w')
        log.write('Starting build %d...\n' % self.build.build_id)
        self.subprocess = Subprocess(
            ['/bin/bash', '-x', '-c', self.script],
            stdout=log,
            stderr=log,
            cwd=self.build_dir)
        self.subprocess.set_exit_callback(self.done)

    def done(self, rv):
        if rv == 0:
            self.build.status = 'SUCCESS'
        else:
            self.build.status = 'FAIL'
        self.db.commit()
