from ymci import url, config, Route, WebSocket, MultiDict, ioloop
from ymci.tools import build, get_log_file
from wtforms import Form, StringField, TextAreaField, validators
from time import time


class ProjectForm(Form):
    name = StringField('Name', [validators.Required()])
    description = TextAreaField('Description')
    build_script = TextAreaField('Build script')


@url(r'/project/view/([^/]+)')
class ProjectView(Route):
    def get(self, id):
        return self.render('project/view.html', id=id)


@url(r'/project/add')
class ProjectAdd(Route):
    def get(self):
        return self.render('form.html', form=ProjectForm())

    def post(self):
        form = ProjectForm(self.posted)
        if form.validate():
            id = form.name.data.replace(' ', '-')
            config['projects'][id] = form.data
            config._sync()
            return self.redirect('/')
        return self.render('form.html', form=form)


@url(r'/project/edit/([^/]+)')
class ProjectEdit(Route):
    def get(self, id):
        return self.render(
            'form.html', form=ProjectForm(MultiDict(config['projects'][id])))

    def post(self, id):
        form = ProjectForm(self.posted, config['projects'][id])
        if form.validate():
            config['projects'][id] = form.data
            config._sync()
            return self.redirect('/')
        return self.render('form.html', form=form)


@url(r'/project/delete/([^/]+)')
class ProjectDelete(Route):
    def get(self, id):
        return self.render(
            'ask.html', message="Do you really want to delete project %s" %
            config['projects'][id]['name'])

    def post(self, id):
        config['projects'].pop(id)
        config._sync()
        return self.redirect('/')


@url(r'/project/build/([^/]+)')
class ProjectBuild(Route):
    def get(self, id):
        idx = config['projects'][id]['build_number'] = config[
            'projects'][id].get('build_number', 0) + 1
        config._sync()
        build(id, idx)
        return self.redirect(self.reverse_url('ProjectLog', id, idx))


@url(r'/log/([^/]+)/(\d*)/pipe')
class ProjectLogWebsocket(WebSocket):
    def open(self, id, idx):
        self.file = open(get_log_file(id, int(idx)), 'r')
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
        if idx:
            idx = int(idx)
        else:
            idx = config['projects'][id].get('build_number', 0)

        if idx > config['projects'][id].get('build_number', -1):
            self.abort(404)
        else:
            return self.render('project/log.html', id=id, idx=idx)
