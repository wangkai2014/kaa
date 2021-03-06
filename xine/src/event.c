#include "xine.h"
#include "event.h"
#include "event_queue.h"
#include "structmember.h"


// Owner must be a EventQueue object
Xine_Event_PyObject *
pyxine_new_event_pyobject(Xine_PyObject *xine, void *owner, xine_event_t *event, int do_dispose)
{
    Xine_Event_PyObject *o;
    PyObject *owner_pyobject;

    o = (Xine_Event_PyObject *)xine_object_to_pyobject_find(event);
    if (o) {
        Py_INCREF(o);
        return o;
    }

    // Verify owner
    owner_pyobject = xine_object_to_pyobject_find(owner);
    if (!owner_pyobject || !Xine_Event_Queue_PyObject_Check(owner_pyobject)) {
        PyErr_Format(xine_error, "Unsupported owner for Event object");
        return NULL;
    }

    o = (Xine_Event_PyObject *)Xine_Event_PyObject__new(&Xine_Event_PyObject_Type, NULL, NULL);
    if (!o)
        return NULL;

    o->event = event;
    o->type = PyInt_FromLong(event->type);
    o->xine = xine;
    o->do_dispose = do_dispose;
    o->owner = owner;
    Py_INCREF(o->xine);
    if (event->data_length == sizeof(int)) {
        // Assume that data is an integer and include that value in the data dict.
        PyDict_SetItemString_STEAL(o->data, "int", PyInt_FromLong(*(int *)event->data));
    }

    // Interpret specific event types.  Python space could use struct.unpack
    // to parse the data, but this is for convenience.
    switch (event->type) {
        case XINE_EVENT_FRAME_FORMAT_CHANGE: {
            xine_format_change_data_t *d = (xine_format_change_data_t *)event->data;
            PyDict_SetItemString_STEAL(o->data, "width", PyInt_FromLong(d->width));
            PyDict_SetItemString_STEAL(o->data, "height", PyInt_FromLong(d->height));
            PyDict_SetItemString_STEAL(o->data, "aspect", PyInt_FromLong(d->aspect));
            PyDict_SetItemString_STEAL(o->data, "pan_scan", PyInt_FromLong(d->pan_scan));
            break;
        }

        case XINE_EVENT_UI_NUM_BUTTONS: {
            xine_ui_data_t *d = (xine_ui_data_t *)event->data;
            PyDict_SetItemString_STEAL(o->data, "num_buttons", PyInt_FromLong(d->num_buttons));
            break;
        }

        case XINE_EVENT_UI_SET_TITLE: {
            xine_ui_data_t *d = (xine_ui_data_t *)event->data;
            PyDict_SetItemString_STEAL(o->data, "str", PyString_FromString(d->str));
            break;
        }

        case XINE_EVENT_UI_MESSAGE: {
            xine_ui_message_data_t *d = (xine_ui_message_data_t *)event->data;
            PyDict_SetItemString_STEAL(o->data, "type", PyInt_FromLong(d->type));
            if (d->explanation)
                PyDict_SetItemString_STEAL(o->data, "explanation", 
                                           PyString_FromString((char *)(event->data + d->explanation)));
            if (d->num_parameters) {
                PyObject *params = PyList_New(0);
                int i;
                char *ptr = event->data + d->parameters;
                for (i = 0; i < d->num_parameters; i++, ptr += strlen(ptr) + 1) {
                    PyObject *str = PyString_FromString(ptr);
                    PyList_Append(params, str);
                    Py_DECREF(str);
                }
                PyDict_SetItemString_STEAL(o->data, "parameters", params);

            }
        }

        case XINE_EVENT_DROPPED_FRAMES: {
            xine_dropped_frames_t *d = (xine_dropped_frames_t *)event->data;
            PyDict_SetItemString_STEAL(o->data, "skipped_frames", PyInt_FromLong(d->skipped_frames));
            PyDict_SetItemString_STEAL(o->data, "skipped_threshold", PyInt_FromLong(d->skipped_threshold));
            PyDict_SetItemString_STEAL(o->data, "discarded_frames", PyInt_FromLong(d->discarded_frames));
            PyDict_SetItemString_STEAL(o->data, "discarded_threshold", PyInt_FromLong(d->discarded_threshold));
            break;
        }

        case XINE_EVENT_MRL_REFERENCE_EXT: {
            xine_mrl_reference_data_ext_t *d = (xine_mrl_reference_data_ext_t*)event->data;
            PyDict_SetItemString_STEAL(o->data, "alternative", PyInt_FromLong(d->alternative));
            PyDict_SetItemString_STEAL(o->data, "start_time", PyInt_FromLong(d->start_time));
            PyDict_SetItemString_STEAL(o->data, "duration", PyInt_FromLong(d->duration));
            PyDict_SetItemString_STEAL(o->data, "mrl", PyString_FromString(d->mrl));
            break;
        }

        case XINE_EVENT_PROGRESS: {
            xine_progress_data_t *d = (xine_progress_data_t *)event->data;
            PyDict_SetItemString_STEAL(o->data, "description", PyString_FromString(d->description));
            PyDict_SetItemString_STEAL(o->data, "percent", PyInt_FromLong(d->percent));
            break;
        }

        default:
            PyDict_SetItemString_STEAL(o->data, "data", 
                                       PyString_FromStringAndSize(event->data, event->data_length));

    }

    xine_object_to_pyobject_register(event, (PyObject *)o);
    return o;
}

