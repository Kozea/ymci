from .. import url, Route, server
from ..utils.db import upgrade


@url(r'/admin')
class Admin(Route):
    def get(self):
        self.render('admin/index.html')

    def post(self):
        upgrade()
        self.redirect(self.reverse_url('Admin'))


@url(r'/admin/db_upgrade')
class AdminDBUpgrade(Route):
    def get(self):
        upgrade()
        self.redirect(self.reverse_url('Admin'))


@url(r'/admin/plugin_refresh')
class AdminPluginRefresh(Route):
    def get(self):
        self.application.plugins.reload()
        self.application.components.blocks.plugins.refresh()
        self.redirect(self.reverse_url('Admin'))


server.components.project_auth.admin = {
    'route': 'Admin',
    'label': 'Admin'
}
