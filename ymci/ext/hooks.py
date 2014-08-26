from tornado.process import Subprocess
from subprocess import STDOUT


class BuildHook(object):

    def __init__(self, project, build, out):
        self.project = project
        self.build = build
        self.out = out

    def execute(self, cmd, callback, cwd=None):
        subproc = Subprocess(
            cmd,
            stdout=Subprocess.STREAM,
            stderr=STDOUT,
            cwd=cwd or self.project.src_dir)

        def send(data):
            if data:
                self.out(data.decode('utf-8'))

        subproc.stdout.read_until_close(send, send)
        subproc.set_exit_callback(callback)

    @property
    def active(self):
        return False

    def pre_copy(self):
        pass

    def pre_build(self):
        pass

    def post_build(self):
        pass
