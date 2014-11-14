from .. import url, Route
from ..model import User
from wtforms.form import Form
from wtforms.fields import StringField, PasswordField
from wtforms.validators import InputRequired
from tornado.escape import json_encode
from simplepam import authenticate
import datetime


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
        service = self.read_pam_config()
        check = authenticate(form.login.data, form.password.data, service)
        if check:
            user = (self.db.query(User)
                    .filter(User.login == form.login.data)
                    .first())

            if not user:
                user = User(login=form.login.data)
                self.db.add(user)
                self.db.commit()

            self.set_current_user(user.login)
            self.set_flash_message('success', 'Connection successful')
            user.login_count = (user.login_count or 0) + 1
            user.last_login = datetime.datetime.now()
            self.db.commit()
            return self.redirect(self.get_argument("next", "/"))

        self.set_flash_message('danger', 'User/Password do not match')
        self.redirect(self.reverse_url('AuthLogin'))

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", json_encode(user))
        else:
            self.clear_cookie("user")

    def read_pam_config(self):
        return self.application.conf.get('pam_service', 'login')


@url(r'/auth/logout')
class AuthLogout(Route):
    def get(self):
        self.clear_cookie("user")
        self.set_flash_message('success', 'Logout successful')
        self.redirect("/")
