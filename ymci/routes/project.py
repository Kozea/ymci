from . import ymci_style, graph_config
from .. import url, Route, server, WebSocket
from ..model import Project, Build
from ..utils import short_transaction, secure_rmtree
from datetime import datetime
from logging import getLogger
from wtforms_alchemy import ModelForm, ModelFormField
import pkg_resources
import pygal
import os


log = getLogger('ymci')

config_forms = []
for config_form in pkg_resources.iter_entry_points('ymci.ext.form.Form'):
    try:
        config_forms.append(config_form.load())
    except Exception:
        log.exception('Failed to load config from plugin %s' % config_form)

config_hooks = []
for config_hook in pkg_resources.iter_entry_points(
        'ymci.ext.hook.FormHook'):
    try:
        config_hooks.append(config_hook.load())
    except:
        log.exception('Failed to load hook from plugin %s' % config_hook)


class Meta(object):
    model = Project

forms = {
    c.Meta.model.project.property.back_populates: ModelFormField(c)
    for c in config_forms}

for ufield in forms.values():
    ufield.creation_counter += 10000

forms.update({'Meta': Meta})
ProjectForm = type('ProjectForm', (ModelForm,), forms)


@url(r'/project/list')
class ProjectList(Route):
    def get(self):
        self.render(
            'project/list.html', projects=self.db.query(Project).all())


@url(r'/project/view/(\d+)')
class ProjectView(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
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
            for hook in config_hooks:
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


@url(r'/project/edit/(\d+)')
class ProjectEdit(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        self.render(
            'form.html', form=ProjectForm(obj=project),
            render_form_recursively=self.render_form_recursively)

    def post(self, id):
        project = self.db.query(Project).get(id)
        form = ProjectForm(self.posted, project)
        if form.validate():
            for hook in config_hooks:
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


@url(r'/project/delete/(\d+)')
class ProjectDelete(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        self.render(
            'ask.html', message="Do you really want to delete project %s" %
            project.name)

    def post(self, id):
        project = self.db.query(Project).get(id)
        self.db.delete(project)
        secure_rmtree(
            os.path.join(server.conf['projects_realpath'], project.dir_name))
        self.db.commit()
        self.blocks.project.refresh()
        self.blocks.home.refresh()
        self.redirect(self.reverse_url('ProjectList'))


@url(r'/project/build/(\d+)')
class ProjectBuild(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        build = Build()
        build.timestamp = datetime.now()
        build.build_id = (
            project.last_build and project.last_build.build_id or 0) + 1
        build.status = 'PENDING'
        project.builds.append(build)

        self.db.add(build)

        self.db.commit()

        self.application.builder.add(build)

        self.redirect(self.reverse_url(
            'ProjectLog', project.project_id, build.build_id))


@url(r'/log/(\d+)/(\d+)/pipe')
class ProjectLogWebSocket(WebSocket):
    def open(self, id, idx):
        self.id = id
        self.idx = idx
        with short_transaction() as db:
            self.build = db.query(Build).get((idx, id))
            self.application.builder.log_streams['%s-%s' % (
                self.build.project_id,
                self.build.build_id
            )].append(self)

            if os.path.exists(self.build.log_file):
                with open(self.build.log_file, 'r') as f:
                    for line in f:
                        self.write_message(line)

    def on_close(self):
        self.application.builder.log_streams[
            '%s-%s' % (self.id, self.idx)].remove(self)


@url(r'/project/log/(\d+)/(\d+)')
@url(r'/project/log/(\d+)', suffix='Last')
class ProjectLog(Route):
    def get(self, id, idx=None):
        project = self.db.query(Project).get(id)
        if idx:
            build = self.db.query(Build).get((idx, id))
        else:
            build = project.last_build
        if build.status != 'RUNNING' and os.path.exists(build.log_file):
            with open(build.log_file, 'r') as f:
                log = f.read()
        else:
            log = None
        self.render(
            'project/log.html', project=project, build=build, log=log)


@url(r'/project/build/(\d+)/(\d+)/stop')
class ProjectBuildStop(Route):
    def get(self, id, idx):
        build = self.db.query(Build).get((idx, id))
        self.application.builder.stop(build)

        self.redirect(self.reverse_url(
            'ProjectLog', build.project_id, build.build_id))


@url(r'/project/chart/time/(\d+).svg')
@url(r'/project/chart/time/(\d+)_(\d+)_(\d+).svg', suffix='Size')
class ProjectChartTime(Route):
    def get(self, id, width=None, height=None):
        project = self.db.query(Project).get(id)
        config = graph_config(width, height)
        config.style = ymci_style
        svg = pygal.Line(config)
        builds = project.builds.filter(Build.status == 'SUCCESS').all()[::-1]
        svg.add('Success', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.duration} for b in builds])
        if width and height:
            svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.value_formatter = lambda x: '%.2fs' % (x or 0)
        svg.interpolate = 'cubic'
        svg.show_legend = False
        svg.title = 'Build duration in seconds'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())
