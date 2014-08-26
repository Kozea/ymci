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
        if not os.path.exists(os.path.join(self.project.src_dir, '.git')):
            yield self.execute(
                ['git', 'clone', self.project.repository, '.'])
        else:
            yield self.execute(
                ['git', 'fetch', 'origin'])

            yield self.execute(
                ['git', 'reset', '--hard', 'origin/master'])
