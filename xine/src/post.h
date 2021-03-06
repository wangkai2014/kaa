#ifndef __POST_H_
#define __POST_H_
#include "config.h"

#include <Python.h>
#include <xine.h>
#include <xine/post.h>


#define Xine_Post_PyObject_Check(v) ((v)->ob_type == &Xine_Post_PyObject_Type)

typedef struct {
    PyObject_HEAD

    Xine_PyObject *xine;
    xine_post_t *post;
    int do_dispose;

    PyObject *outputs,  // list of PostOut objects
             *inputs,   // list of PostIn objects
             *name,     // post plugin identifier
             *wrapper;
} Xine_Post_PyObject;

extern PyTypeObject Xine_Post_PyObject_Type;

PyObject *Xine_Post_PyObject__new(PyTypeObject *, PyObject *, PyObject *);
Xine_Post_PyObject *pyxine_new_post_pyobject(Xine_PyObject *, xine_post_t *, char *, int);


#endif
