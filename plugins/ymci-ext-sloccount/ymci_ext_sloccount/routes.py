from ymci.ext.routes import url, Route
from ymci.model import Project
from ymci import server
from ymci.routes import graph_config
import pygal


def graph(route, project_id, width, height, title, value_type='normal'):
    project = route.db.query(Project).get(project_id)
    config = graph_config(width, height)
    svg = pygal.Line(config)
    builds = project.builds[::-1]
    languages = list(set(
        [s.language for b in builds for s in b.sloccounts]))
    data = {language: [] for language in languages}
    for language in languages:
        for build in builds:
            if language in [sloc.language for sloc in build.sloccounts]:
                data[language].extend([{
                    'xlink': route.reverse_url(
                        'ProjectLog', project_id, build.build_id),
                    'value': s.count if value_type == 'normal' else s.percent}
                    for s in build.sloccounts if s.language == language])
            else:
                data[language].append(
                    {'xlink': route.reverse_url(
                        'ProjectLog', project_id, build.build_id),
                     'value': 0})
    for language in data.keys():
        svg.add(language, data[language])
    if width and height:
        svg.x_labels = ['#%d' % b.build_id for b in builds]
    if value_type == 'normal':
        svg.value_formatter = lambda x: '%d' % (x or 0)
    else:
        svg.value_formatter = lambda x: '%.2f %%' % (x or 0)
    svg.title = title
    route.set_header("Content-Type", "image/svg+xml")
    return svg


@url(r'/project/chart/sloccount/(\d+).svg')
@url(r'/project/chart/sloccount/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class SloccountChart(Route):
    def get(self, id, width=None, height=None):
        self.write(graph(self, id, width, height, 'Sloccount').render())


@url(r'/project/chart/sloccount/percent/(\d+).svg')
@url(r'/project/chart/sloccount/percent/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class SloccountPercentChart(Route):
    def get(self, id, width=None, height=None):
        self.write(graph(
            self, id, width, height, 'Sloccount in percent',
            value_type='percent').render())


@url(r'/project/chart/sloccount/delta/(\d+).svg')
@url(r'/project/chart/sloccount/delta/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class SloccountDeltaChart(Route):
    def get(self, id, width=None, height=None):
        project = self.db.query(Project).get(id)
        config = graph_config(width, height)
        config.print_values = False
        svg = pygal.StackedBar(config)
        builds = project.builds[::-1]
        if len(builds):
            first_build, remain_builds = builds[0], builds[1:]
            languages = list(set(
                [s.language for b in builds for s in b.sloccounts]))
            data = {language: [
                {'xlink': self.reverse_url(
                    'ProjectLog', id, first_build.build_id),
                 'value': 0}] for language in languages}

            def delta(language, previous_build, build):
                prev_count = (
                    [s.count for s in previous_build.sloccounts if
                     s.language == language] or [0])
                current_count = (
                    [s.count for s in build.sloccounts
                     if s.language == language]
                    or [0])
                return current_count[0] - prev_count[0]

            for language in languages:
                previous_build = first_build
                for build in remain_builds:
                    data[language].append({
                        'xlink': self.reverse_url(
                            'ProjectLog', id, build.build_id),
                        'value': delta(language, previous_build, build)})
                    previous_build = build
            if width and height:
                svg.x_labels = ['#%d' % b.build_id for b in builds]

            for language in data.keys():
                svg.add(language, data[language])
        svg.value_formatter = lambda x: '%d' % (x or 0)
        svg.title = 'Sloccount delta'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())


server.components.project_charts.sloccountchart = SloccountChart
server.components.project_charts.sloccountpercentchart = SloccountPercentChart
server.components.project_charts.sloccountdeltachart = SloccountDeltaChart
