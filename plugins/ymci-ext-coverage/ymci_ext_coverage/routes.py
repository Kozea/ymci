from ymci.ext.routes import url, Route
from ymci.model import Project
from ymci import server
from ymci.routes import ymci_style
import pygal


@url(r'/project/chart/coverage/(\d+).svg')
class CoverageChart(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        style = pygal.style.Style(**ymci_style.__dict__)
        svg = pygal.Line(
            js=['/static/svg.jquery.js?://',
                '/static/pygal-tooltips.js?://'],
            style=style)

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
        svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.show_minor_x_labels = False
        svg.value_formatter = lambda x: '%.2fs %%' % x
        svg.x_labels_major_count = 20
        svg.include_x_axis = True
        svg.truncate_label = 10
        svg.legend_at_bottom = True
        svg.title = 'Test coverage'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())


@url(r'/project/chart/coverage/stats/(\d+).svg')
class StatsChart(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        style = pygal.style.Style(**ymci_style.__dict__)
        svg = pygal.Line(
            js=['/static/svg.jquery.js?://',
                '/static/pygal-tooltips.js?://'],
            style=style)

        builds = project.builds[::-1]
        svg.add('Lines', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.lines if b.coverage else 0
        } for b in builds])

        svg.add('Files', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.coverage.files if b.coverage else 0
        } for b in builds])

        svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.show_minor_x_labels = False
        svg.value_formatter = lambda x: '%d' % x
        svg.x_labels_major_count = 20
        svg.include_x_axis = True
        svg.truncate_label = 10
        svg.legend_at_bottom = True
        svg.title = 'Source metric'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())

server.components.project_charts.coveragechart = CoverageChart
server.components.project_charts.coveragestatschart = StatsChart
