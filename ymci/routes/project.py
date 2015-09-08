from . import ymci_style, graph_config
from .. import url, Route, server, WebSocket
from ..model import Project, Build
from ..utils import short_transaction, secure_rmtree
from datetime import datetime
from logging import getLogger
from wtforms_alchemy import ModelForm, ModelFormField
import pygal
import os


log = getLogger('ymci')


class Meta(object):
    model = Project

forms = {
    c.Meta.model.project.property.back_populates: ModelFormField(c)
    for c in server.plugins['ymci.ext.form.Form']}

for ufield in forms.values():
    ufield.creation_counter += 10000

forms.update({'Meta': Meta})
ProjectForm = type('ProjectForm', (ModelForm,), forms)


@url(r'/project/list')
class ProjectList(Route):
    def get(self):
        self.render(
            'project/list.html', projects=self.db.query(Project).all())


@url(r'/project/view/(?P<project_id>\d+)')
class ProjectView(Route):
    def get(self, project_id):
        project = self.db.query(Project).get(project_id)
        self.render('project/view.html', project=project)


@url(r'/project/add')
class ProjectAdd(Route):
    def get(self):
        return self.render(
            'form.html', form=ProjectForm(),
            render_form_recursively=self.render_form_recursively)

    def post(self):
        form = ProjectForm(self.posted)
        if form.validate():
            project = Project()
            for hook in self.application.plugins['ymci.ext.hook.FormHook']:
                hook().pre_populate(form)
            form.populate_obj(project)
            self.db.add(project)
            self.db.commit()
            self.blocks.project.refresh()
            self.blocks.home.refresh()
            self.redirect('/')
            return
        self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)


@url(r'/project/edit/(?P<project_id>\d+)')
class ProjectEdit(Route):
    def get(self, project_id):
        project = self.db.query(Project).get(project_id)
        self.render(
            'form.html', form=ProjectForm(obj=project),
            render_form_recursively=self.render_form_recursively)

    def post(self, project_id):
        project = self.db.query(Project).get(project_id)
        form = ProjectForm(self.posted, project)
        if form.validate():
            for hook in self.application.plugins['ymci.ext.hook.FormHook']:
                hook().pre_populate(form)
            old_dir = project.project_dir
            form.populate_obj(project)
            if project.project_dir != old_dir:
                os.rename(old_dir, project.project_dir)
            self.db.commit()
            self.blocks.project.refresh()
            self.blocks.home.refresh()
            self.redirect('/')
            return
        self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)


@url(r'/project/delete/(?P<project_id>\d+)')
class ProjectDelete(Route):
    def get(self, project_id):
        project = self.db.query(Project).get(project_id)
        self.render(
            'ask.html', confirm="Do you really want to delete project %s" %
            project.name)

    def post(self, project_id):
        project = self.db.query(Project).get(project_id)
        self.db.delete(project)
        secure_rmtree(project.project_dir)
        self.db.commit()
        self.blocks.project.refresh()
        self.blocks.home.refresh()
        self.redirect(self.reverse_url('ProjectList'))


@url(r'/project/build/(?P<project_id>\d+)')
class ProjectBuild(Route):
    def get(self, project_id):
        self.redirect(self.build(project_id))

    def post(self, project_id):
        self.build(project_id)
        self.write('OK')
        self.finish()

    def build(self, project_id):
        project = self.db.query(Project).get(project_id)
        build = Build()
        build.timestamp = datetime.now()
        build.build_id = (
            project.last_build and project.last_build.build_id or 0) + 1
        build.status = 'PENDING'
        project.builds.append(build)

        self.db.add(build)

        self.db.commit()

        self.application.builder.add(build)
        return self.reverse_url(
            'ProjectLog', project.project_id, build.build_id)


@url(r'/log/(?P<project_id>\d+)/(?P<build_id>\d+)/pipe')
class ProjectLogWebSocket(WebSocket):
    def open(self, project_id, build_id):
        self.id = project_id
        self.idx = build_id
        with short_transaction() as db:
            self.build = db.query(Build).get((build_id, project_id))
            self.application.builder.log_streams['%s-%s' % (
                self.build.project_id,
                self.build.build_id
            )].append(self)

    def on_close(self):
        self.application.builder.log_streams[
            '%s-%s' % (self.id, self.idx)].remove(self)


@url(r'/project/log/(?P<project_id>\d+)/(?P<build_id>\d+)')
@url(r'/project/log/(?P<project_id>\d+)', suffix='Last')
class ProjectLog(Route):
    def get(self, project_id, build_id=None):
        project = self.db.query(Project).get(project_id)
        if build_id:
            build = self.db.query(Build).get((build_id, project_id))
        else:
            build = project.last_build
        if os.path.exists(build.log_file):
            with open(build.log_file, 'r') as f:
                log = f.read()
        else:
            log = None
        self.render(
            'project/log.html', project=project, build=build, log=log)


@url(r'/project/build/(?P<project_id>\d+)/(?P<build_id>\d+)/stop')
class ProjectBuildStop(Route):
    def get(self, project_id, build_id):
        build = self.db.query(Build).get((build_id, project_id))
        self.application.builder.stop(build)

        self.redirect(self.reverse_url(
            'ProjectLog', build.project_id, build.build_id))


@url(r'/project/chart/time/(?P<project_id>\d+).svg')
@url(r'/project/chart/time/'
     '(?P<project_id>\d+)_(?P<width>\d+)_(?P<height>\d+).svg',
     suffix='Size')
class ProjectChartTime(Route):
    def get(self, project_id, width=None, height=None):
        project = self.db.query(Project).get(project_id)
        config = graph_config(width, height)
        config.style = ymci_style
        svg = pygal.Line(config)
        builds = project.builds.all()[::-1]
        svg.add('Build times', {
            '#%d' % b.build_id: {
                'xlink': self.reverse_url(
                    'ProjectLog', project_id, b.build_id),
                'color': b.bootstrap_status_color,
                'value': b.duration
            } for b in builds if b.status != 'STOPPED'})
        svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.value_formatter = lambda x: '%.2fs' % (x or 0)
        svg.show_legend = False
        svg.show_labels = False
        svg.title = 'Build duration in seconds'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())
