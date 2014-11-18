import os
import smtplib
import logging
from email.mime.text import MIMEText
from ymci import server
from ymci.model import Build
from ymci.ext.hooks import BuildHook
from .utils import MailGenerator
from tornado.options import options

cur_dir = os.path.dirname(__file__)
log = logging.getLogger('ymci')


class MailHook(BuildHook):
    """Defines hooks for mail actions."""
    @property
    def active(self):
        return server.conf.get('mail_alert', None)

    def __init__(self, build, out):
        self.conf = server.conf.get('mail_alert')
        self.smtp = self.conf.get('server', None)
        self.port = self.conf.get('port', smtplib.SMTP_PORT)
        self.port = int(self.port)
        self.from_ = self.conf.get('From', None)
        self.to = self.conf.get('To', None)
        self.login = self.conf.get('credentials', {}).get('login', None)
        self.password = self.conf.get('credentials', {}).get('password', None)
        self.key = self.conf.get('credentials', {}).get('key', None)
        self.cert = self.conf.get('credentials', {}).get('cert', None)
        super().__init__(build, out)

    def send_mail(self, subject, message, to=None):
        to = to or self.to
        self.out('Sending mail to %s' % to)
        smtp = smtplib.SMTP(self.smtp, self.port)

        message['Subject'] = subject
        message['From'] = self.from_
        message['To'] = to

        smtp.ehlo()
        if smtp.has_extn('STARTTLS'):
            smtp.starttls(self.key, self.cert)
            smtp.ehlo()
            if self.login and self.password:
                smtp.login(self.login, self.password)

        smtp.send_message(message)
        smtp.quit()

    def render_mail(self, path, **kwargs):
        generator = MailGenerator()
        message = MIMEText(generator.gen_template(path, **kwargs), 'html')
        return message

    def post_build(self):
        if self.build.status not in ('FAILED', 'BROKEN'):
            return
        if self.build.build_id > 1:
            previous_build = self.build._sa_instance_state.session.query(
                Build).get((
                    self.build.build_id - 1, self.build.project_id))
        else:
            previous_build = None
        if previous_build and previous_build.status == self.build.status:
            return

        log_url = '%s%s' % (
            options.external_url,
            server.reverse_url(
                'ProjectLog',
                self.build.project.project_id,
                self.build.build_id))
        try:
            self.send_mail(
                'YMCI build #%d is %s for project %s' % (
                    self.build.build_id,
                    self.build.status.lower(),
                    self.build.project.name),
                self.render_mail('mails/error.txt',
                                 build=self.build, log_url=log_url),
                getattr(self.build, '_author', None))
        except Exception:
            log.exception('Error on mail send')
