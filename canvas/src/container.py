__all__ = [ 'Container' ]


from object import *
from image import *
from rectangle import *
from text import *
#from canvas import *


class Container(Object):

    def __init__(self):
        self._children = []
        super(Container, self).__init__()
        self["size"] = ("auto", "auto")


    def _canvased(self, canvas):
        super(Container, self)._canvased(canvas)
        for child in self._children:
            child._canvased(canvas)


    def _uncanvased(self):
        super(Container, self)._uncanvased()
        for child in self._children:
            child._uncanvased()


    def _set_property_generic(self, key, value):
        super(Container, self)._set_property_generic(key, value)

        if key not in ("name",):
            #self._queue_children_sync_property(key)
            self._force_sync_property(key)


    def _force_sync_property(self, prop):
        super(Container, self)._force_sync_property(prop)
        for child in self._children:
            child._force_sync_property(prop)
        self._queue_render()


    def _child_property_changed(self, child, prop):
        if prop in ("size",):
            # TODO: be smarter about reflow.
            print "REFLOW CAUSED", self, child, prop
            self._notify_parent_property_changed(prop)
            self._force_sync_property("pos")
            self._force_sync_property("size")
            self._dirty_cached_value("computed_pos")
   

    def _dirty_cached_value(self, prop):
        super(Container, self)._dirty_cached_value(prop)
        for child in self._children:
            child._dirty_cached_value(prop)

    def _sync_properties(self, pre_render = False):
        retval = super(Container, self)._sync_properties(pre_render)
        for child in self._children:
            if child._sync_properties(pre_render):
                retval = True
        return retval


    def _sync_property_clip(self):
        super(Container, self)._sync_property_clip()
        if not self._children:
            # Hide clip object if there are no children (otherwise it will
            # just be rendered as a visible white rectangle.)
            self._clip_object.hide()
        else:
            self._apply_clip_to_children()


    def _can_sync_property(self, property):
        return self.get_canvas() != None

    def _sync_property_pos(self):
        return True

    def _sync_property_color(self):
        return True

    def _sync_property_visible(self):
        return True

    def _sync_property_layer(self):
        return True

    def _sync_property_size(self):
        return True

    def _apply_clip_to_children(self):
        for child in self._children:
            if type(child) == Container:
                child._apply_clip_to_children()
            else:
                child._apply_parent_clip()


    def _reset(self):
        super(Container, self)._reset()
        for child in self._children:
            child._reset()


    def _get_actual_size(self):
        w, h = 0, 0
        for child in self._children:
            pos = child._get_computed_pos()
            size = child._get_actual_size()
            if pos[0] + size[0] > w:
                w = pos[0] + size[0]
            if pos[1] + size[1] > h:
                h = pos[1] + size[1]

        return w, h

    def _get_computed_size(self, child = None):
        if self._parent:
            # Determine the size of our container (ask parent).
            psize = self._parent._get_computed_size(child = self)
        else:
            psize = self["size"]

        size = list(self["size"])
        for index in range(2):
            # If one of our children is asking our size, and a dimension
            # is set to auto, inherit our parent's size.
            if size[index] == "auto" and child:
                size[index] = psize[index]

        size = self._compute_size(psize, size)
        return size


    #
    # Public API
    #

    def add_child(self, child, **kwargs):
        if child._parent:
            raise CanvasError, "Attempt to parent an adopted child."

        if "pos" in kwargs:
            child.move(kwargs["pos"])
        if "visible" in kwargs:
            child.set_visible(kwargs["visible"])
        if "color" in kwargs:
            child.set_color(*kwargs["color"])
        if "name" in kwargs:
            child.set_name(kwargs["name"])
        if "layer" in kwargs:
            child.set_layer(kwargs["layer"])
        if "clip" in kwargs:
            child.clip(*kwargs["clip"])
        if "size" in kwargs and not isinstance(child, Text):
            child.resize(kwargs["size"])
        if ("font" in kwargs or "size" in kwargs) and isinstance(child, Text):
            child.set_font(kwargs.get("font"), kwargs.get("size"))

        self._children.append(child)
        child._adopted(self)
        child._canvased(self.get_canvas())

        if self._clip_object:
            self._clip_object.show()

        return child


    def remove_child(self, child):
        if child not in self._children:
            return False
        self._children.remove(child)
        if child._o:
            child._o.hide()
        # FIXME: shouldn't access _queued_children directly (create an 
        # unqueue method)
        if child._canvas and child in child._canvas._queued_children:
            del child._canvas._queued_children[child]
        child._orphaned()
        if self._clip_object and not self._children:
            # Hide clip object if there are no children (otherwise it will
            # just be rendered as a visible white rectangle.)
            self._clip_object.hide()
        return True


    def kidnap(self, child):
        """
        Forces a child to be added even if it's adopted by another parent.
        """
        if child.get_parent():
            child.get_parent().remove_child(child)
        if child.get_canvas() != self.get_canvas():
            child._uncanvased()
            child._reset()
        self.add_child(child)
     
        
    # Convenience functions for object creation.


    def add_container(self, **kwargs):
        return self.add_child(Container(), **kwargs)

    def add_image(self, image, **kwargs):
        return self.add_child(Image(image), **kwargs)

    def add_text(self, text = None, **kwargs):
        return self.add_child(Text(text), **kwargs)

    def add_rectangle(self, **kwargs):
        return self.add_child(Rectangle(), **kwargs)

