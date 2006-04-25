# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# parser.py - Parser for metadata
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: add more data to the item (cover) and start thumbnailing
#
# -----------------------------------------------------------------------------
# kaa-beacon - A virtual filesystem with metadata
# Copyright (C) 2006 Dirk Meyer
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
from kaa.strutils import str_to_unicode
import kaa.metadata

# get logging object
log = logging.getLogger('beacon.parser')

def parse(db, item, store=False):
    log.debug('check %s', item.url)
    mtime = item._beacon_mtime()
    if not mtime:
        log.warning('no mtime, skip %s' % item)
        return
    parent = item._beacon_parent
    if not parent:
        log.warning('no parent, skip %s' % item)
        return

    if not parent._beacon_id:
        # There is a parent without id, update the parent now. We know that the
        # parent should be in the db, so commit and it should work
        db.commit()
        if not parent._beacon_id:
            # Still not in the database? Well, this should never happen but does
            # when we use some strange softlinks around the filesystem. So in
            # that case we need to scan the parent, too.
            parse(db, parent, True)
        if not parent._beacon_id:
            # This should never happen
            raise AttributeError('parent for %s has no dbid' % item)
    if item._beacon_data['mtime'] == mtime:
        log.debug('up-to-date %s' % item)
        return

    if not item._beacon_id:
        # New file, maybe already added? Do a small check to be sure we don't
        # add the same item to the db again.
        data = db.get_object(item._beacon_data['name'], parent._beacon_id)
        if data:
            item._beacon_database_update(data)
            if item._beacon_data['mtime'] == mtime:
                log.info('up-to-date %s' % item)
                return
            
    log.info('scan %s' % item)
    attributes = { 'mtime': mtime }
    metadata = kaa.metadata.parse(item.filename)
    if metadata and metadata['media'] and \
             db.object_types().has_key(metadata['media']):
        type = metadata['media']
        # XXX: data coming out of kaa.metadata looks like latin-1 encoded 
        # inside a unicode object.  This logic below is taken from mminfo.
        # Why is this needed?  Something looks seriously broken.
        for key in metadata.keys:
            if isinstance(metadata[key], unicode):
                metadata[key] = str_to_unicode(unicode(metadata[key]).encode('latin-1', 'replace'))
    elif item._beacon_isdir:
        type = 'dir'
    else:
        type = 'file'

    if item._beacon_id and type != item._beacon_id[0]:
        # The item changed its type. Adjust the db
        data = db.update_object_type(item._beacon_id, type)
        if not data:
            log.warning('item to change not in the db anymore, try to find it')
            data = db.get_object(item._beacon_data['name'], parent._beacon_id)
        log.info('change item %s to %s' % (item._beacon_id, type))
        item._beacon_database_update(data)


    if type == 'dir':
        for cover in ('cover.jpg', 'cover.png'):
            if os.path.isfile(item.filename + cover):
                attributes['image'] = item.filename + cover
                break
        # TODO: do some more stuff here:
        # Audio directories may hve a different cover if there is only
        # one jpg in a dir of mp3 files or a files with 'front' in the name.
        # They need to be added here as special kind of cover

    else:
        base = os.path.splitext(item.filename)[0]
        for ext in ('.jpg', '.png'):
            if os.path.isfile(base + ext):
                attributes['image'] = base + ext
                break
            if os.path.isfile(item.filename + ext):
                attributes['image'] = item.filename + ext
                break
                
            
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

    if item._beacon_id:
        # Update
        db.update_object(item._beacon_id, **attributes)
        item._beacon_data.update(attributes)
    else:
        # Create. Maybe the object is already in the db. This could happen because
        # of bad timing but should not matter. Only one entry will be there after
        # the next update
        db.add_object(type, name=item._beacon_data['name'], parent=parent._beacon_id,
                      overlay=item._beacon_overlay, callback=item._beacon_database_update,
                      **attributes)
    if store:
        db.commit()
    return True


class Checker(object):
    def __init__(self, notify, db, items, callback):
        self.notify = notify
        self.db = db
        self.items = items
        self.callback = callback

        self.max = len(items)
        self.pos = 0

        self.updated = []
        self.stopped = False
        self.check()


    @execute_in_timer(Timer, 0.01)
    def check(self):
        if self.stopped:
            return False
        
        if self.items:
            self.pos += 1
            item = self.items[0]
            self.items = self.items[1:]
            if item:
                self.notify('progress', self.pos, self.max, item.url)
                parse(self.db, item)
                if item._beacon_id:
                    self.notify('updated', [ (item.url, item._beacon_data) ])
                else:
                    self.updated.append(item)


        if not self.items:
            self.db.commit()
            self.stop()
            self.callback()

            
        updated = []
        while self.updated and self.updated[0] and self.updated[0]._beacon_id:
            updated.append(self.updated.pop(0))
        if updated:
            updated = [ (x.url, x._beacon_data) for x in updated ]
            updated.sort(lambda x,y: cmp(x[0], y[0]))
            self.notify('updated', updated)
            
        if not self.items:
            return False
        return True


    def stop(self):
        self.items = []
        self.stopped = True


    def __del__(self):
        log.info('del parser')
