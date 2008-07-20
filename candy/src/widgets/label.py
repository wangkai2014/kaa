# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# label.py - Label Widget
# -----------------------------------------------------------------------------
# $Id$
#
# This code is much faster than the pango based code
#
# -----------------------------------------------------------------------------
# kaa-candy - Third generation Canvas System using Clutter as backend
# Copyright (C) 2008 Dirk Meyer, Jason Tackaberry
#
# First Version: Dirk Meyer <dischi@freevo.org>
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
import cairo
import re

# kaa.candy imports
from ..core import Color
import core


class Label(core.CairoTexture):
    """
    Text label widget based on cairo.
    """
    candyxml_name = 'label'
    context_sensitive = True

    def __init__(self, pos, size, font, color, text, align='left',
                 context=None):
        """
        Create a new label widget
        @param pos: (x,y) position of the widget or None
        @param size: (width,height) geometry of the widget or None. The height
            parameter is ignored, the widget will always be as height as one line
            of text with the given font.
        @param font: kaa.candy.Font object
        @param text: Text to render. This can also be a context based string like
            C{$text} with the context containing C{text='My String'}. This will
            make the widget context sensitive.
        @param align: Text alignment. One of 'left' (default), 'center' or 'right'
        @param context: the context the widget is created in
        """
        if size[1] is None:
            size = size[0], font.get_height(font.MAX_HEIGHT)
        super(Label, self).__init__(pos, size, context)
        if context:
            def replace_context(matchobj):
                return self.eval_context(matchobj.groups()[0])
            text = re.sub('\$([a-zA-Z_\.]*)', replace_context, text)
        if not isinstance(color, Color):
            color = Color(color)
        self._font = font
        self._color = color
        self._text = text
        self._align = align
        self._render()

    def set_color(self, color):
        """
        Set a new color and re-render the label
        @param color: kaa.candy.Color object
        """
        self._color = color
        self._render()

    def get_color(self):
        """
        Return color object.
        @returns: kaa.candy.Color object
        """
        return self._color

    def _render(self):
        """
        Render the label.
        """
        self.clear()
        # draw new text string
        context = self.cairo_create()
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.set_source_rgba(*self._color.to_cairo())
        context.select_font_face(self._font.name, cairo.FONT_SLANT_NORMAL)
        context.set_font_size(self._font.size)
        x, y, w, h = context.text_extents(self._text)[:4]
        # http://www.tortall.net/mu/wiki/CairoTutorial
        if self._align == 'left':
            x = -x
        if self._align == 'center':
            x = (self.get_property('surface_width') - w) / 2 - x
        if self._align == 'right':
            x = self.get_property('surface_width') - w - x
        if x < 0:
            x = 0
            w = self.get_property('surface_width')
            s = cairo.LinearGradient(0, 0, w, 0)
            c = self._color.to_cairo()
            s.add_color_stop_rgba(0, *c)
            # 50 pixel fading
            s.add_color_stop_rgba(1 - (50.0 / w), *c)
            s.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
            context.set_source(s)
        context.move_to(x, context.font_extents()[0])
        context.show_text(self._text)
        #del context

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the candyxml element for parameter to create the widget. Example::
          <label x='10' y='50' width='100' font='Vera:24' color='0xffffffff'
              text='my string' align='left'/>

        The text can also be a context based variable like C{$text}. This
        will make the widget context sensitive.
        """
        return super(Label, cls).candyxml_parse(element).update(
            font=element.font, color=element.color,
            text=element.content, align=element.align)


# register widget to candyxml
Label.candyxml_register()