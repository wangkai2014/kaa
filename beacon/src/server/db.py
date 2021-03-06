# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# db.py - Beacon database
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa.beacon - A virtual filesystem with metadata
# Copyright (C) 2006-2007 Dirk Meyer
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import logging
import time

# kaa imports
import kaa
from kaa import db
from kaa.db import *

# beacon imports
from ..item import Item
from ..db import Database as RO_Database, create_directory

# get logging object
log = logging.getLogger('beacon.db')

MAX_BUFFER_CHANGES = 200

class ReadLock(object):
    """
    Read lock for the database.

    Clients that want to read directly from the database will send a 'db_lock'
    rpc.  The first such client to do so will cause the 'lock' signal to emit,
    which will call commit() on the server, causing sqlite to release the
    exclusive flock on the database so that other processes can read.
    
    At this point, clients may acquire the read lock indefinitely.  The server
    must not attempt to write to the database.

    When the server side wants to write to the database, it will wait until
    the read lock is unlocked by yielding kaa.inprogress(readlock).  (If the
    readlock is not locked, then it will end up yielding a finished InProgress
    which will cause the coroutine to be immediately resumed.)  Once the
    coroutine is resumed, all clients will have relinquished their readlock,
    and db writes may be performed.

    *NB* If the server-side coroutine subsequently yields for any reason, it
    MUST test the read lock before attempting to write again.  Otherwise, a
    client 'db_lock' rpc could be processed before reentering the coroutine,
    and a db write may cause the client to barf in the middle of a db read.
    """
    def __init__(self):
        self.signals = kaa.Signals('locked', 'unlocked')
        self._clients = []
        self._in_progress = None
        # Precreate a finished InProgress object that we can return when
        # not locked.
        self._in_progress_finished = kaa.InProgress().finish(None)


    def __inprogress__(self):
        if self._clients:
            # We are locked.  Create a new InProgress on-demand if necessary.
            if not self._in_progress:
                self._in_progress = kaa.InProgress()
            return self._in_progress
        else:
            return self._in_progress_finished


    def lock(self, client):
        """
        Lock the database for reading.
        """
        self._clients.append(client)
        log.debug('lock++ (%d)', len(self._clients))
        if len(self._clients) == 1:
            self.signals['locked'].emit()


    def unlock(self, client, all=False):
        """
        Unlock the database. If more than one lock was made
        this will only decrease the lock variable but not
        unlock the database.
        """
        while client in self._clients:
            self._clients.remove(client)
            if not all:
                break

        log.debug('lock-- (%d)', len(self._clients))
        if not self._clients:
            if self._in_progress:
                self._in_progress.finish(None)
                self._in_progress = None
            self.signals['unlocked'].emit()


    @property
    def locked(self):
        """
        True if locked.
        """
        return bool(self._clients)



