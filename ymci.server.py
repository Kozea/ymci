#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ymci - You Modern Continuous Integration server
# Copyright © 2014 Florian Mounier, Kozea


from tornado.options import options
from tornado_systemd import SystemdHTTPServer
from ymci import server, ioloop
from ymci.utils.db import upgrade
from logging import getLogger
import sys

log = getLogger('ymci')
log.setLevel(10 if options.debug else 20)

if options.upgrade:
    upgrade()
    sys.exit(0)


if options.debug:
    from wdb.ext import wdb_tornado
    wdb_tornado(server, start_disabled=True)

http_server = SystemdHTTPServer(server, ssl_options={
    'certfile': '/etc/butterfly/ssl/butterfly_ca.crt',
    'keyfile': '/etc/butterfly/ssl/butterfly_ca.key',
})

log.debug('Listening')
http_server.listen(options.port)

ioloop.start()