PyObject *
Xine_Event_PyObject__new(PyTypeObject *type, PyObject *args, PyObject * kwargs)
{
    Xine_Event_PyObject *self;

    if (args) {
        PyErr_SetString(xine_error, "Don't call me directly");
        return NULL;
    }

    self = (Xine_Event_PyObject *)type->tp_alloc(type, 0);
    self->data = PyDict_New();
    self->wrapper = Py_None;
    Py_INCREF(Py_None);
    return (PyObject *)self;
}

static int
Xine_Event_PyObject__init(Xine_Event_PyObject *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static PyMemberDef Xine_Event_PyObject_members[] = {
    {"data", T_OBJECT_EX, offsetof(Xine_Event_PyObject, data), 0, "Event data"},
    {"type", T_OBJECT_EX, offsetof(Xine_Event_PyObject, type), 0, "Event type"},
    {"wrapper", T_OBJECT_EX, offsetof(Xine_Event_PyObject, wrapper), 0, "Wrapper object"},
    {NULL}
};


void
Xine_Event_PyObject__dealloc(Xine_Event_PyObject *self)
{
    //printf("DEalloc Event: %x\n", self->event);
    if (self->event && self->do_dispose) {
        Py_BEGIN_ALLOW_THREADS
        xine_event_free(self->event);
        Py_END_ALLOW_THREADS
    }
    Py_DECREF(self->wrapper);
    Py_DECREF(self->data);
    Py_DECREF(self->type);
    Py_DECREF(self->xine);
    //Xine_Event_PyObject__clear(self);
    xine_object_to_pyobject_unregister(self->event);
    self->ob_type->tp_free((PyObject*)self);
}

PyObject *
Xine_Event_PyObject_get_owner(Xine_Event_PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *owner = xine_object_to_pyobject_find(self->owner);
    if (!owner)
        owner = Py_None;
    Py_INCREF(owner);
    return owner;
}


PyMethodDef Xine_Event_PyObject_methods[] = {
    {"get_owner", (PyCFunction) Xine_Event_PyObject_get_owner, METH_VARARGS },
    {NULL, NULL}
};

PyTypeObject Xine_Event_PyObject_Type = {
    PyObject_HEAD_INIT(NULL) 
    0,                          /* ob_size */
    "_xine.Event",               /* tp_name */
    sizeof(Xine_Event_PyObject),      /* tp_basicsize */
    0,                          /* tp_itemsize */
    (destructor) Xine_Event_PyObject__dealloc,        /* tp_dealloc */
    0,                          /* tp_print */
    0,                          /* tp_getattr */
    0,                          /* tp_setattr */
    0,                          /* tp_compare */
    0,                          /* tp_repr */
    0,                          /* tp_as_number */
    0,                          /* tp_as_sequence */
    0,                          /* tp_as_mapping */
    0,                          /* tp_hash */
    0,                          /* tp_call */
    0,                          /* tp_str */
    PyObject_GenericGetAttr,    /* tp_getattro */
    PyObject_GenericSetAttr,    /* tp_setattro */
    0,                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "Xine Event Object",       /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Xine_Event_PyObject_methods,     /* tp_methods */
    Xine_Event_PyObject_members,     /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Xine_Event_PyObject__init, /* tp_init */
    0,                         /* tp_alloc */
    Xine_Event_PyObject__new,        /* tp_new */
};


