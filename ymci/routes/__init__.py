from ymci import url, Route


@url(r'/')
class Index(Route):
    def get(self):
        return self.render('index.html')


import ymci.routes.project
