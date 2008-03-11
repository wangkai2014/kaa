# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# hal.py - dbus/hal based monitor
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# kaa.beacon.server - A virtual filesystem with metadata
# Copyright (C) 2006-2008 Dirk Meyer
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

__all__ = [ 'signals', 'Device', 'start' ]

import sys
import os
import time
import signal
import logging

import kaa
import kaa.metadata

# check for dbus and it's version
import dbus
if getattr(dbus, 'version', (0,0,0)) < (0,8,0):
    raise ImportError('dbus >= 0.8.0 not found')

# Set dbus to use gtk and adjust kaa to it. Right now python dbus
# only supports the glib mainloop and no generic one.
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
kaa.main.select_notifier('gtk', x11=False)

# kaa.beacon imports
from kaa.beacon.server.config import config
from kaa.beacon.utils import fstab
from cdrom import eject

# get logging object
log = logging.getLogger('beacon.hal')

# HAL signals
signals = kaa.Signals('add', 'remove', 'changed', 'failed')


class Device(object):
    """
    A device object
    """
    def __init__(self, prop, bus):
        self.udi = prop['info.udi']
        self.prop = prop
        self._eject = False
        self._bus = bus

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def mount(self, umount=False):
        """
        Mount or umount the device.
        """
        if self.prop.get('volume.mount_point') and not umount:
            # already mounted
            return False
        for device, mountpoint, type, options in fstab():
            if device == self.prop['block.device'] and \
                   (options.find('users') >= 0 or os.getuid() == 0):
                cmd = ('mount', self.prop['block.device'])
                if umount:
                    cmd = ('umount', self.prop['block.device'])
                break
        else:
            if umount:
                cmd = ("pumount", self.prop.get('volume.mount_point'))
            else:
                cmd = ("pmount-hal", self.udi)
        proc = kaa.Process(cmd)
        proc.signals['stdout'].connect(log.warning)
        proc.signals['stderr'].connect(log.error)
        proc.start()
        return True


    def eject(self):
        """
        Eject the device. This includes umounting and removing from
        the list. Devices that can't be ejected (USB sticks) are only
        umounted and removed from the list.
        """
        if self.prop.get('volume.mount_point'):
            # umount before eject
            self._eject = True
            return self.mount(umount=True)
        # remove from list
        _device_remove(self.udi)
        if self.prop.get('volume.is_disc'):
            eject(self.prop['block.device'])


    def __getattr__(self, attr):
        return getattr(self.prop, attr)


    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------

    def _modified(self, num_changes, change_list):
        """
        Device was modified (mount, umount..)
        """
        for c in change_list:
            if c[0] == 'volume.mount_point':
                obj = self._bus.get_object('org.freedesktop.Hal', self.udi)
                obj = dbus.Interface(obj, 'org.freedesktop.Hal.Device')
                obj.GetAllProperties(reply_handler=self._property_update,
                                     error_handler=log.error)


    def _property_update(self, prop):
        """
        Update internal property list and call signal.
        """
        prop['info.parent'] = self.prop.get('info.parent')
        if not prop.get('volume.mount_point') and self._eject:
            self.prop = prop
            return self.eject()
        signals['changed'].emit(self, prop)
        self.prop = prop



# -----------------------------------------------------------------------------
# Connection handling
# -----------------------------------------------------------------------------

_bus = None
_connection_timeout = 5

def start():
    """
    Connect to DBUS and start to connect to HAL.
    """
    global _bus
    global _connection_timeout
    _connection_timeout -= 1
    try:
        if not _bus:
            _bus = dbus.SystemBus()
    except Exception, e:
        # unable to connect to dbus
        if not _connection_timeout:
            # give up
            signals['failed'].emit('unable to connect to dbus')
            return False
        kaa.OneShotTimer(start).start(2)
        return False
    try:
        obj = _bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
    except Exception, e:
        # unable to connect to hal
        signals['failed'].emit('hal not found on dbus')
        return False
    hal = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')
    hal.GetAllDevices(reply_handler=_device_all, error_handler=log.error)
    hal.connect_to_signal('DeviceAdded', _device_new)
    hal.connect_to_signal('DeviceRemoved', _device_remove)
    return False


