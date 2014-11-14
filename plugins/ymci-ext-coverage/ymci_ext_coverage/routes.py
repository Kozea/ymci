from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
from pygments.util import ClassNotFound
from sqlalchemy import func
from tornado.web import HTTPError
from xml.etree import ElementTree
from ymci.routes.browse import ProjectBrowse
from ymci.ext.routes import url, Route
from ymci.model import Project, Build
from .db import Coverage
from ymci import server
from ymci.routes import graph_config
import pygal
import os
import yaml


@url(r'/project/chart/coverage/(\d+).svg')
@url(r'/project/chart/coverage/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class CoverageChart(Route):
    def get(self, id, width=None, height=None):
        svg = pygal.Line(graph_config(width, height))
        builds = (
            self.db.query(
                Build.build_id,
                func.avg(Coverage.line_rate).label('line'),
                func.avg(Coverage.branch_rate).label('branch'),
                func.avg(Coverage.cls_rate).label('cls'),
                func.avg(Coverage.file_rate).label('file'))
            .select_from(Build)
            .join(Coverage, Build.coverages)
            .filter(Build.project_id == id)
            .group_by(Build.build_id)
            .order_by(Build.build_id)
            .all())

        svg.add('Lines', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.line
        } for b in builds])
        svg.add('Branches', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.branch
        } for b in builds])
        svg.add('Classes', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.cls
        } for b in builds])
        svg.add('Files', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.file
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
        config = graph_config(width, height)
        config.logarithmic = True
        svg = pygal.Line(config)
        builds = (
            self.db.query(
                Build.build_id,
                func.sum(Coverage.lines).label('lines'),
                func.sum(Coverage.cls).label('cls'))
            .select_from(Build)
            .join(Coverage, Build.coverages)
            .filter(Build.project_id == id)
            .group_by(Build.build_id)
            .order_by(Build.build_id)
            .all())

        svg.add('Lines', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.lines or None
        } for b in builds])

        svg.add('Classes', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.cls or None
        } for b in builds])

        if width and height:
            svg.x_labels = ['#%d' % b.build_id for b in builds]

        svg.value_formatter = lambda x: '%d' % (x or 0)
        svg.title = 'Source metric'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())

server.components.project_charts.coveragechart = CoverageChart
server.components.project_charts.coveragestatschart = StatsChart


@url(r'/project/coverage/(?P<project_id>\d+)/path/(?P<path>.+)',
     suffix='LastPath')
@url(r'/project/coverage/(?P<project_id>\d+)', suffix='Last')
@url(r'/project/coverage/(?P<project_id>\d+)/build/'
     '(?P<build_id>\d+)/path/(?P<path>.+)')
class ProjectBrowseCoverage(ProjectBrowse):
    """Overidden class that adds coverage highlighting of the code."""

    def get(self, project_id, build_id=None, path=''):
        if path is None and build_id is not None:
            path = build_id
            build_id = None
        code = ''

        project = self.db.query(Project).get(project_id)
        if build_id:
            build = self.db.query(Build).get((build_id, project.project_id))
        else:
            build = project.last_build

        config = os.path.join(build.dir, 'ymci_ext_coverage_config.yaml')
        coverage_file_path = ''

        if not os.path.exists(config):
            self.log.error("Coverage file not found.")
            raise HTTPError(404)

        with open(config) as fd:
            coverage_file_path = yaml.load(fd).get('coverage_path')
        if not (coverage_file_path and os.path.exists(coverage_file_path)):
            self.log.error("Coverage file not found.")
            raise HTTPError(404)

        if path and '..' not in path:
            file = os.path.join(project.src_dir, path)
            formatter = self.get_coverage_formatter(
                id, build, file, coverage_file_path)
            if os.path.exists(file):
                try:
                    with open(file, 'r') as f:
                        code = f.read()
                except UnicodeDecodeError:
                    code = None
                else:
                    try:
                        lexer = guess_lexer_for_filename(file, code)
                    except ClassNotFound:
                        lexer = get_lexer_by_name('text')
                    code = highlight(code, lexer, formatter)

        self.render(
            'source.html', code=code,
            tree=self.recurse(
                self.get_tree_dict(project.src_dir, path), id, build),
            project=project,
            build_id=build.build_id,
            path=path
        )

    def recurse(self, dct, id, build):
        out = '<ul>'
        for name, dirdct in sorted(dct['dirs'].items()):
            out += '<li class="dir">'
            out += '<input type="checkbox"%s id="node_%s" />' % (
                ' checked' if dirdct['active'] else '',
                dirdct['name'].replace('/', ':'))
            out += '<label class="dir_title" for="node_%s">' % (
                dirdct['name'].replace('/', ':'))
            out += '<i class="glyphicon"></i> %s' % name
            out += '</label>%s' % self.recurse(dirdct, id, build)
            out += '</li>'

        for file, active in sorted(dct['files'].items()):
            out += '<li class="file">'
            out += '<label>'
            if not active:
                out += '<a href="%s">' % self.reverse_url(
                    'ProjectBrowseCoverage', id, build.build_id,
                    os.path.join(dct['name'], file))
            out += '<i class="glyphicon glyphicon-file"></i>%s' % file
            if not active:
                out += '</a>'
            out += '</label>'
            out += '</li>'

        return out + '</ul>'

    def get_coverage_formatter(self, id, build, file, coverage_file):
        project = self.db.query(Project).get(id)
        build = self.db.query(Build).get((build.build_id, project.project_id))
        tree = ElementTree.parse(coverage_file)
        root = tree.getroot()
        packages = root.find('packages')
        coverage = []
        for package in packages:
            for classes in package:
                for cls in classes:
                    if file.endswith(cls.get('filename', '')):
                        for lines in cls:
                            for line in lines:
                                if line.get('hits', '0') > '0':
                                    coverage.append(line.get('number'))
        return HtmlFormatter(
            linenos=True, cssclass='code', hl_lines=coverage)

server.components.project_links.coverage = {
    'route': 'ProjectBrowseCoverageLast',
    'label': 'Coverage'
}
