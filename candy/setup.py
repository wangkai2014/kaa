# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# setup.py - Setup script for kaa.candy
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa-candy - Third generation Canvas System using Clutter as backend
# Copyright (C) 2008 Dirk Meyer, Jason Tackaberry
#
# First Version: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

# python imports
import sys
import os
import sys
import stat
try:
    # kaa base imports
    from kaa.distribution.core import Extension, setup
    import kaa.utils
except ImportError:
    print 'kaa.base not installed'
    sys.exit(1)

if len(sys.argv) == 2 and sys.argv[1] == 'clean':
    for file in ('build', 'dist', 'src/version.py', 'MANIFEST',
                 'src/backend/gen_libcandy.c', 'doc/html'):
        if os.path.isdir(file):
            print 'removing %s' % file
            os.system('rm -rf %s' % file)
        if os.path.isfile(file):
            print 'removing %s' % file
            os.unlink(file)
    sys.exit(0)

libcandy_modules = [ 'clutter-reflect-texture' ]

# add /usr/local/lib/pkgconfig because this is where clutter installs
# as default and it may not be in your path
pkgconfig = '/usr/local/lib/pkgconfig'
if os.environ.get('PKG_CONFIG_PATH'):
    pkgconfig += ':' + os.environ.get('PKG_CONFIG_PATH')
os.environ['PKG_CONFIG_PATH'] = pkgconfig

# create libcandy extension, gen_libcandy.c may not exist yet
files = [ 'src/backend/%s.c' % m for m in libcandy_modules ]
files.extend(['src/backend/gen_libcandy.c', 'src/backend/libcandymodule.c'])
libcandy = Extension('kaa/candy/backend/libcandy', files)

# check dependencies
if not libcandy.check_library('clutter-1.0', '1.0.4'):
    print 'clutter-1.0 >= 1.0.4 not found'
    sys.exit(1)
if not libcandy.check_library('pygobject-2.0', '2.16.0'):
    print 'pygobject >= 2.16.0 not found'
    sys.exit(1)

# check for pygobject-codegen to generate python bindings
# should be part of pygobject
pygobject_codegen = kaa.utils.which('pygobject-codegen-2.0')
if not pygobject_codegen:
    print 'pygobject-codegen-2.0 not found, should be part of pygobject'
    sys.exit(1)

# check for pyclutter defs for pygobject-codegen
for version in ('0.9', '1.0'):
    clutter_defs = os.popen('pkg-config pyclutter-%s --variable=defsdir' % version).read().strip()
    if clutter_defs:
        break
else:
    print 'pyclutter-0.9 not found'
    sys.exit(1)
# ok, add defs file to the path
clutter_defs += '/clutter-base-types.defs'

# now check if we need to build the wrapper code file
# Note: the defs file was created by
# python /usr/lib/python2.6/site-packages/gtk-2.0/codegen/h2def.py clutter-reflect-texture.h
# This it may be needed in the future to edit this file manually it is
# in svn and not generated on the fly
gen_stat = 0
if os.path.isfile('src/backend/gen_libcandy.c'):
    gen_stat = os.stat('src/backend/gen_libcandy.c')[stat.ST_MTIME]
for m in libcandy_modules:
    if os.stat('src/backend/%s.h' % m)[stat.ST_MTIME] > gen_stat:
        print 'creating python wrapper file'
        os.system(
            '%s -I src/backend/libcandy --py_ssize_t-clean --prefix libcandy ' \
            '--register %s --override src/backend/libcandy.override ' \
            'src/backend/libcandy.defs > src/backend/gen_libcandy.c' \
            % (pygobject_codegen,clutter_defs))
        break

# now trigger the python magic
setup(
    module = 'candy',
    version = '0.0.9',
    license = 'LGPL',
    summary = 'Third generation Canvas System using Clutter as backend.',
    ext_modules  = [ libcandy ],
    namespace_packages = ['kaa']
)
