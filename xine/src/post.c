#include "xine.h"
#include "video_port.h"
#include "audio_port.h"
#include "post.h"
#include "structmember.h"

Xine_Post_PyObject *
pyxine_new_post_pyobject(Xine_PyObject *xine, xine_post_t *post, 
                         PyObject *audio_targets, PyObject *video_targets, 
                         int owner)
{
    Xine_Post_PyObject *o = (Xine_Post_PyObject *)xine_object_to_pyobject_find(post);
    if (o) {
        Py_INCREF(o);
        return o;
    }
    o = (Xine_Post_PyObject *)Xine_Post_PyObject__new(&Xine_Post_PyObject_Type, NULL, NULL);
    if (!o)
        return NULL;
    o->post = post;
    o->xine_pyobject = (PyObject *)xine;
    o->xine = xine->xine;
    o->xine_object_owner = owner;
    Py_INCREF(xine);
    o->audio_targets = audio_targets;
    Py_INCREF(audio_targets);
    o->video_targets = video_targets;
    Py_INCREF(video_targets);
    xine_object_to_pyobject_register(post, (PyObject *)o);
    return o;
}



static int
Xine_Post_PyObject__clear(Xine_Post_PyObject *self)
{
    PyObject *tmp;
    if (self->xine_pyobject) {
        tmp = self->xine_pyobject;
        self->xine_pyobject = 0;
        Py_DECREF(tmp);
    }
    if (self->audio_targets) {
        tmp = self->audio_targets;
        self->audio_targets = 0;
        Py_DECREF(tmp);
    }
    if (self->video_targets) {
        tmp = self->video_targets;
        self->video_targets = 0;
        Py_DECREF(tmp);
    }
    return 0;
}

static int
Xine_Post_PyObject__traverse(Xine_Post_PyObject *self, visitproc visit, void *arg)
{
    int ret;
    if (self->xine_pyobject) {
        ret = visit((PyObject *)self->xine_pyobject, arg);
        if (ret != 0)
            return ret;
    }
    if (self->audio_targets) {
        ret = visit((PyObject *)self->audio_targets, arg);
        if (ret != 0)
            return ret;
    }
    if (self->video_targets) {
        ret = visit((PyObject *)self->video_targets, arg);
        if (ret != 0)
            return ret;
    }
    return 0;
}

PyObject *
Xine_Post_PyObject__new(PyTypeObject *type, PyObject * args, PyObject * kwargs)
{
    Xine_Post_PyObject *self;

    if (args) {
        PyErr_SetString(xine_error, "Don't call me directly");
        return NULL;
    }

    self = (Xine_Post_PyObject *)type->tp_alloc(type, 0);
    self->post = NULL;
    self->xine = NULL;
    self->xine_pyobject = NULL;
    self->wrapper = Py_None;
    Py_INCREF(Py_None);
    return (PyObject *)self;
}

