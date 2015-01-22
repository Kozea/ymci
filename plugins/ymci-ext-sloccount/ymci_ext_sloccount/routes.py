from .db import Sloccount
from ymci.ext.routes import url, Route
from ymci.model import Build
from ymci import server
from ymci.routes import graph_config
from sqlalchemy import func
from collections import defaultdict, OrderedDict
import pygal


def pair(l):
    l = list(l)
    g = list(l)
    g.pop()
    g.insert(0, (None, None))
    return zip(g, l)


def graph(route, project_id, svg, title, with_labels, type):
    builds = (
        route.db.query(
            Build.build_id,
            Sloccount.language,
            func.sum(Sloccount.count).label('sum'))
        .select_from(Build)
        .join(Sloccount, Build.sloccounts)
        .filter(Build.project_id == project_id)
        .group_by(Build.build_id, Sloccount.language)
        .order_by(Build.build_id)
        .all())

    x_labels = set()
    totals = defaultdict(int)
    languages = defaultdict(OrderedDict)
    for build in builds:
        x_labels.add(build.build_id)
        languages[build.language][build.build_id] = build.sum
        totals[build.build_id] += build.sum

    for language, builds in languages.items():
        def value(build_id, count, previous_count):
            if type == 'percent':
                return 100 * count / totals[build_id]
            if type == 'count':
                return count
            if type == 'delta':
                if previous_count:
                    return count - previous_count
                return 0

        svg.add(language, [
            {
                'xlink': route.reverse_url('ProjectLog', project_id, build_id),
                'value': value(build_id, count, prev_count)
            } for (_, prev_count), (build_id, count) in pair(builds.items())])

    if with_labels:
        svg.x_labels = ['#%d' % b for b in x_labels]

    svg.title = title
    return svg


@url(r'/project/chart/sloccount/(\d+).svg')
@url(r'/project/chart/sloccount/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class SloccountChart(Route):
    def get(self, project_id, width=None, height=None):
        config = graph_config(width, height)
        svg = pygal.Line(config)
        svg = graph(self, project_id, svg, 'Sloccount', bool(width), 'count')
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())


@url(r'/project/chart/sloccount/percent/(\d+).svg')
@url(r'/project/chart/sloccount/percent/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class SloccountPercentChart(Route):
    def get(self, project_id, width=None, height=None):
        config = graph_config(width, height)
        config.fill = True
        config.range = 0, 100
        svg = pygal.StackedLine(config)
        svg.fill = True
        svg = graph(
            self, project_id, svg, 'Sloccount in percent', bool(width),
            'percent')
        svg.value_formatter = lambda x: '%.2f %%' % (x or 0)
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())


@url(r'/project/chart/sloccount/delta/(\d+).svg')
@url(r'/project/chart/sloccount/delta/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class SloccountDeltaChart(Route):
    def get(self, project_id, width=None, height=None):
        config = graph_config(width, height)
        config.print_values = False
        svg = pygal.StackedBar(config)
        svg = graph(self, project_id, svg, 'Sloccount delta', bool(width),
                    'delta')
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())


server.components.project_charts.sloccountchart = SloccountChart
server.components.project_charts.sloccountpercentchart = SloccountPercentChart
server.components.project_charts.sloccountdeltachart = SloccountDeltaChart
