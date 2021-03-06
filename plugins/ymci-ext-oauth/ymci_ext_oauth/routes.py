from ymci.ext.routes import url, Route
from tornado.auth import GoogleOAuth2Mixin
from tornado.gen import coroutine
from tornado.escape import json_encode, json_decode
from tornado.web import HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options
from ymci import server


@url(r'/_oauth2callback')
class GoogleOAuth2LoginHandler(Route, GoogleOAuth2Mixin):
    google_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'

    @property
    def oauth_url(self):
        return '%s/_oauth2callback' % options.external_url

    @coroutine
    def get(self):
        if self.application.settings.get('debug', False):
            referer = self.request.headers.get('Referer', '/')
            self.set_secure_cookie('user', json_encode('debug'))
            self.set_flash_message('success', 'Debug login successful')
            return self.redirect(referer)

        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(
                redirect_uri=self.oauth_url,
                code=self.get_argument('code'))
            self.log.debug('Got user %s' % user)
            if not user and 'token' not in user:
                self.clear_all_cookies()
                self.set_flash_message('danger', 'Unknown user')
                raise HTTPError(403)

            if not self.settings['google_oauth'].get('domain', ''):
                self.set_secure_cookie('user', json_encode(user))
                self.set_flash_message('success', 'Login successful')
                return self.redirect('/')

            access_token = str(user['access_token'])
            response = yield AsyncHTTPClient().fetch(
                self.google_info_url,
                headers={
                    'Authorization': 'Bearer %s' % access_token
                })

            self.log.debug('Got userinfo %s' % response.body)
            if response.code != 200:
                self.set_flash_message('danger', 'Error contacting oauth api')
                raise HTTPError(403)

            body = json_decode(response.body)
            email = body['email']
            if not email.endswith(
                    '@%s' % self.settings['google_oauth']['domain']):
                self.set_flash_message(
                    'danger', '%s is not in domain %s' % (
                        email, self.settings['google_oauth']['domain']))
                raise HTTPError(403)

            self.set_secure_cookie('user', email, expires_days=1)
            self.set_flash_message(
                'success', 'Login successful for %s' % email)
            return self.redirect('/')

        yield self.authorize_redirect(
            redirect_uri=self.oauth_url,
            client_id=self.settings['google_oauth']['key'],
            scope=['profile', 'email'],
            response_type='code',
            extra_params={
                'approval_prompt': 'auto'
            })


@url(r'/google_auth/logout')
class GoogleOAuth2Logout(Route):
    def get(self):
        self.clear_cookie("user")
        self.set_flash_message('success', 'Logout successful')
        self.redirect("/")


server.components.project_unauth.login = {
    'route': 'GoogleOAuth2LoginHandler',
    'label': 'Login'
}

server.components.project_auth.logout = {
    'route': 'GoogleOAuth2Logout',
    'label': 'Logout'
}
