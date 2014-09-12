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
    server = 'localhost'

    def __init__(self):
        self.read_config()
        config = server.conf['mails']

        self.smtp = config['server']
        self.port = int(config['port'])
        self._from = config['From']
        self.to = config['To']

        self.__server = None

    @property
    def server(self):
        self.__server = self.__server or smtplib.SMTP(self.smtp, self.port)
        return self.__server

    def quit(self):
        if self.__server:
            self.__server.quit()

    def send_mail(self, message, mtype):
        message = self.set_mail_headers(message, mtype)
        self.server.starttls()
        self.server.send_message(message)
        self.quit()

    def set_mail_headers(self, message, mtype):
        message['Subject'] = mtype
        message['From'] = self._from
        message['To'] = self.to
        return message

    def read_config(self):
        with open(os.path.join(cur_dir, 'config.yaml')) as fd:
            try:
                server.conf._config.update(yaml.load(fd))
            except Exception:
                log.error('Problème de lecture de la configuration des mails.')
                return False
            return True


class MailHook(BuildHook):
    """Defines hooks for mail actions."""

    @property
    def active(self):
        return True

    def on_build_failure(self):
        mailer = Mail()
        message = self.read_mail('mails/error.txt')
        mailer.send_mail(message=message, mtype='error')

    def read_mail(self, path):
        generator = MailGenerator()
        message = MIMEText(generator.gen_template(
            path, build=self.build, project=self.build.project), 'html')
        return message