class Database(RO_Database):
    """
    A kaa.db based database.
    """

    __kaasignals__ = {
        'changed':
            '''
            Emitted when the database has been modified.

            .. describe:: def callback(changes)

               :param changes: list of kaa.db ids (2-tuple of (type, id)) for
                               the objects that have been added, removed, or
                               updated in the database.
            '''
    }

    def __init__(self, dbdir):
        """
        Init function
        """
        super(Database,self).__init__(dbdir)

        # handle changes in a list and add them to the database
        # on commit.
        self.changes = []

        # server lock when a client is doing something
        self.read_lock = ReadLock()
        self.read_lock.signals['locked'].connect_weak(self.commit)

        # register basic types
        self._db.register_inverted_index('keywords', min = 2, max = 30)
        self._db.register_object_type_attrs('dir',
            # This multi-column index optimizes queries on (name,parent) which
            # is done for every object add/update, so must be fast. All
            # object types will have this combined index.
            [('name', 'parent_type', 'parent_id')],
            name = (str, ATTR_SEARCHABLE | ATTR_INVERTED_INDEX, 'keywords', db.split_path),
            overlay = (bool, ATTR_SIMPLE),
            media = (int, ATTR_SEARCHABLE | ATTR_INDEXED),
            image = (int, ATTR_SIMPLE),
            mtime = (int, ATTR_SIMPLE))

        self._db.register_object_type_attrs('file',
            [('name', 'parent_type', 'parent_id')],
            name = (str, ATTR_SEARCHABLE | ATTR_INVERTED_INDEX, 'keywords', db.split_path),
            overlay = (bool, ATTR_SIMPLE),
            media = (int, ATTR_SEARCHABLE | ATTR_INDEXED),
            image = (int, ATTR_SIMPLE),
            mtime = (int, ATTR_SIMPLE))

        self._db.register_object_type_attrs('media',
            [('name', 'parent_type', 'parent_id')],
            name = (str, ATTR_SEARCHABLE | ATTR_INVERTED_INDEX, 'keywords', db.split_path),
            content = (str, ATTR_SIMPLE))

        # Commit any schema changes we might have performed above.
        self._db.commit()


    def acquire_read_lock(self):
        return kaa.inprogress(self.read_lock)


    def _query_filename_get_dir_create(self, name, parent):
        """
        Adds a directory to the db.  Called from _query_filename_get_dir in
        the superclass.
        """
        # FIXME: this function will change the database even when
        # the db is locked. I do not see a good way around it and
        # it should not happen often. To make the write lock a very
        # short time we commit just after adding.
        c = self.add_object("dir", name=name, parent=parent)
        if self.read_lock.locked:
            # We just stuffed a client who's reading from the db.  sqlite's
            # locking mechanism should prevent the client from getting garbage
            # data, but will likely result in the client getting blocked.  So
            # commit now so we release the exclusive flock on the db, allowing
            # the client to resume.
            self.commit()

        return create_directory(c, parent)



    # -------------------------------------------------------------------------
    # Database access
    # -------------------------------------------------------------------------

    def commit(self):
        """
        Commit changes to the database. All changes in the internal list
        are done first.
        """
        if not self.changes:
            # nothing to do
            return True

        # db commit
        t1 = time.time()
        self._db.commit()
        t2 = time.time()

        # some time debugging
        log.info('*** db.commit %d items: %.5f' % (len(self.changes), t2-t1))

        # fire db changed signal
        changes = self.changes
        self.changes = []
        self.signals['changed'].emit(changes)


    def sync_item(self, item):
        """
        Sync item with current db information.
        This function is only needed for the parser.
        """
        r = self._db.query(name=item._beacon_data['name'],
                           parent=item._beacon_parent._beacon_id)
        if r:
            item._beacon_database_update(r[0])


    def add_object(self, type, metadata=None, **kwargs):
        """
        Add an object to the db.
        """
        if self.read_lock.locked:
            raise IOError('database is locked')

        if metadata:
            for key in self._db._object_types[type][1].keys():
                if metadata.has_key(key) and metadata[key] != None and \
                       not key in kwargs:
                    kwargs[key] = metadata[key]

        if hasattr(kwargs.get('parent'), '_beacon_id'):
            # fill in parent and media if parent is an Item
            kwargs['media'] = kwargs.get('parent')._beacon_media._beacon_id[1]
            kwargs['parent'] = kwargs.get('parent')._beacon_id

        result = self._db.add(type, **kwargs)
        self.changes.append((result['type'], result['id']))
        if len(self.changes) > MAX_BUFFER_CHANGES:
            self.commit()
        return result


    def update_object(self, (type, id), metadata=None, **kwargs):
        """
        Update an object to the db.
        """
        if self.read_lock.locked:
            raise IOError('database is locked')

        if metadata:
            for key in self._db._object_types[type][1].keys():
                if metadata.has_key(key) and metadata[key] != None and \
                       not key == 'media':
                    kwargs[key] = metadata[key]

        if 'media' in kwargs:
            del kwargs['media']
        try:
            self._db.update((type, id), **kwargs)
        except AssertionError, e:
            log.exception('update (%s,%s)', type, id)
            raise e
        self.changes.append((type, id))
        if len(self.changes) > MAX_BUFFER_CHANGES:
            self.commit()


    def update_object_type(self, obj, new_type):
        """
        Change the type of an object. Returns complete db data
        from the object with the new type.
        """
        if self.read_lock.locked:
            raise IOError('database is locked')

        try:
            return self._db.retype(obj, new_type)
        except ValueError:
            # object doesn't exist, already changed by something?
            pass


    def register_inverted_index(self, name, *args, **kwargs):
        """
        Register a new inverted index with the database.
        """
        return self._db.register_inverted_index(name, *args, **kwargs)


    def register_object_type_attrs(self, type, indexes=[], *args, **kwargs):
        """
        Register a new object with attributes. Special keywords like name and
        mtime are added by default.
        """
        kwargs['name'] = (str, ATTR_SEARCHABLE | ATTR_INVERTED_INDEX, 'keywords', db.split_path)
        # TODO: mtime may not e needed for subitems like tracks
        kwargs['overlay'] = (bool, ATTR_SIMPLE)
        kwargs['media'] = (int, ATTR_SEARCHABLE | ATTR_INDEXED)
        if not type.startswith('track_'):
            kwargs['mtime'] = (int, ATTR_SIMPLE)
            kwargs['image'] = (str, ATTR_SIMPLE)
        if not indexes:
            indexes = [("name", "parent_type", "parent_id")]
        return self._db.register_object_type_attrs(type, indexes, *args, **kwargs)


    def _delete_object_recursive(self, entry):
        """
        Helper function for delete_object.
        """
        log.info('delete %s', entry)
        for child in self._db.query(parent = entry):
            self._delete_object_recursive((child['type'], child['id']))
        # FIXME: if the item has a thumbnail, delete it!
        self._db.delete(entry)
        self.changes.append(entry)


    def delete_object(self, entry):
        """
        Delete an object from the database. entry is either an Item or
        a (type, id) tuple.
        """
        if self.read_lock.locked:
            raise IOError('database is locked')
        if isinstance(entry, Item):
            entry = entry._beacon_id
        if not entry:
            log.error('unable to delete db entry None')
            return True
        self._delete_object_recursive(entry)
        if len(self.changes) > MAX_BUFFER_CHANGES:
            self.commit()


    def delete_media(self, id):
        """
        Delete media with the given id.
        """
        log.info('delete media %s', id)
        for child in self._db.query(media = id):
            entry = (str(child['type']), child['id'])
            # FIXME: if the item has a thumbnail, delete it!
            self._db.delete(entry)
            self.changes.append(entry)
        self._db.delete(('media', id))
        self.changes.append(('media', id))
        self.commit()


    def list_object_types(self):
        """
        Return the list of object type keys
        """
        return self._db._object_types.keys()
