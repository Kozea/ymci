from .. import url, BlockWebSocket, server
from ..model import Project, Build
from time import time


@url(r'/blocks/build')
class BuildBlock(BlockWebSocket):
    def render_block(self):
        builder = server.builder
        builds = []
        for task in builder.tasks:
            build = self.db.query(Build).get(
                (task.build_id,
                 task.project_id))
            if task.start_time:
                now = time() - task.start_time
            else:
                now = None
            builds.append((now, build))

        free_slots = builder.limit - len(builder.tasks)
        return self.render_string(
            'blocks/build.html', current_builds=builds, free_slots=free_slots)


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


@url(r'/blocks/home')
class HomeBlock(BlockWebSocket):
    def render_block(self):
        return self.render_string(
            'blocks/home.html',
            projects=self.db.query(Project).all())


@url(r'/blocks/plugins')
class PluginBlock(BlockWebSocket):
    def render_block(self):
        plugins = server.plugins['ymci.ext']
        return self.render_string('blocks/plugins.html', plugins=plugins)


blocks = server.components.blocks
blocks.build = BuildBlock
blocks.project = ProjectBlock
blocks.home = HomeBlock
blocks.history = HistoryBlock
blocks.plugins = PluginBlock
