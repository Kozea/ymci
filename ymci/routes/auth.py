from .. import url, Route
from ..model import User
from pbkdf2 import crypt
from wtforms.form import Form
from wtforms.fields import StringField, PasswordField
from wtforms.validators import InputRequired
from tornado.escape import json_encode
from tornado.options import options


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
        user = (self.db.query(User)
                .filter(User.login == form.login.data)
                .filter(User.password == crypt(
                    form.password.data, salt=options.secret))
                .first())

        if user:
            self.set_current_user(user.login)
            self.set_flash_message('success', 'Connection successful')
            user.login_count = (user.login_count or 0) + 1
            self.db.commit()
            return self.redirect(self.get_argument("next", "/"))

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
