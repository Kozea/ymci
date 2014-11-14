from tornado.web import HTTPError
from ymci.ext.hooks import PrepareHook
from ymci.model import Project, Build
from ymci import server


oauth = server.conf.get('google_oauth')
if oauth:
    server.settings['google_oauth'] = oauth


class OAuthHook(PrepareHook):
    @property
    def active(self):
        return oauth

    def prepare(self, route):
        name = route.__class__.__name__
        current_user = route.get_secure_cookie("user")
        if current_user or not name.startswith('Project') or name in (
                'ProjectList',
        ):
            return
        if not current_user and name == 'ProjectAdd':
            return route.redirect(
                route.reverse_url('GoogleOAuth2LoginHandler'))

        project = None
        if 'project_id' in route.path_kwargs:
            project = self.db.query(Project).get(
                route.path_kwargs['project_id'])
        # if 'build_id' in route.path_kwargs:
        #     project = self.db.query(Build).get(
        #         route.path_kwargs['build_id']).project

        if not project:
            return

        if getattr(project.oauth_config, 'public_read', False) and name in (
                'ProjectView', 'ProjectLog', 'ProjectBuildLog'
        ):
            return

        if getattr(project.oauth_config, 'public_build', False) and name in (
                'ProjectBuild', 'ProjectBuildStop'
        ):
            return

        return route.redirect(
            route.reverse_url('GoogleOAuth2LoginHandler'))
