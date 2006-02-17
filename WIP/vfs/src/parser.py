# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# parser.py - Parser for metadata
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: handle all the FIXME and TODO comments inside this file and
#       add docs for functions, variables and how to use this file
#
# -----------------------------------------------------------------------------
# kaa-vfs - A virtual filesystem with metadata
# Copyright (C) 2005 Dirk Meyer
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file doc/CREDITS for a complete list of authors.
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


# Python imports
import os
import stat
import logging

# kaa imports
from kaa.notifier import Timer, execute_in_timer
import kaa.metadata

# kaa.vfs imports
import util

# get logging object
log = logging.getLogger('vfs')

def parse(db, item, store=False):
    print 'check', item.url
    mtime = item._vfs_mtime()
    if not mtime:
        log.info('oops, no mtime %s' % item)
        return
    parent = item._vfs_parent
    if not parent:
        log.error('no parent %s' % item)
        return

    if not parent._vfs_id:
        # There is a parent without id, update the parent now. We know that the
        # parent should be in the db, so commit and it should work
        db.commit()
        if not parent._vfs_id:
            # this should never happen
            raise AttributeError('parent for %s has no dbid' % item)
    if item._vfs_data['mtime'] == mtime:
        log.debug('up-to-date %s' % item)
        return
    log.info('scan %s' % item)
    attributes = { 'mtime': mtime }
    metadata = kaa.metadata.parse(item.filename)
    if item._vfs_data.has_key('type'):
        type = item._vfs_data['type']
    elif metadata and metadata['media'] and \
             db.object_types().has_key(metadata['media']):
        type = metadata['media']
    elif item._vfs_isdir:
        type = 'dir'
    else:
        type = 'file'

    # add kaa.metadata results, the db module will add everything known
    # to the db.
    attributes['metadata'] = metadata

    # TODO: do some more stuff here:
    # - check metadata for thumbnail or cover (audio) and use kaa.thumb to store it
    # - schedule thumbnail genereation with kaa.thumb
    # - search for covers based on the file (should be done by kaa.metadata)
    # - add subitems like dvd tracks for dvd images on hd

    # Note: the items are not updated yet, the changes are still in
    # the queue and will be added to the db on commit.

    if item._vfs_id:
        # Update
        db.update_object(item._vfs_id, **attributes)
        item._vfs_data.update(attributes)
    else:
        # Create. Maybe the object is already in the db. This could happen because
        # of bad timing but should not matter. Only one entry will be there after
        # the next update
        db.add_object(type, name=item._vfs_data['name'], parent=parent._vfs_id,
                      overlay=item._vfs_overlay, callback=item._vfs_database_update,
                      **attributes)
    if store:
        db.commit()
    return True


class Checker(object):
    def __init__(self, monitor, db, items, notify_checked):
        self.monitor = monitor
        self.db = db
        self.items = items
        self.max = len(items)
        self.pos = 0
        self.updated = []
        self.notify_checked = notify_checked
        self.check()


    @execute_in_timer(Timer, 0.01)
    def check(self):

        if self.items:
            self.pos += 1
            item = self.items[0]
            self.items = self.items[1:]
            if item:
                self.notify('progress', self.pos, self.max, item.url)
                parse(self.db, item)
                if item._vfs_id:
                    self.monitor.send_update([item])
                else:
                    self.updated.append(item)

        if not self.items:
            self.db.commit()
            self.notify('changed')
            if self.notify_checked:
                self.notify('checked')

        updated = []
        while self.updated and self.updated[0] and self.updated[0]._vfs_id:
            updated.append(self.updated.pop(0))
        if updated:
            self.monitor.send_update(updated)

        if not self.items:
            return False
        return True


    def notify(self, *args, **kwargs):
        if self.monitor:
            self.monitor.callback(*args, **kwargs)

#     def __del__(self):
#         print 'del parser'
