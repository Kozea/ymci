from .. import url, Route
from ..model import Project
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
            'index.html',
            projects=self.db.query(Project).order_by(Project.name).all())

import ymci.routes.blocks
import ymci.routes.project
import ymci.routes.browse
import ymci.routes.admin
