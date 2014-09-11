from ymci.ext.routes import url, Route
from ymci.model import Project
from ymci import server
from ymci.routes import graph_config
import pygal


@url(r'/project/chart/coverage/(\d+).svg')
@url(r'/project/chart/coverage/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class CoverageChart(Route):
    def get(self, id, width=None, height=None):
        project = self.db.query(Project).get(id)
        svg = pygal.Line(graph_config(width, height))
        builds = project.builds[::-1]
        svg.add('Lines', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.line_rate if b.coverage else 0
        } for b in builds])
        svg.add('Branches', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.branch_rate if b.coverage else 0
        } for b in builds])
        svg.add('Classes', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.cls_rate if b.coverage else 0
        } for b in builds])
        svg.add('Files', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.file_rate if b.coverage else 0
        } for b in builds])
        if width and height:
            svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.value_formatter = lambda x: '%.2f %%' % (x or 0)
        svg.title = 'Test coverage'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())


@url(r'/project/chart/coverage/stats/(\d+).svg')
@url(r'/project/chart/coverage/stats/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class StatsChart(Route):
    def get(self, id, width=None, height=None):
        project = self.db.query(Project).get(id)
        config = graph_config(width, height)
        config.logarithmic = True
        svg = pygal.Line(config)
        builds = project.builds[::-1]
        svg.add('Lines', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.lines if b.coverage else 0
        } for b in builds])

        svg.add('Classes', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.cls if b.coverage else 0
        } for b in builds])

        if width and height:
            svg.x_labels = ['#%d' % b.build_id for b in builds]

        svg.value_formatter = lambda x: '%d' % (x or 0)
        svg.title = 'Source metric'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())

server.components.project_charts.coveragechart = CoverageChart
server.components.project_charts.coveragestatschart = StatsChart
