from .. import url, Route, WebSocket
from wtforms_alchemy import ModelForm
from ..model import Project, Build
from datetime import datetime
from . import ymci_style, default_config
import pygal
import os


class ProjectForm(ModelForm):
    class Meta(object):
        model = Project


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
        return self.render('form.html', form=ProjectForm())

    def post(self):
        form = ProjectForm(self.posted)
        if form.validate():
            project = Project()
            form.populate_obj(project)
            self.db.add(project)
            self.db.commit()
            self.redirect('/')
        self.render('form.html', form=form)


@url(r'/project/edit/(\d+)')
class ProjectEdit(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        self.render(
            'form.html', form=ProjectForm(obj=project))

    def post(self, id):
        project = self.db.query(Project).get(id)
        form = ProjectForm(self.posted, project)
        if form.validate():
            form.populate_obj(project)
            self.db.commit()
            self.redirect('/')
            return
        self.render('form.html', form=form)


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
        self.db.commit()
        self.redirect('/')


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
        self.build = self.db.query(Build).get((idx, id))
        self.application.builder.log_streams['%s-%s' % (
            self.build.project_id,
            self.build.build_id
        )].append(self)
        if os.path.exists(self.build.log_file):
            with open(self.build.log_file, 'r') as f:
                for line in f:
                    self.write_message(line)

    def on_close(self):
        self.application.builder.log_streams['%s-%s' % (
            self.build.project_id,
            self.build.build_id
        )].remove(self)


@url(r'/project/log/(\d+)/(\d*)')
class ProjectLog(Route):
    def get(self, id, idx):
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
class ProjectChartTime(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        config = default_config()
        config.style = ymci_style
        svg = pygal.Line(config)
        builds = project.builds.filter(Build.status == 'SUCCESS').all()[::-1]
        svg.add('Success', [{
            'xlink': self.reverse_url('ProjectLog', id, b.build_id),
            'value': b.duration} for b in builds])
        svg.x_labels = ['#%d' % b.build_id for b in builds]
        svg.show_minor_x_labels = False
        svg.value_formatter = lambda x: '%.2fs' % x
        svg.interpolate = 'cubic'
        svg.x_labels_major_count = 20
        svg.include_x_axis = True
        svg.truncate_label = 10
        svg.show_legend = False
        svg.title = 'Build duration in seconds'
        self.set_header("Content-Type", "image/svg+xml")
        self.write(svg.render())
