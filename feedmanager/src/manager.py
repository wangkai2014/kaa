# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# manager.py - Manage all feeds
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa.feedmanager - Manage RSS/Atom Feeds
# Copyright (C) 2007-2008 Dirk Meyer
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

# python imports
import os
import logging
from xml.dom import minidom

# kaa imports
import kaa

# fallback RSS parser
import rss

# get logging object
log = logging.getLogger('feedmanager')

# cache file
CACHE = None

# list of all feed objects
_feeds = []

# list of all Feed classes
_generators = []

def register(regexp, generator):
    """
    Register a Feed class.
    """
    _generators.append((regexp, generator))


def _get_feed(url, destdir):
    """
    Get feed class from generators and create the feed object.
    """
    for regexp, generator in _generators:
        if regexp.match(url):
            return generator(url, destdir)
    return rss.Feed(url, destdir)


def add_feed(url, destdir, download=True, num=0, keep=True):
    """
    Add a new feed.
    """
    for c in _feeds:
        if c.dirname == destdir and c.url == url:
            raise RuntimeError('feed already exists')
    feed = _get_feed(url, destdir)
    _feeds.append(feed)
    feed.configure(download, num, keep)
    return feed


def list_feeds():
    """
    Return a list of all feeds.
    """
    return _feeds


def remove_feed(feed):
    """
    Remove a feed.
    """
    _feeds.remove(feed)
    feed.remove()
    save()


def save():
    """
    Save all feed information
    """
    doc = minidom.getDOMImplementation().createDocument(None, "feeds", None)
    top = doc.documentElement
    for c in _feeds:
        node = doc.createElement('feed')
        c._writexml(node)
        top.appendChild(node)
    f = open(CACHE, 'w')
    f.write(doc.toprettyxml())
    f.close()


def init(cachefile):
    """
    Load cached feeds from disc.
    """

    def parse_feed(c):
        for d in c.childNodes:
            if not d.nodeName == 'directory':
                continue
            dirname = kaa.unicode_to_str(d.childNodes[0].data.strip())
            url = kaa.unicode_to_str(c.getAttribute('url'))
            feed = _get_feed(url, dirname)
            feed._readxml(c)
            _feeds.append(feed)
            return

    global CACHE
    CACHE = cachefile

    if not os.path.isfile(CACHE):
        return

    try:
        cache = minidom.parse(CACHE)
    except:
        log.exception('bad cache file: %s' % CACHE)
        return
    if not len(cache.childNodes) == 1 or \
           not cache.childNodes[0].nodeName == 'feeds':
        log.error('bad cache file: %s' % CACHE)
        return

    for c in cache.childNodes[0].childNodes:
        try:
            parse_feed(c)
        except:
            log.exception('bad cache file: %s' % CACHE)