static int
Xine_Post_PyObject__init(Xine_Post_PyObject *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static PyMemberDef Xine_Post_PyObject_members[] = {
    {"wrapper", T_OBJECT_EX, offsetof(Xine_Post_PyObject, wrapper), 0, "Wrapper object"},
    {NULL}
};


void
Xine_Post_PyObject__dealloc(Xine_Post_PyObject *self)
{
    printf("DEalloc Post: %x\n", self->xine);
    if (self->post && self->xine_object_owner) {
        // bug in xine?
        //xine_post_dispose(self->xine, self->post);
    }
    Py_DECREF(self->wrapper);
    Xine_Post_PyObject__clear(self);
    xine_object_to_pyobject_unregister(self->post);
    self->ob_type->tp_free((PyObject*)self);
}

PyObject *
Xine_Post_PyObject_get_audio_inputs(Xine_Post_PyObject *self, PyObject *args, PyObject *kwargs)
{
    Xine_PyObject *xine = (Xine_PyObject *)self->xine_pyobject;
    PyObject *list = PyList_New(0), *o;
    xine_audio_port_t *ao;
    int i;

    for (i = 0; self->post->audio_input[i]; i++) {
        ao = self->post->audio_input[i];
        o = (PyObject *)pyxine_new_audio_port_pyobject(xine, ao, 0);
        PyList_Append(list, o);
        Py_DECREF(o);
    }

    return list;
}

PyObject *
Xine_Post_PyObject_get_video_inputs(Xine_Post_PyObject *self, PyObject *args, PyObject *kwargs)
{
    Xine_PyObject *xine = (Xine_PyObject *)self->xine_pyobject;
    PyObject *list = PyList_New(0), *o;
    xine_video_port_t *vo;
    int i;

    for (i = 0; self->post->video_input[i]; i++) {
        vo = self->post->video_input[i];
        o = (PyObject *)pyxine_new_video_port_pyobject(xine, vo, 0);
        PyList_Append(list, o);
        Py_DECREF(o);
    }

    return list;
}

PyObject *
Xine_Post_PyObject_get_parameters_desc(Xine_Post_PyObject *self, PyObject *args, PyObject *kwargs)
{
    xine_post_in_t *input_api;
    xine_post_api_t *api;
    xine_post_api_descr_t *desc;
    xine_post_api_parameter_t *parm;
    int nparm = 0;
    PyObject *param_dict = PyDict_New();

    input_api = (xine_post_in_t *)xine_post_input(self->post, "parameters");
    if (!input_api) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    api = (xine_post_api_t *)input_api->data;
    desc = api->get_param_descr();
    parm = desc->parameter;

    while (parm->type != POST_PARAM_TYPE_LAST) {
        PyObject *dict = PyDict_New();
        PyObject *type = Py_None;
        switch(parm->type) {
            case POST_PARAM_TYPE_INT:
                type = (PyObject *)&PyInt_Type;
                break;
            case POST_PARAM_TYPE_DOUBLE:
                type = (PyObject *)&PyFloat_Type;
                break;
            case POST_PARAM_TYPE_CHAR:
            case POST_PARAM_TYPE_STRING:
                type = (PyObject *)&PyString_Type;
                break;
            case POST_PARAM_TYPE_STRINGLIST:
                type = (PyObject *)&PyList_Type;
                break;
            case POST_PARAM_TYPE_BOOL:
                type = (PyObject *)&PyBool_Type;
                break;
        }
        Py_INCREF(type);
        PyDict_SetItemString(dict, "type", type);
        PyDict_SetItemString(dict, "name", PyString_FromString(parm->name));
        PyDict_SetItemString(dict, "offset", PyInt_FromLong(parm->offset));
        PyDict_SetItemString(dict, "size", PyInt_FromLong(parm->size));
        PyDict_SetItemString(dict, "readonly", PyBool_FromLong(parm->readonly));

        PyDict_SetItemString(param_dict, parm->name, dict);
        Py_DECREF(dict);
        parm++;
    }

    return param_dict;
}


PyObject *
Xine_Post_PyObject_get_parameters(Xine_Post_PyObject *self, PyObject *args, PyObject *kwargs)
{
    xine_post_in_t *input_api;
    xine_post_api_t *api;
    xine_post_api_descr_t *desc;
    xine_post_api_parameter_t *parm;
    char *data;
    PyObject *dict= PyDict_New();

    input_api = (xine_post_in_t *)xine_post_input(self->post, "parameters");
    if (!input_api) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    api = (xine_post_api_t *)input_api->data;
    desc = api->get_param_descr();
    parm = desc->parameter;
    data = (void *)malloc(desc->struct_size);
    api->get_parameters(self->post, (void *)data);

    while (parm->type != POST_PARAM_TYPE_LAST) {
        PyObject *value = NULL;
        switch(parm->type) {
            case POST_PARAM_TYPE_INT:
                value = PyInt_FromLong(*(int *)(data + parm->offset));
                break;
            case POST_PARAM_TYPE_DOUBLE:
                value = PyFloat_FromDouble(*(double *)(data + parm->offset));
                break;
            case POST_PARAM_TYPE_CHAR:
                value = PyString_FromString((char *)(data + parm->offset));
                break;
            case POST_PARAM_TYPE_STRING:
                value = PyString_FromString(*(char **)(data + parm->offset));
                break;
            case POST_PARAM_TYPE_STRINGLIST:
            {
                int i;
                char **strings = (char **)(data + parm->offset);
                PyObject *str;
                value = PyList_New(0);
                for (i = 0; strings[i]; i++) {
                    str = PyString_FromString(strings[i]);
                    PyList_Append(value, str);
                    Py_DECREF(str);
                }
                break;
            }
            case POST_PARAM_TYPE_BOOL:
                value = PyBool_FromLong(*(int *)(data + parm->offset));
                break;
        }

        if (PyErr_Occurred()) 
            break;

        if (value) {
            PyDict_SetItemString(dict, parm->name, value);
            Py_DECREF(value);
        }
        parm++;
    }

    free(data);
    if (PyErr_Occurred())
        return NULL;

    return dict;
}


PyObject *
Xine_Post_PyObject_set_parameters(Xine_Post_PyObject *self, PyObject *args, PyObject *kwargs)
{
    xine_post_in_t *input_api;
    xine_post_api_t *api;
    xine_post_api_descr_t *desc;
    xine_post_api_parameter_t *parm;
    char *data;
    PyObject *dict;

    if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict))
        return NULL;

    input_api = (xine_post_in_t *)xine_post_input(self->post, "parameters");
    if (!input_api) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    api = (xine_post_api_t *)input_api->data;
    desc = api->get_param_descr();
    parm = desc->parameter;
    data = (void *)malloc(desc->struct_size);
    api->get_parameters(self->post, (void *)data);

    while (parm->type != POST_PARAM_TYPE_LAST) {
        PyObject *value = PyDict_GetItemString(dict, parm->name);
        if (!value) {
            parm++;
            continue;
        }

        switch(parm->type) {
            case POST_PARAM_TYPE_INT:
                *(int *)(data + parm->offset) =  PyLong_AsLong(value);
                break;
            case POST_PARAM_TYPE_DOUBLE:
                *(double *)(data + parm->offset) =  PyFloat_AsDouble(value);
                break;
            case POST_PARAM_TYPE_CHAR:
                strncpy((char *)(data + parm->offset), PyString_AsString(value), parm->size);
                break;
            case POST_PARAM_TYPE_STRING:
            {
                char *tmp;
                tmp = (void *)calloc(1, PySequence_Size(value) + 1);
                strcpy(tmp, PyString_AsString(value));
                *(char **)(data + parm->offset) =  tmp;
                break;
            }
            case POST_PARAM_TYPE_STRINGLIST:
            {
                int i;
                char **strings, *tmp;
                strings = (char **)malloc(PyList_Size(value) + 1);
                for (i = 0; i < PyList_Size(value); i++) {
                    PyObject *o = PyList_GetItem(value, i);
                    tmp = (void *)calloc(1, PySequence_Size(o) + 1);
                    strcpy(tmp, PyString_AsString(o));
                    strings[i] = tmp;
                    Py_DECREF(o);
                }
                strings[i] = NULL;
                *(char **)(data + parm->offset) = (char *)strings;
                break;
            }
            case POST_PARAM_TYPE_BOOL:
                *(int *)(data + parm->offset) =  PyLong_AsLong(value);
                break;
        }
        parm++;
    }

    api->set_parameters(self->post, (void *)data);
    free(data);
    if (PyErr_Occurred())
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