# -----------------------------------------------------------------------------
# Device handling
# -----------------------------------------------------------------------------

_devices = []
_blockdevices = {}

def _device_all(device_names):
    """
    HAL callback with the list of all known devices.
    """
    for name in device_names:
        obj = _bus.get_object("org.freedesktop.Hal", str(name))
        obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device",
                             reply_handler=kaa.Callback(_device_add, name),
                             error_handler=log.error)


def _device_new(udi):
    """
    HAL callback for a new device.
    """
    obj = _bus.get_object("org.freedesktop.Hal", udi)
    obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device",
                         reply_handler=kaa.Callback(_device_add, udi, True),
                         error_handler=log.error)


def _device_remove(udi):
    """
    HAL callback when a device is removed.
    """
    if udi in _blockdevices:
        del _blockdevices[udi]
        return True
    for dev in _devices:
        if dev.udi == udi:
            break
    else:
        return True
    # this causes an error later (no such id). Well, there is no disc with
    # that id, but we need to unreg, right? FIXME by reading hal doc.
    sig = _bus.remove_signal_receiver
    sig(dev._modified, "PropertyModified", 'org.freedesktop.Hal.Device',
        "org.freedesktop.Hal", udi)
    _devices.remove(dev)
    # signal changes
    if isinstance(dev.prop.get('info.parent'), dict):
        signals['remove'].emit(dev)


def _device_add(prop, udi, removable=False):
    """
    HAL callback for property list of a new device. If removable is set to
    False this functions tries to detect if it is removable or not.
    """
    if not 'volume.mount_point' in prop:
        if 'linux.sysfs_path' in prop and 'block.device' in prop:
            _blockdevices[udi] = prop
            for dev in _devices:
                if dev.prop.get('info.parent') == udi:
                    dev.prop['info.parent'] = prop
                    signals['add'].emit(dev)
        return

    if prop.get('block.device').startswith('/dev/mapper') or \
           (prop.get('block.device') and config.discs and \
            (prop.get('block.device')[:-1] in config.discs.split(' ') or \
             prop.get('block.device')[:-2] in config.discs.split(' '))):
        # fixed device set in config
        return

    if config.discs:
        # fixed drives are set so this is a removable
        removable = True

    if not prop.get('volume.is_disc') and not removable:
        # No disc and not already marked as removable.
        # Check if the device is removable
        try:
            fd = open(os.path.dirname(prop["linux.sysfs_path"]) + '/removable')
            rm = fd.read(1)
            fd.close()
            if rm != '1':
                # not removable
                return
        except (OSError, KeyError):
            # Error reading info. Either file not found, linux.sysfs_path_device
            # not in prop or no read permissions. So not removable in that case.
            return
    elif prop.get('volume.is_disc') and prop.get('block.device'):
        # Set nice beacon unique id for discs
        try:
            prop['volume.uuid'] = kaa.metadata.cdrom.status(prop.get('block.device'))[1]
        except Exception, e:
            log.exception('device checking')
            return

    dev = Device(prop, _bus)
    _devices.append(dev)
    sig = _bus.add_signal_receiver
    sig(dev._modified, "PropertyModified", 'org.freedesktop.Hal.Device',
        "org.freedesktop.Hal", prop['info.udi'])

    parent = _blockdevices.get(prop.get('info.parent'))
    if parent:
        prop['info.parent'] = parent
        # signal changes
        signals['add'].emit(dev)


if __name__ == '__main__':      
    def new_device(dev):
        print dev.udi
    signals['add'].connect(new_device)
    start()
    kaa.main.run()
