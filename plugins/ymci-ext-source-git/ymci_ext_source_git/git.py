from ymci.ext.hooks import BuildHook
from logging import getLogger
import os

log = getLogger('ymci')


class GitHook(BuildHook):

    @property
    def active(self):
        return self.build.project.repository.startswith('git+')

    def pre_copy(self):
        repo = self.build.project.repository[4:]
        branch = 'master'
        if '!' in repo:
            repo, branch = repo.split('!')
        if not os.path.exists(
                os.path.join(self.build.project.src_dir, '.git')):
            self.execute(
                ['git', 'clone', repo, '.'])

        self.execute(['git', 'fetch', 'origin'])
        self.execute(
            ['git', 'reset', '--hard', 'origin/%s' % branch])
