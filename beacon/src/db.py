# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# db.py - Beacon database
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: o Mountpoint handling (rom drive mount/umount)
#       o Make it possible to override create_file and create_dir
#       o Support tracks and other non file based items
#
# -----------------------------------------------------------------------------
# kaa-beacon - A virtual filesystem with metadata
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

# python imports
import os
import threading
import logging
import time

# kaa imports
import kaa.notifier
from kaa import db
from kaa.db import *

# get logging object
log = logging.getLogger('beacon')

MAX_BUFFER_CHANGES = 20

# Item generation mapping
from directory import Directory as create_dir
from file import File as create_file

class Mountpoint(object):
    """
    Internal class for mountpoints. More a list of attributes important
    for each mountpoint.
    """


    # TODO: make this object visible to the client and add mount and umount
    # functions to it. But we need different kinds of classes for client
    # and server because the client needs to use ipc for the mounting.

    def __init__(self, device, directory, beacon_dir, db, client):
        self.device = device
        self.directory = directory
        self.name = None
        self.id = None
        self.beacon_dir = beacon_dir
        self.db = db
        self.overlay = ''
        self.url = ''
        self.client = client
        
    def load(self, name):
        """
        Set name of the mountpoint (== load new media)
        """
        if name == self.name:
            return False
        self.name = name
        self.id = None
        self.url = ''
        # get the db id
        if self.name != None:
            media = self.db.query(type="media", name=self.name)
            if media:
                # known, set internal id
                media = media[0]
                self.id = ('media', media['id'])
            elif not self.client:
                # no client == server == write access
                # create media entry and root filesystem
                log.info('create media entry for %s' % self.name)
                media = self.db.add_object("media", name=self.name, content='file')
                self.id = ('media', media['id'])
            if not self.db.query(type='dir', name='', parent=self.id) and \
                   not self.client:
                log.info('create root filesystem for %s' % self.name)
                self.db.add_object("dir", name="", parent=self.id)
            if not self.client:
                self.db.commit()
            if media:
                self.url = media['content'] + '//' + self.directory
            if name:
                self.overlay = os.path.join(self.beacon_dir, name)
                if not os.path.isdir(self.overlay):
                    os.mkdir(self.overlay)
            else:
                self.overlay = ''
        return True


#     def item(self):
#         """
#         Get the id of the mountpoint. This functions needs the database
#         and _must_ be called from the same thread as the db itself.
#         Return the root item for the mountpoint.
#         """
#         if not self.id:
#              return None
#         media = self.db.query(type='media', id=self.id[1])
#         content = media[0]['content']
#         if content == 'file':
#             # a simple data dir
#             current = self.db.query(type="dir", name='', parent=self.id)[0]
#             return item.create(current, None, self)
#         # a track of something else
#         return [ item.create(x, self, self) for x in \
#                  self.db.query(type='track_%s' % content, parent=self.id) ]
#         # TODO: support other media
#         return None

        
    def __repr__(self):
        """
        Convert object to string (usefull for debugging)
        """
        return '<beacon.Mountpoint for %s>' % self.directory


    def __del__(self):
        return 'del', self


