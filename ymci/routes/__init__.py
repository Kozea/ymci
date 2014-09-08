from .. import url, Route, BlockWebSocket, server
from ..model import Project
import pkg_resources
from logging import getLogger
import pygal
from pygal import Config
from copy import copy
log = getLogger('ymci')


base_style = pygal.style.Style(
    background='white',
    plot_background='white',
    foreground='#555',
    foreground_light='#666',
    foreground_dark='#444',
    opacity='.6',
    opacity_hover='.9',
    transition='400ms ease-in',
    colors=[])

ymci_style = pygal.style.RotateStyle('#28b62c', base_style=base_style)


def default_config():
    class DefaultConfig(Config):
        """Config for minimal graph."""
        js = ['/static/svg.jquery.js?://', '/static/pygal-tooltips.js?://']
        style = pygal.style.Style(**ymci_style.__dict__)
        width = 500
        height = 500
    return copy(DefaultConfig)


@url(r'/')
class Index(Route):
    def get(self):
        return self.render(
            'index.html', projects=self.db.query(Project).all())


@url(r'/blocks/build')
class BuildBlock(BlockWebSocket):
    def render_block(self):
        return self.render_string('blocks/build.html')


@url(r'/blocks/project')
class ProjectBlock(BlockWebSocket):
    def render_block(self):
        return self.render_string(
            'blocks/project.html',
            projects=self.db.query(Project).all())


@url(r'/blocks/history/([^\/]+)')
class HistoryBlock(BlockWebSocket):
    def render_block(self, id):
        return self.render_string(
            'blocks/history.html',
            project=self.db.query(Project).get(id))


@url(r'/blocks/home')
class HomeBlock(BlockWebSocket):
    def render_block(self):
        return self.render_string(
            'blocks/home.html',
            projects=self.db.query(Project).all())


blocks = server.components.blocks
blocks.build = BuildBlock
blocks.project = ProjectBlock
blocks.home = HomeBlock
blocks.history = HistoryBlock
import ymci.routes.project

plugin_routes = []

for route in pkg_resources.iter_entry_points('ymci.ext.routes.Route'):
    try:
        plugin_routes.append(route.load())
    except Exception:
        log.exception('Failed to load plugin route %r' % route)
        continue
