# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# setup.py - Setup script for kaa.base
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Copyright 2005-2009 Dirk Meyer, Jason Tackaberry
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

# python imports
import sys
import os
import time

# We require python 2.5 or later, so complain if that isn't satisfied.
if sys.hexversion < 0x02050000:
    print "Python 2.5 or later required."
    sys.exit(1)

# Check for an old install of kaa.base.  TODO: remove at some suitable
# time in the future.
path = os.popen("python -c 'import kaa; print kaa.__path__[0]' 2>/dev/null").readline().strip()
if path and os.path.exists(os.path.join(path, 'rpc.py')):
    print ('ERROR: detected conflicting files from a previous kaa.base version.\n\n'
           "To fix, you'll need to rm -rf the following directories:\n"
           '   1. build/\n'
           '   2. %s/\n\n'
           "Once you delete #2, you'll need to reinstall all the kaa\n"
           'sub-modules you use.') % path
    sys.exit(1)

# We have some extensions but kaa.distribution might not be installed yet.  And
# even if it is, we want to use the one in src/.
sys.path.insert(0, 'src')

# However, any installed kaa eggs will create a problem.  Because all kaa eggs
# install kaa/__init__.py stubs that declare the kaa namespace _and_ import
# kaa.base, some other install of kaa.base could end up getting imported as
# soon as distribution.core imports setuptools (because importing setuptools
# implicitly imports all declared namespace packages).  So here we remove any
# such installed kaa eggs that might cause some other kaa.base to take precedence
# over src/
[sys.path.remove(x) for x in sys.path[:] if '/kaa_' in x and x.endswith('.egg')]

# And now import it from the source tree.
from distribution.core import Extension, setup

extensions = []

shm_ext = Extension('kaa.base.shmmodule', ['src/extensions/shmmodule.c'])
if not shm_ext.has_python_h():
    print "---------------------------------------------------------------------"
    print "Python headers not found; please install python development package."
    print "kaa.db, shm and inotify support will be unavailable"
    print "---------------------------------------------------------------------"
    time.sleep(2)

else:
    osname = os.popen('uname -s').read().strip().lower()
    if osname == 'darwin':
        print '- kaa.shm not supported on Darwin, not building'
    else:
        extensions.append(shm_ext)

    objectrow_ext = Extension('kaa.base._objectrow', ['src/extensions/objectrow.c'])
    if objectrow_ext.check_library("glib-2.0", "2.4.0"):
        print '+ glib >= 2.4.0 found; building kaa.db'
        extensions.append(objectrow_ext)
    else:
        print "- glib >= 2.4.0 not found; kaa.db will be unavailable"

    utils_ext = Extension('kaa.base._utils', ['src/extensions/utils.c'], config='src/extensions/config.h')
    extensions.append(utils_ext)
    if utils_ext.check_cc(['<sys/prctl.h>'], 'prctl(PR_SET_NAME, "x");'):
        utils_ext.config('#define HAVE_PRCTL')

    if osname == 'linux':
        inotify_ext = Extension("kaa.base.inotify._inotify",
                                ["src/extensions/inotify/inotify.c"],
                                config='src/extensions/inotify/config.h')
        

        if not inotify_ext.check_cc(["<sys/inotify.h>"], "inotify_init();"):
            if not inotify_ext.check_cc(["<sys/syscall.h>"], "syscall(0);"):
                print "- inotify not enabled; are system headers not installed?"
            else:
                print "+ inotify not supported in glibc; no problem, using built-in support instead."
                inotify_ext.config("#define USE_FALLBACK")
                extensions.append(inotify_ext)
        else:
            print "+ inotify supported by glibc; good."
            extensions.append(inotify_ext)

    else:
        print '- Linux-specific features not being built (inotify, set_process_name)'


# call setup
setup(
    module = 'base',
    version = '0.99.0',
    license = 'LGPL',
    url = 'http://doc.freevo.org/api/kaa/base/',
    summary = 'An application framework specializing in asynchronous programming.',
    description  = 'kaa.base is an LGPL-licensed generic application framework, providing the '
                   'foundation for other modules within Kaa, and can be used in any type of project, '
                   'from small event-driven tools, to larger, complex applications.',
    rpminfo = {
        'requires': 'glib2 >= 2.6.0, python-sqlite2 >= 2.3.0, libxml2-python >= 2.6.0',
        'build_requires': 'glib2-devel >= 2.6.0, python-devel >= 2.5.0'
    },
    ext_modules = extensions,
    namespace_packages = ['kaa']
)
