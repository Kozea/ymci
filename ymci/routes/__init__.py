from .. import url, Route, BlockWebSocket, server
from ..model import Project, Build
from time import time
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


def graph_config(width, height):
    class GraphConfig(Config):
        """Config for minimal graph."""
        js = ['/static/svg.jquery.js?://', '/static/pygal-tooltips.js?://']
        style = pygal.style.Style(**ymci_style.__dict__)
        show_minor_x_labels = False
        x_labels_major_count = 20
        truncate_label = 10
        legend_at_bottom = True
    config = GraphConfig()
    if not (width or height):
        config.show_legend = False
        config.show_y_labels = False
        config.show_x_labels = False
        config.show_dots = False
        config.no_data_font_size = 36
        config.x_labels_major_count = None
        config.width = config.height = 200
    else:
        # Good ratio for graph size, associated with a `margin` on the popup
        config.width = int(width) * 0.8
        config.height = int(height) * 0.8
    return copy(config)


@url(r'/')
class Index(Route):
    def get(self):
        return self.render(
            'index.html', projects=self.db.query(Project).all())


@url(r'/blocks/build')
class BuildBlock(BlockWebSocket):
    def render_block(self):
        builder = server.builder
        builds = []
        for task in builder.tasks:
            build = self.db.query(Build).get(
                (task.build_id,
                 task.project_id))
            if task.start_time:
                now = time() - task.start_time
            else:
                now = None
            builds.append((now, build))

        free_slots = builder.limit - len(builder.tasks)
        return self.render_string(
            'blocks/build.html', current_builds=builds, free_slots=free_slots)


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
