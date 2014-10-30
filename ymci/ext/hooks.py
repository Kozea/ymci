from ..builder.util import execute


class BuildHook(object):

    def __init__(self, build, out):
        self.build = build
        self.out = out

    def execute(self, cmd, cwd=None):
        def send(data):
            if data:
                self.out(data)

        execute(cmd, cwd or self.build.project.src_dir,
                send, self.build.project_id, self.build.build_id)

    @property
    def active(self):
        return False

    def pre_copy(self):
        pass

    def pre_build(self):
        pass

    def post_build(self):
        pass

    def validate_build(self):
        pass


class FormHook(object):
    @property
    def active(self):
        return False

    def pre_populate(self, form=None):
        pass

    def pre_commit(self, form=None):
        pass

    def pre_add(self):
        pass


class PrepareHook(object):
    def __init__(self, db):
        self.db = db

    @property
    def active(self):
        return False

    def prepare(self):
        pass
