from ymci import url, config, Route, MultiDict
from wtforms import Form, StringField, TextAreaField, validators


class Project(Form):
    name = StringField('Name', [validators.Required()])
    description = TextAreaField('Description')


@url(r'/')
class Index(Route):
    def get(self):
        return self.render('index.html')


@url(r'/project/add')
class ProjectAdd(Route):
    def get(self):
        return self.render('form.html', form=Project())

    def post(self):
        form = Project(self.posted)
        if form.validate():
            id = form.name.data.replace(' ', '-')
            config['projects'][id] = form.data
            config._sync()
            return self.redirect('/')
        return self.render('form.html', form=form)


@url(r'/project/edit/(.+)')
class ProjectEdit(Route):
    def get(self, id):
        return self.render(
            'form.html', form=Project(MultiDict(config['projects'][id])))

    def post(self, id):
        form = Project(self.posted, config['projects'][id])
        if form.validate():
            config['projects'][id] = form.data
            config._sync()
            return self.redirect('/')
        return self.render('form.html', form=form)
