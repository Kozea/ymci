import sys
import site
import pkg_resources
from logging import getLogger
from importlib import reload, invalidate_caches

log = getLogger('ymci')


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
                cls = entry.load()
                cls.__entry_name__ = entry.name
                self[key].append(cls)
                log.debug(
                    'Plugin %r for %s successfully loaded' % (entry, key))
            except Exception:
                log.exception('Failed to load plugin %r for %s' % (entry, key))

    def init(self):
        self.load('ymci.ext')

        # Explicit loads
        self.load('ymci.ext.db.Table')
        self.load('ymci.ext.routes.Route')

    def reload(self):
        self.clear()

        # ?
        invalidate_caches()

        # Clean up sys.path
        sys.path[:] = list(filter(
            lambda x: x.startswith(sys.prefix),
            sys.path))

        # Reloading site for egg packages
        reload(site)

        # Fix basestring import bug
        del pkg_resources.basestring

        # Reload packgares
        reload(pkg_resources)

        self.init()
