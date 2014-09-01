from ymci.ext.hooks import BuildHook
from logging import getLogger
import os

log = getLogger('ymci')


class GitHook(BuildHook):

    @property
    def active(self):
        return self.build.project.repository.endswith('.git')

    def pre_copy(self):
        if not os.path.exists(
                os.path.join(self.build.project.src_dir, '.git')):
            self.execute(
                ['git', 'clone', self.build.project.repository, '.'])

        self.execute(['git', 'fetch', 'origin'])
        self.execute(
            ['git', 'reset', '--hard', 'origin/master'])
