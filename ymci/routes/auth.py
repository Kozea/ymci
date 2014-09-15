from .. import url, Route
from ..model import User
from ..utils.auth import check_login_credentials
from wtforms.form import Form
from wtforms.fields import StringField, PasswordField
from wtforms.validators import InputRequired
from tornado.escape import json_encode


class AuthForm(Form):
    form_name = 'Login'
    login = StringField('login', validators=[InputRequired])
    password = PasswordField('password', validators=[InputRequired])


@url(r'/auth/login')
class AuthLogin(Route):
    def get(self):
        self.render('form.html', form=AuthForm(),
                    render_form_recursively=self.render_form_recursively)

    def post(self):
        form = AuthForm(self.posted)
        user = self.db.query(User).filter_by(login=form.login.data).first()
        if not user:
            self.set_flash_message('danger', 'User/Password do not match')
            self.redirect(self.reverse_url('AuthLogin'))
        auth = check_login_credentials(user, form.password.data)
        if auth:
            self.set_current_user(user.login)
            self.set_flash_message('success', 'Connection successful')
            self.redirect(self.get_argument("next", "/"))
        else:
            self.set_flash_message('danger', 'User/Password do not match')
            self.redirect(self.reverse_url('AuthLogin'))

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", json_encode(user))
        else:
            self.clear_cookie("user")


@url(r'/auth/logout')
class AuthLogout(Route):
    def get(self):
        self.clear_cookie("user")
        self.set_flash_message('success', 'Logout successful')
        self.redirect("/")
