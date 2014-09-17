import pkg_resources
from logging import getLogger

log = getLogger('ymci')

entry_points = [
    'ymci.ext.db.Table',
    'ymci.ext.form.Form',
    'ymci.ext.hook.FormHook',
    'ymci.ext.hooks.BuildHook',
    'ymci.ext.hooks.PrepareHook',
    'ymci.ext.routes.Route',
]


class Plugins(dict):
    def __init__(self):
        super().__init__()

    def __getitem__(self, entry):
        if entry not in self:
            self.load(entry)
        return super().__getitem__(entry)

    def load(self, key):
        self[key] = []
        for entry in pkg_resources.iter_entry_points(key):
            try:
                self[key].append(entry.load())
            except Exception:
                log.exception('Failed to load plugin %r for %s' % (entry, key))
