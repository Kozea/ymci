class ConfigHook(object):

    @property
    def active(self):
        return False

    def pre_populate(self, form=None):
        pass

    def pre_commit(self, form=None):
        pass
