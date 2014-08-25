from ymci import url, Route
from ymci.model import Project


@url(r'/')
class Index(Route):
    def get(self):
        return self.render(
            'index.html', projects=self.db.query(Project).all())


import ymci.routes.project
