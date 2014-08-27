from ..builder.util import execute


class BuildHook(object):

    def __init__(self, build, out):
        self.build = build
        self.out = out

    def execute(self, cmd, cwd=None):
        def send(data):
            if data:
                self.out(data)

        execute(cmd, cwd or self.build.project.src_dir, send)

    @property
    def active(self):
        return False

    def pre_copy(self):
        pass

    def pre_build(self):
        pass

    def post_build(self):
        pass
