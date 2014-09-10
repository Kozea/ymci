from ymci.ext.routes import url, Route
from ymci.model import Project
from ymci import server
from ymci.routes import graph_config
import pygal


@url(r'/project/chart/results/(\d+).svg')
@url(r'/project/chart/results/(\d+)_(\d+)_(\d+).svg')
class ResultChart(Route):
    def get(self, id, width=None, height=None):
        project = self.db.query(Project).get(id)
        config = graph_config(width, height)
        config.style.colors = ('#ff7156', '#ff4136', '#ff851b', '#28b62c')
        config.print_values = False
        svg = pygal.StackedBar(config)
        builds = project.builds[::-1]
        svg.add('Errors', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.result.error if b.result else 0} for b in builds])
        svg.add('Failures', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.result.fail if b.result else 0} for b in builds])
        svg.add('Skips', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.result.skip if b.result else 0} for b in builds])
        svg.add('Success', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.result.success if b.result else 0} for b in builds])
        if width and height:
            svg.x_labels = ['#%d' % b.build_id for b in builds]

        svg.value_formatter = lambda x: '%d' % (x or 0)
        svg.title = 'Test results'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())

server.components.project_charts.resultchart = ResultChart
