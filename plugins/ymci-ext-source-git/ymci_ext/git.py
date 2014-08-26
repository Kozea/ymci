from ymci.ext.hooks import BuildHook
import os


class GitHook(BuildHook):

    @property
    def active(self):
        return self.project.repository.endswith('.git')

    def pre_copy(self):
        if not os.path.exists(os.path.join(self.project.src_dir, '.git')):
            self.execute(
                ['git', 'clone', self.project.repository, '.'])
        else:
            self.execute(['git', 'fetch', 'origin'])
            self.execute(['git', 'reset', '--hard', 'origin/master'])
