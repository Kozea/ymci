import os
import smtplib
import yaml
import logging
from email.mime.text import MIMEText
from ymci import server
from ymci.ext.hooks import BuildHook
from .utils import MailGenerator

cur_dir = os.path.dirname(__file__)
log = logging.getLogger('ymci')


class Mail(object):
    """Handles mails in plain text type."""
    auth = False

    def __init__(self):
        self.read_config()
        config = server.conf['mails']

        self.smtp = config.get('server', None)
        self.port = config.get('port', None)
        if self.port:
            self.port = int(self.port)
        self._from = config.get('From', None)
        self.to = config.get('To', None)

        if config.get('credentials', None):
            self.login = config['credentials']['login']
            self.password = config['credentials']['password']
            self.auth = True

        self.__smtp_server = None

    @property
    def smtp_server(self):
        self.__smtp_server = (
            self.__smtp_server or smtplib.SMTP(self.smtp, self.port))
        return self.__smtp_server

    def quit(self):
        if self.__smtp_server:
            self.__smtp_server.quit()

    def send_mail(self, message, mtype):
        message = self.set_mail_headers(message, mtype)
        try:
            self.authenticate()
            self.smtp_server.send_message(message)
        except Exception:
            log.exception("Mail error")
        finally:
            try:
                self.quit()
            except Exception:
                log.exception("Quit error")

    def set_mail_headers(self, message, mtype):
        message['Subject'] = mtype
        message['From'] = self._from
        message['To'] = self.to
        return message

    def authenticate(self):
        self.smtp_server.ehlo()

        if self.smtp_server.has_extn('STARTTLS'):
            self.smtp_server.starttls()
            self.smtp_server.ehlo()

        if self.auth and self.login and self.password:
            self.smtp_server.login(self.login, self.password)

    def read_config(self):
        with open(os.path.join(cur_dir, 'config.yaml')) as fd:
            try:
                server.conf.update(yaml.load(fd))
            except Exception:
                log.exception('Error reading mail configuration.')
                return False
            return True


class MailHook(BuildHook):
    """Defines hooks for mail actions."""

    @property
    def active(self):
        return server.conf.get('mails', None)

    def post_build(self):
        if not self.build.status == 'FAILED':
            return
        mailer = Mail()
        message = self.read_mail('mails/error.txt')
        mailer.send_mail(message=message, mtype='error')

    def read_mail(self, path):
        generator = MailGenerator()
        message = MIMEText(generator.gen_template(
            path, build=self.build, project=self.build.project), 'html')
        return message
