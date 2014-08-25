#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ymci - You Modern Continous Integration server
# Copyright © 2014 Florian Mounier, Kozea


from tornado.options import options
from tornado_systemd import SystemdHTTPServer
from ymci import server, ioloop
from logging import getLogger

log = getLogger('ymci')
log.setLevel(10 if options.debug else 30)

if options.debug:
    from wdb.ext import wdb_tornado
    wdb_tornado(server, start_disabled=True)

http_server = SystemdHTTPServer(server)

log.debug('Listening')
http_server.listen(options.port)

ioloop.start()
