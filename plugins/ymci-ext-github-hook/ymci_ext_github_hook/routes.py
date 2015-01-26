from ymci.ext.routes import url, Route
from ymci.model import Project, Build
from datetime import datetime
import json


@url(r'/github/hook')
class GithubHook(Route):
    def get(self):
        self.write('GET OK')

    def post(self):
        hook = json.loads(self.request.body.decode('utf-8'))
        if not hook['repository']:
            self.write('VOID POST OK')
            return
        repos = [
            hook['repository'].get('url'),
            hook['repository'].get('ssh_url'),
            hook['repository'].get('svn_url'),
            hook['repository'].get('git_url'),
            hook['repository'].get('clone_url')
        ]
        builds = []

        projects = self.db.query(Project).all()
        for project in projects:
            if project.repository.startswith('git+'):
                repo = project.repository[4:]
                branch = hook['repository'].get('default_branch', 'master')
                if '!' in repo:
                    repo, branch = repo.split('!')
            else:
                continue

            if repo and repo in repos:
                if hook['ref'] == 'refs/heads/%s' % branch:
                    build = Build()
                    build.timestamp = datetime.now()
                    build.build_id = (
                        project.last_build and
                        project.last_build.build_id or 0) + 1
                    build.status = 'PENDING'
                    project.builds.append(build)

                    self.db.add(build)
                    builds.append(build)

        self.db.commit()

        for build in builds:
            self.application.builder.add(build)

        self.write('POST OK')
