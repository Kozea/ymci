import os
from ymci.ext.routes import url, Route
from ymci.model import Project
from ymci import server
from tornado.web import StaticFileHandler
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


@url(r'/project/browse/(\d+)/(.*)')
class Browse(Route):
    def get_tree_dict(self, directory, path):
        tree_dict = {}
        base, prefix = os.path.split(directory)

        for dir, dirs, files in os.walk(directory):
            dir = dir.replace(base + '/', '')
            parts = dir.split(os.path.sep)
            dct = tree_dict
            for part in parts[1:]:
                dct = dct['dirs'][part]

            dct['name'] = (dir.replace(prefix + '/', '')
                           if dir != prefix else '')
            dct['active'] = path.startswith(dct['name'] + '/')
            dct['dirs'] = {dir_: {} for dir_ in dirs}
            dct['files'] = {file: os.path.join(dct['name'], file) == path
                            for file in files}

        return tree_dict

    def recurse(self, dct, id):
        out = '<ul>'
        for name, dirdct in sorted(dct['dirs'].items()):
            out += '<li class="dir">'
            out += '<input type="checkbox"%s id="node_%s" />' % (
                ' checked' if dirdct['active'] else '',
                dirdct['name'].replace('/', ':'))
            out += '<label class="dir_title" for="node_%s">' % (
                dirdct['name'].replace('/', ':'))
            out += '<i class="glyphicon"></i> %s' % name
            out += '</label>%s' % self.recurse(dirdct, id)
            out += '</li>'

        for file, active in sorted(dct['files'].items()):
            out += '<li class="file">'
            out += '<label>'
            if not active:
                out += '<a href="%s">' % self.reverse_url(
                    'Browse', id, os.path.join(dct['name'], file))
            out += '<i class="glyphicon glyphicon-file"></i>%s' % file
            if not active:
                out += '</a>'
            out += '</label>'
            out += '</li>'

        return out + '</ul>'

    def get(self, id, path):
        code = ''
        formatter = HtmlFormatter(linenos=True, cssclass='code')

        project = self.db.query(Project).get(id)
        if path and '..' not in path:
            file = os.path.join(project.src_dir, path)
            if os.path.exists(file):
                try:
                    with open(file, 'r') as f:
                        code = f.read()
                except UnicodeDecodeError:
                    code = None
                else:
                    try:
                        lexer = guess_lexer_for_filename(file, code)
                    except ClassNotFound:
                        lexer = get_lexer_by_name('text')
                    code = highlight(code, lexer, formatter)

        self.render(
            'source.html', code=code,
            tree=self.recurse(self.get_tree_dict(project.src_dir, path), id),
            project=project,
            path=path
        )


@url(r'/project/browse/raw/(\d+)/(.*)')
class BrowseRaw(Route):
    def get(self, id, path):
        project = self.db.query(Project).get(id)
        if path and '..' not in path:
            file = os.path.join(project.src_dir, path)
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    self.write(f.read())
        self.finish()


server.components.project_links.browse = Browse
