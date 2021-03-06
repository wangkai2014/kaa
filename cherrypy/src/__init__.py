# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# __init__py - Interface to kaa.cherrypy
# -----------------------------------------------------------------------------
# $Id$
#
# This module define the expose decorator. The idea is copied from TurboGears.
# The expose function adds a template (Kid) and it is possible to execute the
# function from the main thread.
#
# -----------------------------------------------------------------------------
# kaa.cherrypy - Web Framework for Kaa based on CherryPy
# Copyright (C) 2006-2008 Dirk Meyer
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version
# 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA
#
# -----------------------------------------------------------------------------

# system cherrypy installation
import cherrypy
if int(cherrypy.__version__.split('.')[0]) < 3:
    msg = 'CherryPy >= 3.0.0 required, %s found' % cherrypy.__version__
    raise ImportError(msg)

# Import everything from cherrypy into kaa.cherrypy namespace, so its
# APIs are conveniently accessible.
from cherrypy import *

# kaa imports
import kaa

# kaa.cherrypy imports
from version import VERSION
from controller import expose, Template, template, thread_template, set_default_engine


def mount(root, path, config = None):
    """
    Binds the given root (which is an object containing methods decorated with
    exposed) to the path.  Optional config can be specified for this path.
    Config is a dict of dicts.
    """
    cherrypy.tree.mount(root, path, config)


def start(config = None):
    """
    Start cherrypy server.
    """
    def _stop():
        cherrypy.server.stop()
        cherrypy.engine.stop()
    if config:
        cherrypy.config.update(config)
    cherrypy.server.quickstart()
    cherrypy.engine.SIGHUP = cherrypy.engine.SIGTERM = None
    cherrypy.engine.start(blocking=False)
    kaa.main.signals['shutdown'].connect(_stop)
