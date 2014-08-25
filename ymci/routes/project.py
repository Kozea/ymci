from ymci import url, Route, WebSocket, ioloop, builder
from ymci.tools import Task
from wtforms_alchemy import ModelForm
from ymci.model import Project, Build
from datetime import datetime
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

        builder.add(Task(project, build))

        return self.redirect(self.reverse_url(
            'ProjectLog', project.project_id, build.build_id))


@url(r'/log/([^/]+)/(\d*)/pipe')
class ProjectLogWebsocket(WebSocket):
    def open(self, id, idx):
        # project = self.db.query(Project).get(id)
        build = self.db.query(Build).get((idx, id))

        self.file = open(build.log_file, 'r')
        self.write_message(self.file.read())
        self.timeout_hdl = ioloop.add_timeout(time(), self.read)

    def read(self):
        data = self.file.read()
        if data:
            self.write_message(data)
        self.timeout_hdl = ioloop.add_timeout(time() + .001, self.read)

    def on_close(self):
        ioloop.remove_timeout(self.timeout_hdl)
        self.file.close()


@url(r'/project/log/([^/]+)/(\d*)')
class ProjectLog(Route):
    def get(self, id, idx):
        project = self.db.query(Project).get(id)
        build = self.db.query(Build).get((idx or project.last_build, id))
        return self.render('project/log.html', project=project, build=build)
