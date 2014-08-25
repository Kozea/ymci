from ymci import url, Route, WebSocket, ioloop, builder
from ymci.builder import Task
from wtforms_alchemy import ModelForm
from ymci.model import Project, Build
from datetime import datetime
from collections import defaultdict
from time import time


class ProjectForm(ModelForm):
    class Meta(object):
        model = Project


@url(r'/project/view/([^/]+)')
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


@url(r'/project/edit/([^/]+)')
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


@url(r'/project/delete/([^/]+)')
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


@url(r'/project/build/([^/]+)')
class ProjectBuild(Route):
    def get(self, id):
        project = self.db.query(Project).get(id)
        build = Build()
        build.timestamp = datetime.now()
        build.build_id = project.last_build + 1
        build.status = 'PENDING'
        project.builds.append(build)

        self.db.add(build)
        self.db.commit()

        builder.add(Task(project, build, ProjectLogWebSocket.log_clients[
            '%s-%s' % (
                project.project_id,
                build.build_id
            )]))

        return self.redirect(self.reverse_url(
            'ProjectLog', project.project_id, build.build_id))


@url(r'/log/([^/]+)/(\d*)/pipe')
class ProjectLogWebSocket(WebSocket):

    log_clients = defaultdict(list)

    def open(self, id, idx):
        self.project = self.db.query(Project).get(id)
        self.build = self.db.query(Build).get((idx, id))
        ProjectLogWebSocket.log_clients['%s-%s' % (
            self.project.project_id,
            self.build.build_id
        )].append(self)

        with open(self.build.log_file, 'r') as f:
            self.write_message(f.read())

    def on_close(self):
        ProjectLogWebSocket.log_clients['%s-%s' % (
            self.project.project_id,
            self.build.build_id
        )].remove(self)


@url(r'/project/log/([^/]+)/(\d*)')
class ProjectLog(Route):
    def get(self, id, idx):
        project = self.db.query(Project).get(id)
        build = self.db.query(Build).get((idx or project.last_build, id))
        return self.render('project/log.html', project=project, build=build)