class Database(object):
    """
    A kaa.db based database.
    """

    def __init__(self, dbdir, client):
        """
        Init function
        """
        # internal db dir, it contains the real db and the
        # overlay dir for the beacon
        self.dbdir = dbdir

        # remeber client
        # no client == server == write access
        self.client = client
        
        # handle changes in a list and add them to the database
        # on commit.
        self.changes = []

        # internal list of mountpoints
        self._mountpoints = []

        # create db
        if not os.path.isdir(self.dbdir):
            os.makedirs(self.dbdir)
        self._db = db.Database(self.dbdir + '/db')

        # register basic types
        self._db.register_object_type_attrs("dir",
            name = (str, ATTR_KEYWORDS_FILENAME),
            overlay = (bool, ATTR_SIMPLE),
            media = (int, ATTR_SIMPLE),
            mtime = (int, ATTR_SIMPLE))

        self._db.register_object_type_attrs("file",
            name = (str, ATTR_KEYWORDS_FILENAME),
            overlay = (bool, ATTR_SIMPLE),
            media = (int, ATTR_SIMPLE),
            mtime = (int, ATTR_SIMPLE))

        self._db.register_object_type_attrs("media",
            name = (str, ATTR_KEYWORDS),
            title = (unicode, ATTR_KEYWORDS),
            overlay = (bool, ATTR_SIMPLE),
            length = (int, ATTR_SIMPLE),
            content = (str, ATTR_SIMPLE))

        # commit
        self._db.commit()


    def add_mountpoint(self, device, directory):
        """
        Add a mountpoint to the system.
        """
        for mountpoint in self._mountpoints:
            if mountpoint.directory == directory:
                return False
        mountpoint = Mountpoint(device, directory, self.dbdir, self._db,
                                self.client)
        self._mountpoints.append(mountpoint)
        self._mountpoints.sort(lambda x,y: -cmp(x.directory, y.directory))
        return True


    def get_mountpoints(self, return_objects=False):
        """
        Return current list of mountpoints
        """
        if return_objects:
            return self._mountpoints
        return [ (m.device, m.directory, m.name) for m in self._mountpoints ]


    def set_mountpoint(self, directory, name):
        """
        Set name of the mountpoint (load a media)
        """
        for mountpoint in self._mountpoints:
            if mountpoint.directory == directory:
                return mountpoint.load(name)
        else:
            raise AttributeError('unknown mountpoint')


    def _get_dir(self, dirname, media):
        """
        Get database entry for the given directory. Called recursive to
        find the current entry. Do not cache results, they could change.
        """
        if not media:
            # Unknown media and looks like we are read only.
            # Return None, if the media is not known, the dir also won't
            # Note: this should never happen
            log.error('no media set, this should never happen')
            return None
        if dirname == media.directory:
            # we know that '/' is in the db
            current = self._db.query(type="dir", name='', parent=media.id)[0]
            return create_dir(current, media)

        parent = self._get_dir(os.path.dirname(dirname), media)
        name = os.path.basename(dirname)

        if not parent._beacon_id:
            return create_dir(name, parent)
            
        current = self._db.query(type="dir", name=name, parent=parent._beacon_id)
        if not current and self.client:
            return create_dir(name, parent)

        if not current:
            current = self._db.add_object("dir", name=name, parent=parent._beacon_id)
            self._db.commit()
        else:
            current = current[0]
        return create_dir(current, parent)


    def commit(self):
        """
        Commit changes to the database. All changes in the internal list
        are done first.
        """
        if not self.changes:
            return

        log.info('COMMIT')
        t1 = time.time()
        changes = self.changes
        for function, arg1, args, kwargs in self.changes:
            # It could be possible that an item is added twice. But this is no
            # problem because the duplicate will be removed at the
            # next query. It can also happen that a dir is added because of
            # _getdir and because of the parser. We can't avoid that but the
            # db should clean itself up.
            if 'callback' in kwargs:
                callback = kwargs['callback']
                del kwargs['callback']
                callback(function(arg1, *args, **kwargs))
            else:
                function(arg1, *args, **kwargs)
        self._db.commit()
        self.changes = []
        log.info('db.commit took %s seconds' % (time.time() - t1))


    def _delete(self, entry):
        """
        Delete item with the given id from the db and all items with that
        items as parent (and so on). To avoid internal problems, make sure
        commit is called just after this function is called.
        """
        log.debug('DELETE %s' % entry)
        for child in self._db.query(parent = entry._beacon_id):
            self._delete(child)
        self._db.delete_object((entry._beacon_id))


    def _query_dir(self, parent):
        """
        A query to get all files in a directory. The parameter parent is a
        directort object.
        """
        dirname = parent.filename[:-1]
        items = []
        for i in self._db.query(parent = parent._beacon_id):
            if i['type'] == 'dir':
                items.append(create_dir(i, parent))
            else:
                items.append(create_file(i, parent))
        # sort items based on url. The listdir is also sorted, that makes
        # checking much faster
        items.sort(lambda x,y: cmp(x._beacon_name, y._beacon_name))

        # TODO: this could block for cdrom drives and network filesystems. Maybe
        # put the listdir in a thread

        # TODO: use parent mtime to check if an update is needed. Maybe call
        # it scan time or something like that. Also make it an option so the
        # user can turn the feature off.
        pos = -1

        for pos, (f, overlay) in enumerate(parent._beacon_listdir()):
            if pos == len(items):
                # new file at the end
                if os.path.isdir(parent.filename + f):
                    if not overlay:
                        items.append(create_dir(f, parent))
                    continue
                items.append(create_file(f, parent, overlay))
                continue
            while f > items[pos]._beacon_name:
                # file deleted
                i = items[pos]
                items.remove(i)
                if not self.client:
                    # no client == server == write access
                    # delete from database by adding it to the internal changes
                    # list. It will be deleted right before the next commit.
                    self.changes.append((self._delete, i, [], {}))
                # delete
            if f == items[pos]._beacon_name:
                # same file
                continue
            # new file
            if os.path.isdir(parent.filename + f):
                if not overlay:
                    items.insert(pos, create_dir(f, parent))
                continue
            items.insert(pos, create_file(f, parent, overlay))

        if pos + 1 < len(items):
            # deleted files at the end
            if not self.client:
                # no client == server == write access
                for i in items[pos+1-len(items):]:
                    self.changes.append((self._delete, i, [], {}))
            items = items[:pos+1-len(items)]

        if self.changes:
            # need commit because some items were deleted from the db
            self.commit()
        items.sort(lambda x,y: cmp(x.url, y.url))
        return items


    def _query_filename(self, filename):
        """
        Return item for filename, can't be in overlay
        """
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        # find correct mountpoint
        for m in self._mountpoints:
            if dirname.startswith(m.directory):
                break
        parent = self._get_dir(dirname, m)
        if parent._beacon_id:
            # parent is a valid db item, query
            e = self._db.query(parent=parent._beacon_id, name=basename)
            if e:
                # entry is in the db
                basename = e[0]
        if os.path.isdir(filename):
            return create_dir(basename, parent)
        return create_file(basename, parent)


    def _query_id(self, (type, id), cache=None):
        """
        Return item based on (type,id). Use given cache if provided.
        """
        i = self._db.query(type=type, id=id)[0]
        # now we need a parent
        if i['name'] == '':
            # root node found, find correct mountpoint
            for m in self._mountpoints:
                if m.id == i['parent']:
                    break
            else:
                raise AttributeError('bad media %s' % i['parent'])
            return create_dir(i, m)

        # query for parent
        pid = i['parent']
        if cache is not None and pid in cache:
            parent = cache[pid]
        else:
            parent = self._query_id(pid)
            if cache is not None:
                cache[pid] = parent
                
        if i['type'] == 'dir':
            # it is a directory, make a dir item
            return create_dir(i, parent)
        if parent._beacon_isdir:
            # parent is dir, this item is not
            return create_file(i, parent)
        # neither dir nor file, something else
        return create_item(i, parent)


    def _query_parent(self, parent):
        """
        Return all items for the given parent object.
        """
        if parent._beacon_isdir:
            return self._query_dir(parent)
        raise AttributeError('oops, fix me')
    

    def _query_attr(self, query):
        """
        A query to get a list of possible values of one attribute. Special
        keyword 'attr' the query is used for that. This query will not return
        a list of items.
        """
        attr = query['attr']
        del query['attr']

        result = self._db.query_raw(attrs=[attr], distinct=True, **query)[1]
        result = [ x[1] for x in result if x[1] ]

        # sort results and return
        result.sort()
        return result

    
    def query(self, **query):
        """
        Main query function.
        """
        # make sure db is ok
        self.commit()

        # do query based on type
        if 'filename' in query and len(query) == 1:
            return self._query_filename(query['filename'])
        if 'id' in query and len(query) == 1:
            return self._query_id(query['id'])
        if 'parent' in query and len(query) == 1:
            return self._query_parent(query['parent'])
        if 'attr' in query:
            return self._query_attr(query)
            
        # 'raw' query
        result = []
        cache = {}
        for r in self._db.query(**query):

            # get parent
            pid = r['parent']
            if pid in cache:
                parent = cache[pid]
            else:
                parent = self._query_id(pid, cache)
                cache[pid] = parent

            # create item
            if r['type'] == 'dir':
                # it is a directory, make a dir item
                result.append(create_dir(r, parent))
            elif parent._beacon_isdir:
                # parent is dir, this item is not
                result.append(create_file(r, parent))
            else:
                # neither dir nor file, something else
                result.append(create_item(r, parent))

        # sort results and return
        result.sort(lambda x,y: cmp(x.url, y.url))
        return result

