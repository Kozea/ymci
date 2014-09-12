import os
from tornado import template
from tornado.escape import xhtml_escape, to_unicode

cur_dir = os.path.dirname(__file__)


class MailGenerator():
    """Handles mail rendering."""

    def gen_template(self, filename, **kwargs):
        html = ''
        with open(os.path.join(cur_dir, filename), 'r') as fd:
            html = fd.read()
        t = template.Template(html)
        return to_unicode(xhtml_escape(t.generate(**kwargs)))
