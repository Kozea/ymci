from ymci.ext.routes import url, Route
from ymci.model import Project
from ymci import server
from ymci.routes import ymci_style
import pygal


@url(r'/project/chart/results/(\d+).svg')
class ResultChart(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        style = pygal.style.Style(**ymci_style.__dict__)
        style.colors = ('#ff7156', '#ff4136', '#ff851b', '#28b62c')
        svg = pygal.StackedBar(
            js=['/static/svg.jquery.js?://',
                '/static/pygal-tooltips.js?://'],
            style=style)

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
        svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.show_minor_x_labels = False
        svg.value_formatter = lambda x: '%.2fs' % x
        svg.x_labels_major_count = 20
        svg.include_x_axis = True
        svg.truncate_label = 10
        svg.legend_at_bottom = True
        svg.title = 'Test results'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())

server.components.project_charts.resultchart = ResultChart
