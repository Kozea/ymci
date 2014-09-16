#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ymci - You Modern Continous Integration server
# Copyright © 2014 Florian Mounier, Kozea


from tornado.options import options
from tornado_systemd import SystemdHTTPServer
from ymci import server, ioloop
from logging import getLogger
import sys

log = getLogger('ymci')
log.setLevel(10 if options.debug else 30)

if options.upgrade:
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, "Automatic revision", autogenerate=True)
    command.upgrade(alembic_cfg, "head")
    sys.exit(0)


if options.debug:
    from wdb.ext import wdb_tornado
    wdb_tornado(server, start_disabled=True)

http_server = SystemdHTTPServer(server)

log.debug('Listening')
http_server.listen(options.port)

ioloop.start()
