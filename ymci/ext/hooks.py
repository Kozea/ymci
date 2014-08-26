from tornado import gen
from ymci.builder.util import execute


class BuildHook(object):

    def __init__(self, project, build, out):
        self.project = project
        self.build = build
        self.out = out

    def execute(self, cmd, cwd=None):
        def send(data):
            if data:
                self.out(data)

        return execute(cmd, cwd or self.project.src_dir, send)

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
