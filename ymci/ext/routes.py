import sys
import os
from .. import (
    url, BlockWebSocket as BaseBlockWebSocket, Route as BaseRoute,
    ExtStaticFileHandler, MetaBlock as BaseMetaBlock)
from tornado.template import Template, BaseLoader, Loader
from logging import getLogger

log = getLogger('ymci')


class DualLoader(Loader):
    def __init__(self, roots, **kw):
        super().__init__('/', **kw)
        self.roots = roots
        self.root = None

    def load(self, name, parent_path=None):
        """Loads a template."""
        roots = self.roots
        if name.startswith('ymci:'):
            roots = roots[-1:]
            name = name[5:]
            parent_path = None
        for root in roots:
            try:
                self.root = root
                return super().load(name, parent_path)
            except FileNotFoundError:
                pass
            finally:
                self.root = self.roots[-1]
        raise FileNotFoundError(name, parent_path, self.roots)


class ExtPluginClass(type):
    def __init__(cls,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        root_module = sys.modules.get(cls.__module__.split('.')[0])
        if hasattr(root_module, '__path__'):
            if hasattr(root_module.__path__, '_path'):
                cls._ext_dir = root_module.__path__._path[0]
            else:
                cls._ext_dir = root_module.__path__[0]
        else:
            cls._ext_dir = os.path.dirname(root_module.__file__)

        cls._key = os.path.join('ext', os.path.split(cls._ext_dir)[1])
        ExtStaticFileHandler.ext_path[cls._key] = os.path.join(
            cls._ext_dir, 'static')


class PathHandler(object):
    def get_template_path(self):
        # Look for plugin template path
        path = os.path.join(self._ext_dir, 'templates')
        if os.path.exists(path):
            return path

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        namespace.update(dict(
            static_url=self.local_static_url
        ))
        return namespace

    def local_static_url(self, file, *args, **kwargs):
        # Try to get from local plugin
        path = os.path.join(self._ext_dir, 'static', file)
        if os.path.exists(path):
            # Append ext prefix
            file = os.path.join(self._key, file)
        return self.static_url(file, *args, **kwargs)

    def create_template_loader(self, template_path):
        return DualLoader([
            template_path, self.application.settings.get("template_path")])


class Route(PathHandler, BaseRoute, metaclass=ExtPluginClass):
    pass


class ExtBlockClass(BaseMetaBlock, ExtPluginClass):
    pass


class BlockWebSocket(PathHandler, BaseBlockWebSocket, metaclass=ExtBlockClass):
    pass
