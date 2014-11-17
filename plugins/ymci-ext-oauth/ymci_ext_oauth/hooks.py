from tornado.web import HTTPError
from ymci.ext.hooks import PrepareHook
from ymci.model import Project
from ymci import server


oauth = server.conf.get('google_oauth')
if oauth:
    server.settings['google_oauth'] = oauth


class OAuthHook(PrepareHook):
    @property
    def active(self):
        return oauth

    def _auth(self, user, endpoint, *args, **kwargs):
        if user or not endpoint.startswith('Project') or endpoint in (
                'ProjectList',):
            return True
        if not user and endpoint == 'ProjectAdd':
            return False

        project = None
        if 'project_id' in kwargs:
            project = self.db.query(Project).get(
                kwargs['project_id'])

        if not project:
            return True

        if getattr(
                project.oauth_config, 'public_read', False) and endpoint in (
                'ProjectView', 'ProjectLog', 'ProjectBuildLog'):
            return True

        if getattr(
                project.oauth_config, 'public_build', False) and endpoint in (
                'ProjectBuild', 'ProjectBuildStop'):
            return True

        return False

    def prepare(self, route):
        self._route = route
        if self._auth(
                route.get_secure_cookie("user"),
                route.__class__.__name__,
                *route.path_args,
                **route.path_kwargs):
            return
        raise HTTPError(403)

    def auth_url(self, endpoint, *args, **kwargs):
        if not hasattr(self, '_route'):
            raise Exception(
                'Prepare must be called before using auth_reverse_url')

        return self._auth(
            self._route.get_secure_cookie('user'),
            endpoint, *args, **kwargs)
