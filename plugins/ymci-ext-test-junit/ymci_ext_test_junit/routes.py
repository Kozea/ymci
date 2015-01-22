from ymci.ext.routes import url, Route
from .db import Result
from ymci.model import Build
from ymci import server
from ymci.routes import graph_config
from sqlalchemy import func
import pygal


@url(r'/project/chart/results/(\d+).svg')
@url(r'/project/chart/results/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class ResultChart(Route):
    def get(self, project_id, width=None, height=None):
        config = graph_config(width, height)
        config.style.colors = ('#ff7156', '#ff4136', '#ff851b', '#28b62c')
        config.print_values = False
        svg = pygal.StackedBar(config)
        builds = (
            self.db.query(
                Build.build_id,
                func.sum(Result.error).label('errors'),
                func.sum(Result.fail).label('fails'),
                func.sum(Result.skip).label('skips'),
                func.sum(Result.success).label('success'))
            .select_from(Build)
            .join(Result, Build.results)
            .filter(Build.project_id == project_id)
            .group_by(Build.build_id)
            .order_by(Build.build_id)
            .all())

        svg.add('Errors', [{
            'xlink': self.reverse_url('ProjectLog', project_id, b.build_id),
            'value': b.errors or 0} for b in builds])
        svg.add('Failures', [{
            'xlink': self.reverse_url('ProjectLog', project_id, b.build_id),
            'value': b.fails or 0} for b in builds])
        svg.add('Skips', [{
            'xlink': self.reverse_url('ProjectLog', project_id, b.build_id),
            'value': b.skips or 0} for b in builds])
        svg.add('Success', [{
            'xlink': self.reverse_url('ProjectLog', project_id, b.build_id),
            'value': b.success or 0} for b in builds])
        if width and height:
            svg.x_labels = ['#%d' % b.build_id for b in builds]

        svg.value_formatter = lambda x: '%d' % (x or 0)
        svg.title = 'Test results'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())

server.components.project_charts.resultchart = ResultChart