#         if 'device' in kwargs:
#             # A query to monitor a media (mountpoint). Special keyword 'media' in
#             # the query is used for that.
#             for m in self._mountpoints:
#                 if m.device == kwargs['device']:
#                     return m
#             raise AttributeError('Unknown device' % kwargs['device'])
#         return self._db.query(*args, **kwargs)



    def add_object(self, type, *args, **kwargs):
        """
        Add an object to the db. If the keyword 'beacon_immediately' is set, the
        object will be added now and the db will be locked until the next commit.
        To avoid locking, do not se the keyword, but this means that a requery on
        the object won't find it before the next commit.
        """
        if 'metadata' in kwargs:
            metadata = kwargs['metadata']
            if metadata:
                for key in self._db._object_types[type][1].keys():
                    if metadata.has_key(key) and metadata[key] != None:
                        kwargs[key] = metadata[key]
            del kwargs['metadata']

        if 'beacon_immediately' in kwargs:
            if len(self.changes):
                self.commit()
            del kwargs['beacon_immediately']
            return self._db.add_object(type, *args, **kwargs)

        self.changes.append((self._db.add_object, type, args, kwargs))
        if len(self.changes) > MAX_BUFFER_CHANGES:
            self.commit()


    def update_object(self, (type, id), *args, **kwargs):
        """
        Update an object to the db. If the keyword 'beacon_immediately' is set, the
        object will be updated now and the db will be locked until the next commit.
        To avoid locking, do not se the keyword, but this means that a requery on
        the object will return the old values.
        """
        if 'metadata' in kwargs:
            metadata = kwargs['metadata']
            if metadata:
                for key in self._db._object_types[type][1].keys():
                    if metadata.has_key(key) and metadata[key] != None:
                        kwargs[key] = metadata[key]
            del kwargs['metadata']

        if 'beacon_immediately' in kwargs:
            if len(self.changes):
                self.commit()
            del kwargs['beacon_immediately']
            return self._db.update_object((type, id), *args, **kwargs)

        self.changes.append((self._db.update_object, (type, id), args, kwargs))
        if len(self.changes) > MAX_BUFFER_CHANGES:
            self.commit()


    def object_types(self):
        """
        Return the list of object types
        """
        return self._db._object_types

        
    def register_object_type_attrs(self, type, *args, **kwargs):
        """
        Register a new object with attributes. Special keywords like name and
        mtime are added by default.
        """
        kwargs['name'] = (str, ATTR_KEYWORDS_FILENAME)
        # TODO: mtime may not e needed for subitems like tracks
        kwargs['overlay'] = (bool, ATTR_SIMPLE)
        kwargs['media'] = (int, ATTR_SIMPLE)
        if not type.startswith('track_'):
            kwargs['mtime'] = (int, ATTR_SIMPLE)
        return self._db.register_object_type_attrs(type, *args, **kwargs)