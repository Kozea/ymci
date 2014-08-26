from tornado.process import Subprocess
from tornado import gen
from tornado.concurrent import Future
from subprocess import STDOUT


class BuildHook(object):

    def __init__(self, project, build, out):
        self.project = project
        self.build = build
        self.out = out

    def execute(self, cmd, cwd=None):
        future = Future()

        subproc = Subprocess(
            cmd,
            stdout=Subprocess.STREAM,
            stderr=STDOUT,
            cwd=cwd or self.project.src_dir)

        def send(data):
            if data:
                self.out(data.decode('utf-8'))

        def callback(rv):
            future.set_result(rv)

        subproc.stdout.read_until_close(send, send)
        subproc.set_exit_callback(callback)
        return future

    @property
    def active(self):
        return False

    @gen.coroutine
    def pre_copy(self):
        pass

    @gen.coroutine
    def pre_build(self):
        pass

    @gen.coroutine
    def post_build(self):
        pass
