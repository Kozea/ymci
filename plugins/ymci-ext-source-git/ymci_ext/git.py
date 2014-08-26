from tornado import gen
from ymci.ext.hooks import BuildHook
from logging import getLogger
import os

log = getLogger('ymci')


class GitHook(BuildHook):

    @property
    def active(self):
        return self.project.repository.endswith('.git')

    @gen.coroutine
    def pre_copy(self):
        log.info('Starting git pre copy')
        if not os.path.exists(os.path.join(self.project.src_dir, '.git')):
            log.info('No .git running git clone')
            yield gen.Task(
                self.execute,
                ['git', 'clone', self.project.repository, '.'])
        else:
            log.info('.git found running git fetch')
            yield gen.Task(
                self.execute,
                ['git', 'fetch', 'origin'])

            log.info('.git found running git reset')
            yield gen.Task(
                self.execute,
                ['git', 'reset', '--hard', 'origin/master'])
        log.info('Git pre_copy done')
