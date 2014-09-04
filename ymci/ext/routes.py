import sys
import os
from .. import url, Route as BaseRoute
from tornado.template import Template, BaseLoader, Loader


class DualLoader(Loader):
    def __init__(self, roots, **kw):
        super().__init__('/', **kw)
        self.roots = roots
        self.root = None

    def load(self, name, parent_path=None):
        """Loads a template."""
        for root in self.roots:
            try:
                self.root = root
                return super().load(name, parent_path)
            except FileNotFoundError:
                pass
            finally:
                self.root = root
        raise FileNotFoundError(name, parent_path, self.roots)


class Route(BaseRoute):

    @property
    def _get_path(self):
        plugin_source = sys._getframe(4).f_code.co_filename
        parts = plugin_source.split(os.path.sep)
        for i, part in enumerate(reversed(parts)):
            if part.startswith('ymci_ext'):
                break
        else:
            return
        path = os.path.sep.join(parts[:-(i + 1)] + ['templates'])
        if os.path.exists(path):
            return path

    def get_template_path(self):
        # Look for plugin template path
        return self._get_path

    def create_template_loader(self, template_path):
        return DualLoader([
            template_path, self.application.settings.get("template_path")])

