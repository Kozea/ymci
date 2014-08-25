# -*- coding: utf-8 -*-
#
# ymci - You Modern Continous Integration server
# Copyright © 2014 Florian Mounier, Kozea

from tornado.web import (
    Application, RequestHandler, url as tornado_url, HTTPError)
from sqlalchemy.orm import scoped_session, sessionmaker
from tornado.websocket import WebSocketHandler
from tornado.options import define, parse_command_line, options
from tornado.ioloop import IOLoop
from logging import getLogger
from ymci.builder import Builder
from ymci.model import engine, Query
from ymci.model.config import Config
import os.path

__version__ = '0.0.1'

log = getLogger('ymci')


define("debug", default=False, help="Debug mode")
define("host", default='ymci.l', help="Server host")
define("port", default=7361, help="Server port")
define("config", default='ymci.yaml', help="YMCI config file")
define("secret", default='secret', help="Secret key for cookies")

parse_command_line()
config = Config(options.config)
ioloop = IOLoop.instance()


server = Application(
    debug=options.debug,
    cookie_secret=options.secret,
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates"))

server.db = scoped_session(sessionmaker(bind=engine, query_cls=Query))
builder = Builder(server.db)


class url(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, cls):
        server.add_handlers(
            r'.*$',
            (tornado_url(self.url, cls, name=cls.__name__),)
        )
        return cls


class MultiDict(dict):
    def getlist(self, attr):
        return [v.decode('utf-8') if isinstance(v, bytes) else v
                for v in (self[attr] if isinstance(self[attr], list)
                else [self[attr]])]


class Base(object):
    @property
    def log(self):
        return log

    def abort(self, code):
        raise HTTPError(code)

    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        return self.application.db.remove()


class Route(RequestHandler, Base):
    @property
    def posted(self):
        return MultiDict(self.request.arguments)


class WebSocket(WebSocketHandler, Base):
    pass


import ymci.routes
