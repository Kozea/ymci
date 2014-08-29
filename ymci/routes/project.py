from .. import url, Route, WebSocket
from wtforms_alchemy import ModelForm
from ..model import Project, Build
from datetime import datetime
import os


class ProjectForm(ModelForm):
    class Meta(object):
        model = Project


@url(r'/project/list')
class ProjectList(Route):
    def get(self):
        return self.render(
            'project/list.html', projects=self.db.query(Project).all())


@url(r'/project/view/(\d+)')
class ProjectView(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        return self.render('project/view.html', project=project)


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
            return self.redirect('/')
        return self.render('form.html', form=form)


@url(r'/project/edit/(\d+)')
class ProjectEdit(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        return self.render(
            'form.html', form=ProjectForm(obj=project))

    def post(self, id):
        project = self.db.query(Project).get(id)
        form = ProjectForm(self.posted, project)
        if form.validate():
            form.populate_obj(project)
            self.db.commit()
            return self.redirect('/')
        return self.render('form.html', form=form)


@url(r'/project/delete/(\d+)')
class ProjectDelete(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        return self.render(
            'ask.html', message="Do you really want to delete project %s" %
            project.name)

    def post(self, id):
        project = self.db.query(Project).get(id)
        self.db.remove(project)
        self.db.commit()
        return self.redirect('/')


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

        return self.redirect(self.reverse_url(
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
        return self.render('project/log.html', project=project, build=build)


@url(r'/project/build/(\d+)/(\d+)/stop')
class ProjectBuildStop(Route):
    def get(self, id, idx):
        build = self.db.query(Build).get((idx, id))
        self.application.builder.stop(build)

        return self.redirect(self.reverse_url(
            'ProjectLog', build.project_id, build.build_id))
