# -*- coding: utf-8 -*-
#
# ymci - You Modern Continous Integration server
# Copyright © 2014 Florian Mounier, Kozea

from tornado.web import (
    Application, RequestHandler, url as tornado_url, HTTPError)
from sqlalchemy.orm import scoped_session, sessionmaker
from tornado import gen
from tornado.websocket import WebSocketHandler
from tornado.options import define, parse_command_line, options
from tornado.ioloop import IOLoop
from collections import defaultdict
from tornado.web import StaticFileHandler
from logging import getLogger
from .config import Config
import os.path

__version__ = '0.0.1'

log = getLogger('ymci')


define("debug", default=False, help="Debug mode")
define("host", default='ymci.l', help="Server host")
define("port", default=7361, help="Server port")
define("config", default='ymci.yaml', help="YMCI config file")
define("secret", default='secret', help="Secret key for cookies")

parse_command_line()
ioloop = IOLoop.instance()


class ExtStaticFileHandler(StaticFileHandler):
    ext_path = {}

    @classmethod
    def get_absolute_path(cls, root, path):
        if path.startswith('ext'):
            key = '/'.join(path.split('/')[:2])
            path = '/'.join(path.split('/')[2:])
            root = ExtStaticFileHandler.ext_path[key]
        abspath = os.path.abspath(os.path.join(root, path))
        return abspath

    def validate_absolute_path(self, root, absolute_path):
        if self.path.startswith('ext'):
            key = '/'.join(self.path.split('/')[:2])
            root = ExtStaticFileHandler.ext_path[key]
        return super().validate_absolute_path(root, absolute_path)

server = Application(
    debug=options.debug,
    cookie_secret=options.secret,
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    static_handler_class=ExtStaticFileHandler,
    template_path=os.path.join(os.path.dirname(__file__), "templates"))

server.conf = Config(options.config)

from .model import engine, Query
server.scoped_session = scoped_session(
    sessionmaker(bind=engine, query_cls=Query))


class url(object):
    def __init__(self, url, name=None, suffix=None):
        self.url = url
        self.name = name
        self.suffix = suffix or ''

    def __call__(self, cls):
        server.add_handlers(
            r'.*$',
            (tornado_url(self.url, cls, name=self.name or (
                cls.__name__ + self.suffix)),)
        )
        return cls


class MultiDict(dict):
    def getlist(self, attr):
        return [v.decode('utf-8').replace('\r', '')
                if isinstance(v, bytes) else v
                for v in (self[attr] if isinstance(self[attr], list)
                else [self[attr]])]


class Base(object):
    def get_template_namespace(self):
        from . import utils
        namespace = super().get_template_namespace()
        namespace.update(dict(
            server=self.application,
            utils=utils
        ))
        return namespace

    @property
    def log(self):
        return log

    @property
    def blocks(self):
        return server.components.blocks


class Route(Base, RequestHandler):
    @property
    def posted(self):
        return MultiDict(self.request.arguments)

    def abort(self, code):
        raise HTTPError(code)

    @property
    def db(self):
        # Explicit creation of the request session
        if not getattr(self, '_db', None):
            # Cache it even if it's the same
            self._db = self.application.scoped_session()
        return self._db

    def on_finish(self):
        # Teardown of the current session
        return self.application.scoped_session.remove()

    def render_form_recursively(self, form):
        return self.render_string(
            'fields.html', form=form,
            render_form_recursively=self.render_form_recursively)


class WebSocket(Base, WebSocketHandler):
    pass


class Container(object):
    def __iter__(self):
        for name, attr in self.__dict__.items():
            if not name.startswith('_'):
                yield attr


class Components(object):
    def __init__(self):
        self.blocks = Container()
        self.project_charts = Container()
        self.project_links = Container()

server.components = Components()


class MetaBlock(type):
    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        if cls.__name__ != 'BlockWebSocket':
            cls._sockets = defaultdict(set)
        return cls


class BlockWebSocket(WebSocket, metaclass=MetaBlock):
    def open(self, *args):
        self.args = args
        self.__class__._sockets[self.args].add(self)
        self.render()

    @classmethod
    def refresh(cls, *args):
        args = tuple(map(str, args))
        for sock in cls._sockets[args]:
            sock.render()

    def render_block(self):
        pass

    def write_message(self, message):
        super().write_message(message)

    def render(self):
        # Scope the session in the request
        self.db = self.application.scoped_session()
        self.write_message(self.render_block(*self.args))
        self.application.scoped_session.remove()

    def on_close(self):
        self.__class__._sockets[self.args].remove(self)

from .builder import Pool
server.builder = Pool()

import ymci.routes
