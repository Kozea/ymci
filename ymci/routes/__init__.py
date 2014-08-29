from .. import url, Route, BlockWebSocket, server
from ..model import Project


@url(r'/')
class Index(Route):
    def get(self):
        return self.render(
            'index.html', projects=self.db.query(Project).all())


@url(r'/blocks/build')
class BuildBlock(BlockWebSocket):
    def render_block(self):
        return self.render_string('blocks/build.html')


@url(r'/blocks/project')
class ProjectBlock(BlockWebSocket):
    def render_block(self):
        return self.render_string(
            'blocks/project.html',
            projects=self.db.query(Project).all())


@url(r'/blocks/history/([^\/]+)')
class HistoryBlock(BlockWebSocket):
    def render_block(self, id):
        return self.render_string(
            'blocks/history.html',
            project=self.db.query(Project).get(id))


server.blocks.build = BuildBlock
server.blocks.project = ProjectBlock
server.blocks.history = HistoryBlock
import ymci.routes.project