// *INDENT-OFF*
PyMethodDef Xine_Post_PyObject_methods[] = {
    {"get_audio_inputs", (PyCFunction) Xine_Post_PyObject_get_audio_inputs, METH_VARARGS},
    {"get_video_inputs", (PyCFunction) Xine_Post_PyObject_get_video_inputs, METH_VARARGS},
    {"get_parameters_desc", (PyCFunction) Xine_Post_PyObject_get_parameters_desc, METH_VARARGS},
    {"get_parameters", (PyCFunction) Xine_Post_PyObject_get_parameters, METH_VARARGS},
    {"set_parameters", (PyCFunction) Xine_Post_PyObject_set_parameters, METH_VARARGS},

    {NULL, NULL}
};

PyTypeObject Xine_Post_PyObject_Type = {
    PyObject_HEAD_INIT(NULL) 
    0,                          /* ob_size */
    "_xine.Post",               /* tp_name */
    sizeof(Xine_Post_PyObject),      /* tp_basicsize */
    0,                          /* tp_itemsize */
    (destructor) Xine_Post_PyObject__dealloc,        /* tp_dealloc */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /* tp_flags */
    "Xine Post Object",               /* tp_doc */
    (traverseproc)Xine_Post_PyObject__traverse,   /* tp_traverse */
    (inquiry)Xine_Post_PyObject__clear,           /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Xine_Post_PyObject_methods,     /* tp_methods */
    Xine_Post_PyObject_members,     /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Xine_Post_PyObject__init, /* tp_init */
    0,                         /* tp_alloc */
    Xine_Post_PyObject__new,        /* tp_new */
};


